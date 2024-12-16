# scanner.py

import logging
from pathlib import Path
from typing import Generator, Tuple
from metadata_handler import has_yaml_metadata

logging.basicConfig(level=logging.INFO)

class DirectoryScanner:
    def __init__(self, root_directory: Path):
        """
        Initializes the DirectoryScanner with the root directory to scan.
        
        Parameters:
            root_directory (Path): The root directory path.
        """
        self.root_directory = root_directory

    def scan_and_split(self) -> Generator[Tuple[Path, bool], None, None]:
        """
        Scans the directory for markdown files and yields them with a flag indicating whether they have YAML metadata.
        
        Yields:
            Tuple[Path, bool]: A tuple containing the file path and a boolean indicating YAML metadata presence.
        """
        for file_path in self.root_directory.glob('**/*.md'):
            has_yaml = has_yaml_metadata(file_path)
            yield (file_path, has_yaml)
            logging.info(f"File {file_path} has YAML metadata: {has_yaml}")

# Example usage:
# scanner = DirectoryScanner(Path("path/to/directory"))
# for file_path, has_yaml in scanner.scan_and_split():
#     if has_yaml:
#         # Process files with YAML metadata
#     else:
#         # Process files without YAML metadata