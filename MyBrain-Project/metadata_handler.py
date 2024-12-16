# metadata_handler.py

import logging
from pathlib import Path
from typing import Optional
import yaml

def has_yaml_metadata(file_path: Path) -> bool:
    """
    Checks if the provided file contains YAML metadata.
    """
    try:
        with file_path.open("r", encoding="utf-8") as file:
            content = file.read()
            if content.strip().startswith("---"):
                return True
    except Exception as e:
        logging.error(f"Error checking YAML metadata in {file_path}: {e}")
    return False

def extract_metadata(file_path: Path) -> Optional[dict]:
    """
    Extracts YAML metadata from the provided file.
    """
    try:
        with file_path.open("r", encoding="utf-8") as file:
            content = file.read()
            if content.strip().startswith("---"):
                parts = content.split("---", 2)
                yaml_content = parts[1].strip()
                metadata = yaml.safe_load(yaml_content)
                if isinstance(metadata, dict):
                    return metadata
    except yaml.YAMLError as e:
        logging.error(f"YAML parsing error in {file_path}: {e}")
    except Exception as e:
        logging.error(f"Error extracting metadata from {file_path}: {e}")
    return None