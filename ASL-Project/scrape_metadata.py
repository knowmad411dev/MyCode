# scrape_metadata.py
import os
import json
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import quote

def load_existing_metadata(json_path):
    """
    Loads existing metadata from a JSON file.
    Args:
        json_path (str): Path to the JSON file.
    Returns:
        list: List of metadata entries.
    """
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    return []

def process_word(word, metadata):
    """
    Processes a single word and collects metadata.
    Args:
        word (str): The word to process.
        metadata (list): List to store metadata.
    """
    sanitized_word = word.replace(" ", "-")
    sign_page_url = f"https://www.signasl.org/sign/{quote(sanitized_word)}"
    logging.info(f"Processing word: {word}, URL: {sign_page_url}")

    try:
        response = requests.get(sign_page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        video_tags = soup.find_all('video')
        for idx, video_tag in enumerate(video_tags, start=1):
            source_tag = video_tag.find('source')
            if source_tag and 'src' in source_tag.attrs:
                video_url = source_tag['src']
                resolution = video_tag.get('width', 'Unknown')
                duration = video_tag.get('duration', 'Unknown')
                metadata.append({
                    "word": word,
                    "video_url": video_url,
                    "resolution": resolution,
                    "duration": duration,
                    "index": idx
                })
                logging.info(f"Collected metadata for {word}: {video_url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error processing word {word}: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    word_file_path = "/content/drive/MyDrive/word_list.txt"
    metadata_json_path = "/content/drive/MyDrive/metadata.json"
    metadata = load_existing_metadata(metadata_json_path)

    with open(word_file_path, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f]

    for word in words:
        if not any(entry.get("word") == word for entry in metadata):
            process_word(word, metadata)

    with open(metadata_json_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4)
