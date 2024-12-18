# main.py
import os
import logging
from scrape_metadata import load_existing_metadata
from process_video import stream_video_from_url, plot_results

def filter_videos(metadata):
    """
    Filter and select videos with valid criteria.
    Args:
        metadata (list): List of metadata entries.
    Returns:
        list: Filtered metadata entries.
    """
    filtered_videos = [entry for entry in metadata if entry.get("resolution", "").endswith("p")]
    logging.info(f"Filtered {len(filtered_videos)} videos with valid criteria.")
    return filtered_videos

def main():
    """Main entry point for the program."""
    logging.info("Starting main program.")

    metadata_json_path = os.path.join("/content/drive/MyDrive", "metadata.json")
    metadata = load_existing_metadata(metadata_json_path)

    if not metadata:
        logging.error("No metadata available.")
        return

    logging.info("Filtering videos...")
    filtered_videos = filter_videos(metadata)

    if filtered_videos:
        logging.info(f"Processing {len(filtered_videos)} videos...")
        for video in filtered_videos[:10]:  # Example: Process the first 10 videos
            video_url = video.get("video_url")
            t, x, y, z = stream_video_from_url(video_url)
            if t is not None:
                plot_results(t, x, y, z)
    else:
        logging.warning("No videos matched the filter criteria.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    main()