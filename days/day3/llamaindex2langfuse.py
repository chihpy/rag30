"""
"""
from dotenv import find_dotenv, load_dotenv
from langfuse import get_client

_ = load_dotenv(find_dotenv())
langfuse = get_client()

# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

# Initialize LlamaIndex instrumentation
LlamaIndexInstrumentor().instrument()

from llama_index.core import Document
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents([Document.example()])

query_engine = index.as_query_engine()

response = query_engine.query("Hello LangFuse!")