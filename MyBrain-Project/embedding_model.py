# embedding_model.py

from sentence_transformers import SentenceTransformer
import logging
import torch
import asyncio

class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = None):
        """
        Initializes the embedding model with lazy loading.
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None  # Lazy loading
        logging.info(f"EmbeddingModel initialized with model '{self.model_name}' on device '{self.device}'.")

    def load_model(self):
        """
        Loads the SentenceTransformer model when needed.
        """
        if self.model is None:
            logging.info("Loading SentenceTransformer model...")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logging.info("Model loaded successfully.")

    async def generate_embedding(self, text: str, metadata: dict) -> list:
        """
        Generates an embedding for the given text and metadata.
        """
        self.load_model()
        metadata_str = ", ".join(f"{k}: {v}" for k, v in metadata.items())
        context = f"Metadata: {metadata_str}. Content: {text}"
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(None, self.model.encode, context)
        return embedding.tolist()