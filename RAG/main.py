

from fastapi import FastAPI
from routes.query import router as query_router

app = FastAPI(title="Eocean API",
               version="1.0.0",
                 description="This is a simple API that uses RAG to answer questions related to eocean. You can ask questions related to eocean and get answers in a surprisingly low cost and fast way.")

app.include_router(query_router)

