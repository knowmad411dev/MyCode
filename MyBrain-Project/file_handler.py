# file_handler.py

import logging
from pathlib import Path

class FileHandler:
    @staticmethod
    def read_file(file_path: Path) -> str:
        """
        Reads the content of a file.

        Parameters:
            file_path (Path): The path to the file to be read.

        Returns:
            str: The content of the file.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            return content
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}. Please check the file path.")
            raise
        except IOError as e:
            logging.error(f"Error reading file {file_path}: {e}. Ensure the file is accessible.")
            raise

    @staticmethod
    def write_file(file_path: Path, content: str) -> None:
        """
        Writes content to a file.

        Parameters:
            file_path (Path): The path to the file to write to.
            content (str): The content to write to the file.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            logging.info(f"Content written successfully to file: {file_path}")
        except IOError as e:
            logging.error(f"Error writing to file {file_path}: {e}. Ensure the file is writable.")
            raise