# file_processor.py

import asyncio
from pathlib import Path
from file_handler import read_file
from metadata_handler import extract_metadata
from chunker import chunk_content_with_metadata
import logging
from vector_store import VectorStore
from llm_client import LLMClient
from embedding_model import EmbeddingModel
from chunk_processor import process_chunk_limited

class DocumentProcessor:
    def __init__(self, config):
        """
        Initializes the DocumentProcessor with necessary components.
        """
        self.config = config
        self.vector_store = VectorStore()
        self.llm_client = LLMClient()
        self.embedding_model = EmbeddingModel()

    async def validate_and_process_file(self, file_path: Path) -> dict:
        """
        Validates and processes a file, generating embeddings and storing them in the vector store.

        Parameters:
            file_path (Path): The path to the file to be processed.

        Returns:
            dict: A dictionary indicating the status of the operation and details.
        """
        try:
            content = read_file(file_path)
            metadata = extract_metadata(file_path)
            chunk_generator = chunk_content_with_metadata(content, metadata, chunk_size=500, overlap=50)
            semaphore = asyncio.Semaphore(5)
            tasks = []
            for chunk_data in chunk_generator:
                task = process_chunk_limited(
                    chunk_data, semaphore, self.llm_client, file_path, len(tasks) + 1, len(chunk_generator)
                )
                tasks.append(task)
            results = await asyncio.gather(*tasks)
            vectors = []
            ids = []
            metadata_list = []
            for result in results:
                if result:
                    vectors.append(result['embedding'])
                    ids.append(f"{file_path.stem}_{result['chunk_num']}")
                    metadata_list.append(result['metadata'])
            self.vector_store.upsert_vectors(vectors, ids, metadata_list)
            return {"status": "success", "file_path": str(file_path)}
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")
            return {"status": "error", "file_path": str(file_path), "error": str(e)}