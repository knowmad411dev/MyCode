# vector_store.py

import pinecone
import logging
from config import Config

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        """
        Initializes the VectorStore with Pinecone configuration.
        """
        self.config = Config.load_default()
        pinecone.init(api_key=self.config.pinecone_api_key, environment=self.config.pinecone_environment)
        self.index = pinecone.Index(self.config.pinecone_index_name)

    def upsert_vectors(self, vectors, ids, metadata_list):
        """
        Upserts vectors with their metadata into the Pinecone index.
        """
        vec_list = list(zip(ids, vectors, metadata_list))
        self.index.upsert(vectors=vec_list, namespace='')
        logging.info(f"Successfully upserted {len(vectors)} vectors")

    async def query_vectors(self, query_vector, top_k=5, namespace=''):
        """
        Queries the Pinecone index for vectors similar to the query vector.
        """
        results = await self.index.query(vector=query_vector, top_k=top_k, namespace=namespace)
        logging.info(f"Successfully queried vectors, found {len(results['matches'])} matches")
        return results