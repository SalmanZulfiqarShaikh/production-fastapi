import os
import time
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
from sentence_transformers import CrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_groq import ChatGroq

load_dotenv()
llm_api_key = os.getenv("GROQ_API_KEY")

router = APIRouter(prefix="/query", tags=["Query"])

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    encode_kwargs={"normalize_embeddings": True},
)

vectorstore = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name="eocean",
    url="http://localhost:6333",
)

# Free local reranker (downloads once, ~1GB). For a lighter one use:
# "cross-encoder/ms-marco-MiniLM-L-6-v2"
reranker = CrossEncoder("BAAI/bge-reranker-base")

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=llm_api_key,
    temperature=0,
)

NOT_FOUND = "NOT_FOUND"

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about Eocean. "
    "Answer using the context below. The answer may be spread across several "
    "context sections, so combine them and be complete (list every item when asked for a list). "
    "Be accurate and concise, and never invent facts. "
    f"Reply with exactly {NOT_FOUND} only if the context contains nothing relevant to the question."
)


class QueryRequest(BaseModel):
    query: str


def expand_query(query: str) -> list[str]:
    """Ask the LLM for alternative phrasings of the question."""
    r = llm.invoke(
        "Rewrite this question 3 different ways to search a company document. "
        "Use different keywords and synonyms. One per line, no numbering, no extra text.\n\n"
        f"{query}"
    )
    extra = [l.strip("-• ").strip() for l in r.content.splitlines() if l.strip()][:3]
    return [query] + extra


def retrieve(queries: list[str], fetch: int, keep: int, original_query: str):
    """Search with each query, merge and dedupe, rerank, return the top `keep`."""
    seen, pool = set(), []
    for q in queries:
        for d in vectorstore.similarity_search(q, k=fetch):
            if d.page_content not in seen:
                seen.add(d.page_content)
                pool.append(d)

    scores = reranker.predict([(original_query, d.page_content) for d in pool])
    ranked = sorted(zip(scores, pool), key=lambda x: x[0], reverse=True)
    return [d for _, d in ranked[:keep]]


def answer_from(query: str, docs) -> str:
    context = "\n\n---\n\n".join(
        f"[Page {d.metadata.get('page_label')}]\n{d.page_content}" for d in docs
    )
    messages = [
        ("system", f"{SYSTEM_PROMPT}\n\nContext:\n{context}"),
        ("human", query),
    ]
    return llm.invoke(messages).content.strip()


def page_list(docs):
    pages = {d.metadata.get("page_label") for d in docs}
    return sorted(pages, key=lambda p: int(p) if str(p).isdigit() else 0)


@router.post("/", summary="Query the eocean knowledge base")
def get_query(body: QueryRequest):
    t0 = time.perf_counter()
    attempt = 1

    # Pass 1: wide retrieval + rerank
    docs = retrieve([body.query], fetch=30, keep=8, original_query=body.query)
    answer = answer_from(body.query, docs)

    # Pass 2: retry wider with query expansion before giving up
    if NOT_FOUND in answer:
        attempt = 2
        docs = retrieve(expand_query(body.query), fetch=30, keep=12, original_query=body.query)
        answer = answer_from(body.query, docs)

    if NOT_FOUND in answer:
        answer = "I don't know. This doesn't appear to be covered in the knowledge base."

    return {
        "query": body.query,
        "answer": answer,
        "sources": page_list(docs),
        "attempts": attempt,
        "total_s": round(time.perf_counter() - t0, 2),
    }