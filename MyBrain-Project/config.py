# config.py

import os
from pathlib import Path

class Config:
    def __init__(self):
        """
        Initializes the configuration settings.
        """
        self.model_name = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
        self.device = os.getenv("DEVICE", "cpu")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.repo_url = os.getenv("REPO_URL", "https://github.com/knowmad411dev/MyBrain")
        self.repo_path = Path(os.getenv("REPO_PATH", "MyBrain"))
        self.allowed_extensions = os.getenv("ALLOWED_EXTENSIONS", ".txt,.md").split(',')
        self.log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(levelname)s - %(message)s")
        self.log_file = os.getenv("LOG_FILE", "app.log")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "document-embeddings")

    @staticmethod
    def load_default():
        """
        Returns a new instance of Config with default or environment-defined settings.
        """
        return Config()

    def validate(self):
        """
        Validates the configuration settings.
        """
        required_attrs = [
            "model_name", "device", "ollama_url", "repo_url", "repo_path", 
            "allowed_extensions", "log_format", "log_file",
            "pinecone_api_key", "pinecone_environment", "pinecone_index_name"
        ]
        for attr in required_attrs:
            if not hasattr(self, attr):
                raise ValueError(f"Missing required configuration: {attr}")
        if not self.pinecone_api_key:
            raise ValueError("Missing PINECONE_API_KEY in environment variables")
        if not self.pinecone_environment:
            raise ValueError("Missing PINECONE_ENVIRONMENT in environment variables")