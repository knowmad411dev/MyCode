# chunker.py

import logging
from typing import Generator, Dict
import re

def validate_chunk_params(content: str, chunk_size: int, overlap: int):
    """
    Validates the parameters for chunking content.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")
    if overlap < 0:
        raise ValueError("overlap must be non-negative.")
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap.")
    if len(content) == 0:
        raise ValueError("Content cannot be empty.")

def extract_code_blocks(content: str) -> list:
    """
    Extracts code blocks enclosed in triple backticks from the content.
    """
    code_pattern = r'```.*?```'
    matches = re.finditer(code_pattern, content, re.DOTALL)
    return [(match.start(), match.end(), match.group()) for match in matches]

def chunk_content_with_metadata(content: str, metadata: dict, chunk_size: int, overlap: int = 0) -> Generator[Dict, None, None]:
    """
    Chunks the content into smaller parts while keeping code blocks intact, providing metadata for each chunk.
    """
    validate_chunk_params(content, chunk_size, overlap)
    code_blocks = extract_code_blocks(content)
    code_blocks.sort(key=lambda x: x[0])
    previous_end = 0

    def chunk_text(text: str, chunk_size: int, overlap: int, metadata: dict) -> Generator[Dict, None, None]:
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size].strip()
            if chunk:
                yield {"chunk": chunk, "type": "text", "metadata": metadata}

    for code_block in code_blocks:
        start, end, code = code_block
        text_before = content[previous_end:start]
        for text_chunk in chunk_text(text_before, chunk_size, overlap, metadata):
            yield text_chunk
        yield {"chunk": code.strip(), "type": "code", "metadata": metadata}
        previous_end = end

    remaining_text = content[previous_end:]
    for text_chunk in chunk_text(remaining_text, chunk_size, overlap, metadata):
        yield text_chunk

    logging.info(f"Generated chunks for file.")