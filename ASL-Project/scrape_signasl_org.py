import requests
from bs4 import BeautifulSoup
import os
import json
import logging
from urllib.parse import quote

# Configure logging
log_file_path = r"C:\Users\toddk\Documents\MyCode\ASL-Project\program.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path, mode='a'),  # Append to the log file
        logging.StreamHandler()
    ]
)

# Define the base URL
base_url = "https://www.signasl.org"

# Define the directory to save metadata
save_directory = r"C:\Users\toddk\Documents\MyCode\ASL-Project"
os.makedirs(save_directory, exist_ok=True)

# Path for metadata JSON
metadata_json_path = os.path.join(save_directory, "metadata.json")

# Function to load existing metadata from JSON
def load_existing_metadata(json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    return []

# Function to process a single word and collect metadata
def process_word(word, metadata):
    sanitized_word = word.replace(" ", "-")  # Replace spaces with hyphens
    sign_page_url = f"{base_url}/sign/{quote(sanitized_word)}"
    logging.info(f"Processing word: {word}, URL: {sign_page_url}")

    try:
        response = requests.get(sign_page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <video> tags
        video_tags = soup.find_all('video')
        if video_tags:
            for idx, video_tag in enumerate(video_tags, start=1):
                source_tag = video_tag.find('source')
                if source_tag and 'src' in source_tag.attrs:
                    video_url = source_tag['src']
                    resolution = video_tag.get('width', 'Unknown')  # Extract resolution if available
                    duration = video_tag.get('duration', 'Unknown')  # Extract duration if available
                    metadata.append({
                        "word": word,
                        "video_url": video_url,
                        "resolution": resolution,
                        "duration": duration,
                        "index": idx
                    })
                    logging.info(f"Metadata collected for {word}: {video_url}, Resolution: {resolution}, Duration: {duration}")
        else:
            logging.info(f"No videos found for: {word}")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")

# Function to read all words from a file
def read_all_words(file_path):
    with open(file_path, 'r', encoding='latin-1') as file:
        words = [line.strip().replace('\u00A0', ' ') for line in file if line.strip()]
    logging.info(f"Words read from file (first 10): {words[:10]}")  # Log first 10 words for verification
    return words

# Function to save metadata to JSON
def save_metadata(metadata, json_path):
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(metadata, json_file, indent=4)
    logging.info(f"Metadata saved to {json_path}")

# Function to check if a word is already in the metadata
def is_word_in_metadata(word, metadata):
    return any(entry["word"] == word for entry in metadata)

# Main function to process all words
def scrape_all_words(file_path, metadata_json_path):
    existing_metadata = load_existing_metadata(metadata_json_path)
    words = read_all_words(file_path)
    new_metadata = existing_metadata.copy()

    for word in words:
        if not is_word_in_metadata(word, existing_metadata):
            process_word(word, new_metadata)
        else:
            logging.info(f"Word '{word}' already exists in metadata. Skipping.")

    save_metadata(new_metadata, metadata_json_path)
    logging.info("All words have been processed and metadata saved.")

# Run the script
input_file_path = r"C:\Users\toddk\Documents\The_Oxford_5000_cleaned.txt"
scrape_all_words(input_file_path, metadata_json_path)