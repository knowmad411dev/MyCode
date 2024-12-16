# main.py

import asyncio
from pathlib import Path
from file_processor import DocumentProcessor
from config import Config
from scanner import DirectoryScanner
from utils import setup_logging

async def main():
    config = Config.load_default()
    config.validate()
    setup_logging(config.log_level, config.log_format, config.log_file)
    document_processor = DocumentProcessor(config)
    scanner = DirectoryScanner(Path("path/to/directory"))
    files_to_process = scanner.scan_and_split()
    for file in files_to_process:
        result = await document_processor.validate_and_process_file(file)
        print(result)

if __name__ == "__main__":
    asyncio.run(main())