import asyncio
import logging
from typing import Optional, Dict

async def process_chunk_limited(
    chunk_data: Dict,
    semaphore: asyncio.Semaphore,
    llm_client,
    file_path: str,
    chunk_num: int,
    total_chunks: int,
    timeout: int = 10  # Timeout in seconds
) -> Optional[Dict]:
    """
    Process a single chunk of content with metadata, concurrency limit, and timeout.

    Args:
        chunk_data (Dict): Contains chunk content, type (text/code), and metadata.
        semaphore (asyncio.Semaphore): Semaphore to limit concurrency.
        llm_client: The LLM client for processing.
        file_path (str): Path to the file being processed.
        chunk_num (int): The current chunk number.
        total_chunks (int): Total number of chunks.
        timeout (int): Maximum time to wait for LLM response.

    Returns:
        Optional[Dict]: Processed result including embeddings or None if it fails.

    Logs:
        - Info: When chunk processing starts and completes.
        - Error: If chunk processing fails.
    """
    async with semaphore:
        logging.info(f"Processing chunk {chunk_num}/{total_chunks} for file: {file_path}")
        try:
            chunk = chunk_data["chunk"]
            metadata = chunk_data["metadata"]
            chunk_type = chunk_data["type"]

            # Add chunk type to metadata
            metadata["chunk_type"] = chunk_type

            # Wrap the LLM call in a timeout
            response = await asyncio.wait_for(llm_client.generate_embedding(chunk, metadata), timeout=timeout)
            logging.info(f"Successfully processed chunk {chunk_num}/{total_chunks} for file: {file_path}")
            return {"chunk_num": chunk_num, "embedding": response, "metadata": metadata}
        except asyncio.TimeoutError:
            logging.error(f"Timeout processing chunk {chunk_num}/{total_chunks} for file: {file_path}")
            return None
        except Exception as e:
            logging.error(f"Error processing chunk {chunk_num}/{total_chunks} for file: {file_path} - {e}")
            return None