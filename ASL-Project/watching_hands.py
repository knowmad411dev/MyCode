# Required Libraries Installation (Place in Colab's first cell)
# !pip install numpy matplotlib scipy opencv-python-headless mediapipe gdown

# GPU Availability Check
import tensorflow as tf
if tf.config.list_physical_devices('GPU'):
    print("GPU is available.")
else:
    print("GPU is not available. Please ensure you have selected a GPU runtime in Colab.")

# Import Libraries
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import cv2
import mediapipe as mp
import os

# Download Video File from Google Drive
def download_video_from_drive(file_url, output_path='video.mp4'):
    """
    Downloads an MP4 video from a Google Drive link using gdown.
    Args:
        file_url (str): The Google Drive URL for the file.
        output_path (str): The output path for the downloaded file.
    """
    from google.colab import drive
    drive.mount('/content/drive')

    # Extract the file ID from the URL
    file_id = file_url.split('/d/')[1].split('/')[0]
    gdown_command = f"https://drive.google.com/uc?id={file_id}"
    !gdown $gdown_command -O $output_path
    print(f"Downloaded video to {output_path}")

# MediaPipe Hands Initialization
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    model_complexity=1
)

# Video Processing Function
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Cannot open video: {video_path}")
        return None, None, None, None

    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / frame_rate
    t = []
    x_positions = []
    y_positions = []
    z_positions = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        t.append(frame_count / frame_rate / duration)
        frame_count += 1

        # Convert BGR to RGB and process for hands
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
                y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                z = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].z
                x_positions.append(x)
                y_positions.append(y)
                z_positions.append(z)
                break
        else:
            x_positions.append(np.nan)
            y_positions.append(np.nan)
            z_positions.append(np.nan)
    cap.release()
    return t, x_positions, y_positions, z_positions

# Main Execution
def main():
    # Video file URL (replace with your Google Drive link if different)
    file_url = 'https://drive.google.com/file/d/1C2SJFZprwZ80YLfRIi2iY2gCtXnD-SUO/view?usp=drive_link'
    video_path = 'video.mp4'

    # Download the video
    download_video_from_drive(file_url, video_path)

    # Process the video
    t, x, y, z = process_video(video_path)
    if t is None:
        return

    # Clean and interpolate data
    t_clean = np.array(t)
    x_clean = np.array(x)
    y_clean = np.array(y)
    z_clean = np.array(z)

    # Interpolation
    if (
        np.sum(np.isfinite(x_clean)) > 0 and
        np.sum(np.isfinite(y_clean)) > 0 and
        np.sum(np.isfinite(z_clean)) > 0
    ):
        x_clean = np.interp(
            t_clean,
            t_clean[np.isfinite(x_clean)],
            x_clean[np.isfinite(x_clean)]
        )
        y_clean = np.interp(
            t_clean,
            t_clean[np.isfinite(y_clean)],
            y_clean[np.isfinite(y_clean)]
        )
        z_clean = np.interp(
            t_clean,
            t_clean[np.isfinite(z_clean)],
            z_clean[np.isfinite(z_clean)]
        )

        # Sorting
        sorted_indices = np.argsort(t_clean)
        t_clean = t_clean[sorted_indices]
        x_clean = x_clean[sorted_indices]
        y_clean = y_clean[sorted_indices]
        z_clean = z_clean[sorted_indices]

        # Plot results
        spline_x = UnivariateSpline(t_clean, x_clean, k=3, s=0)
        spline_y = UnivariateSpline(t_clean, y_clean, k=3, s=0)
        spline_z = UnivariateSpline(t_clean, z_clean, k=3, s=0)

        t_fit = np.linspace(t_clean.min(), t_clean.max(), 100)
        x_fit = spline_x(t_fit)
        y_fit = spline_y(t_fit)
        z_fit = spline_z(t_fit)

        plt.figure(figsize=(12, 8))
        plt.subplot(3, 1, 1)
        plt.plot(t_clean, x_clean, 'o', label='Data')
        plt.plot(t_fit, x_fit, '-', label='Spline')
        plt.title('X Coordinate')
        plt.legend()

        plt.subplot(3, 1, 2)
        plt.plot(t_clean, y_clean, 'o', label='Data')
        plt.plot(t_fit, y_fit, '-', label='Spline')
        plt.title('Y Coordinate')
        plt.legend()

        plt.subplot(3, 1, 3)
        plt.plot(t_clean, z_clean, 'o', label='Data')
        plt.plot(t_fit, z_fit, '-', label='Spline')
        plt.title('Z Coordinate')
        plt.legend()

        plt.tight_layout()
        plt.show()
    else:
        print("No valid data points for interpolation.")

if __name__ == "__main__":
    main()
