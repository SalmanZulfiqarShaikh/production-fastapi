from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

pdf_path = Path(__file__).parent.parent / "source" / "eocean.pdf"

# Load and split
loader = PyPDFLoader(str(pdf_path))
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=400,
)
splits = text_splitter.split_documents(documents)

# Free local embedding model 
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    encode_kwargs={"normalize_embeddings": True},
)

dim = len(embeddings.embed_query("test"))
print(dim)  # 384 for bge-small
# Store in Qdrant
vectorstore = QdrantVectorStore.from_documents(
    documents=splits,
    embedding=embeddings,          
    collection_name="eocean",
    url="http://localhost:6333",
)