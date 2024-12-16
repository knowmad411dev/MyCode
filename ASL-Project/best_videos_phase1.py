import json
from collections import defaultdict

# Paths to input and output files
metadata_json_path = r"C:\Users\toddk\Documents\MyCode\ASL-Project\metadata.json"
output_json_path = r"C:\Users\toddk\Documents\MyCode\ASL-Project\best_videos.json"

def load_metadata(json_path):
    """Load metadata from the JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as json_file:
            metadata = json.load(json_file)
        return metadata
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading metadata: {e}")
        return []

def filter_videos_by_metadata(metadata, duration_range=(5, 10)):
    """Filter videos based on metadata attributes (e.g., resolution, duration)."""
    filtered_videos = []
    for entry in metadata:
        # Ensure required keys are present
        if not {"word", "video_url", "resolution", "duration"}.issubset(entry):
            print(f"Skipping invalid metadata entry: {entry}")
            continue
        
        word = entry["word"]
        resolution = entry["resolution"]
        duration = entry["duration"]

        try:
            # Filter based on resolution and duration
            if resolution.endswith("p") and duration_range[0] <= float(duration) <= duration_range[1]:
                filtered_videos.append(entry)
        except ValueError:
            print(f"Invalid resolution or duration in entry: {entry}")
            continue

    return filtered_videos

def calculate_video_score(video, duration_range=(5, 10)):
    """Calculate a score for each video based on resolution and duration."""
    try:
        resolution_score = int(video["resolution"].replace("p", "")) / 1080
        duration = float(video["duration"])
        duration_score = 1 if duration_range[0] <= duration <= duration_range[1] else 0
        return resolution_score + duration_score
    except (ValueError, KeyError):
        return 0  # Return a default low score for invalid entries

def select_best_videos(metadata, filtered_videos, duration_range=(5, 10)):
    """Select the best video for each word."""
    word_to_videos = defaultdict(list)

    # Group all videos by word
    for entry in metadata:
        if {"word", "video_url", "resolution", "duration"}.issubset(entry):
            word_to_videos[entry["word"]].append(entry)
        else:
            print(f"Skipping invalid metadata entry: {entry}")

    best_videos = []
    for word, videos in word_to_videos.items():
        # Filtered videos for the word
        filtered_for_word = [v for v in filtered_videos if v["word"] == word]
        
        if filtered_for_word:
            # Select the best from filtered videos
            best_video = max(filtered_for_word, key=lambda v: calculate_video_score(v, duration_range))
        else:
            # Select the best from all videos for the word
            best_video = max(videos, key=lambda v: calculate_video_score(v, duration_range))
        
        best_videos.append(best_video)

    return best_videos

def save_selected_videos(best_videos, output_path):
    """Save the selected videos to a new JSON file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(best_videos, json_file, indent=4)
        print(f"Selected videos saved to {output_path}")
    except IOError as e:
        print(f"Error saving selected videos: {e}")

def main():
    """Main function to load metadata, filter, select, and save the best videos."""
    print("Loading metadata...")
    metadata = load_metadata(metadata_json_path)
    if not metadata:
        return
    
    print("Filtering videos based on metadata...")
    filtered_videos = filter_videos_by_metadata(metadata)
    
    print("Selecting the best video for each word...")
    best_videos = select_best_videos(metadata, filtered_videos)
    
    print("Saving selected videos...")
    save_selected_videos(best_videos, output_json_path)
    
    print("Best videos selection completed successfully!")

if __name__ == "__main__":
    main()
