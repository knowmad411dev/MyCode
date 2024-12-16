import json
import cv2
import mediapipe as mp
import requests
from urllib.parse import quote
from collections import defaultdict

# Path to the metadata JSON file
metadata_json_path = r"C:\Users\toddk\Documents\MyCode\ASL-Project\metadata.json"

# Path to save the final selected videos JSON file
output_json_path = r"C:\Users\toddk\Documents\MyCode\ASL-Project\best_processed_videos.json"

# Initialize MediaPipe for hand detection, face detection, and pose detection
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose

# Base URL for the ASL website
base_url = "https://www.signasl.org"

# Weighted scoring system
WEIGHTS = {
    "hand_detection_score": 0.5,  # Hands take priority
    "face_detection_score": 0.2,  # Facial expressions are secondary
    "sign_clarity_score": 0.15,   # Sign clarity is important
    "sign_complexity_score": 0.05, # Sign complexity is less important
    "resolution": 0.05,           # Resolution is less important
    "duration": 0.05              # Duration is less important
}

def load_metadata(json_path):
    """Load metadata from the JSON file."""
    with open(json_path, 'r', encoding='utf-8') as json_file:
        metadata = json.load(json_file)
    return metadata

def analyze_video(video_url):
    """Analyze a video to detect hand movements, facial expressions, sign clarity, and complexity."""
    cap = cv2.VideoCapture(video_url)
    hand_detection_score = 0
    face_detection_score = 0
    sign_clarity_score = 0
    sign_complexity_score = 0
    frame_count = 0
    
    with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5) as hands, \
         mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5) as face_mesh, \
         mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            # Convert the frame to grayscale for clarity analysis
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Process the frame with MediaPipe Hands
            hand_results = hands.process(frame)
            if hand_results.multi_hand_landmarks:
                # Check if both hands are detected
                if len(hand_results.multi_hand_landmarks) == 2:
                    hand_detection_score += 1  # Increment score for each frame with both hands detected
                sign_complexity_score += len(hand_results.multi_hand_landmarks)  # Count hand landmarks
            
            # Process the frame with MediaPipe Face Mesh
            face_results = face_mesh.process(frame)
            if face_results.multi_face_landmarks:
                face_detection_score += 1  # Increment score for each frame with detected faces
                sign_complexity_score += len(face_results.multi_face_landmarks[0].landmark)  # Count face landmarks
            
            # Process the frame with MediaPipe Pose
            pose_results = pose.process(frame)
            if pose_results.pose_landmarks:
                sign_complexity_score += len(pose_results.pose_landmarks.landmark)  # Count body landmarks
            
            # Analyze sign clarity using Laplacian variance (measure of sharpness)
            sign_clarity_score += cv2.Laplacian(gray_frame, cv2.CV_64F).var()
    
    cap.release()
    
    # Compute the average scores
    if frame_count > 0:
        hand_detection_score /= frame_count
        face_detection_score /= frame_count
        sign_clarity_score /= frame_count
        sign_complexity_score /= frame_count
    
    return hand_detection_score, face_detection_score, sign_clarity_score, sign_complexity_score

def calculate_video_score(entry):
    """Calculate a combined score for a video based on multiple criteria."""
    # Extract metadata
    hand_detection_score = entry.get("hand_detection_score", 0)
    face_detection_score = entry.get("face_detection_score", 0)
    sign_clarity_score = entry.get("sign_clarity_score", 0)
    sign_complexity_score = entry.get("sign_complexity_score", 0)
    resolution = entry.get("resolution", "0p")
    duration = float(entry.get("duration", 0))
    
    # Normalize resolution (e.g., 1080p = 1.0, 720p = 0.7, 480p = 0.5)
    resolution_score = int(resolution.replace("p", "")) / 1080.0
    
    # Normalize duration (e.g., 5-10 seconds is ideal)
    duration_score = max(0, min((duration - 5) / 5, 1))
    
    # Combine scores using weights
    combined_score = (
        WEIGHTS["hand_detection_score"] * hand_detection_score +
        WEIGHTS["face_detection_score"] * face_detection_score +
        WEIGHTS["sign_clarity_score"] * sign_clarity_score +
        WEIGHTS["sign_complexity_score"] * sign_complexity_score +
        WEIGHTS["resolution"] * resolution_score +
        WEIGHTS["duration"] * duration_score
    )
    
    return combined_score

def process_videos(metadata):
    """Retrieve and process videos for each word in the metadata."""
    word_to_videos = defaultdict(list)
    
    for entry in metadata:
        word = entry["word"]
        video_url = entry["video_url"]
        resolution = entry["resolution"]
        duration = entry["duration"]
        index = entry["index"]
        
        # Analyze the video
        hand_detection_score, face_detection_score, sign_clarity_score, sign_complexity_score = analyze_video(video_url)
        
        # Add the analysis result to the metadata
        entry["hand_detection_score"] = hand_detection_score
        entry["face_detection_score"] = face_detection_score
        entry["sign_clarity_score"] = sign_clarity_score
        entry["sign_complexity_score"] = sign_complexity_score
        word_to_videos[word].append(entry)
    
    # Select the best video for each word
    best_videos = []
    for word, videos in word_to_videos.items():
        # Calculate combined scores for all videos
        for video in videos:
            video["combined_score"] = calculate_video_score(video)
        
        # Select the video with the highest combined score
        best_video = max(videos, key=lambda x: x["combined_score"])
        best_videos.append(best_video)
    
    return best_videos

def save_processed_videos(best_videos, output_path):
    """Save the processed videos to a new JSON file."""
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(best_videos, json_file, indent=4)
    print(f"Best processed videos saved to {output_path}")

def main():
    """Main function to load metadata, retrieve and process videos, and save the results."""
    print("Loading metadata...")
    metadata = load_metadata(metadata_json_path)
    
    print("Processing videos...")
    best_videos = process_videos(metadata)
    
    print("Saving best processed videos...")
    save_processed_videos(best_videos, output_json_path)
    
    print("Video processing completed successfully!")

if __name__ == "__main__":
    main()