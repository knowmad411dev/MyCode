# search.py

from vector_store import VectorStore
from embedding_model import EmbeddingModel

async def search_documents(query: str, top_k: int = 5):
    """
    Searches for documents based on a query using vector similarity.
    """
    vector_store = VectorStore()
    embedding_model = EmbeddingModel()
    query_embedding = await embedding_model.generate_embedding(query, {})
    results = await vector_store.query_vectors(query_embedding, top_k=top_k)
    return results['matches']