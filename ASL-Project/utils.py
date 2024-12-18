# utils.py
import json

def load_vectors(json_path):
    """
    Loads vectors from a JSON file.
    Args:
        json_path (str): Path to the JSON file.
    Returns:
        dict: Dictionary of vectors.
    """
    with open(json_path, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)
