# process_video.py
import cv2
import numpy as np
import mediapipe as mp
import requests
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    model_complexity=1
)

def stream_video_from_url(video_url):
    """
    Streams video data from a URL and processes frames using GPU when available.
    Args:
        video_url (str): URL of the video to process.
    Returns:
        tuple: Time, x, y, z positions of the hand landmarks.
    """
    response = requests.get(video_url, stream=True)
    if response.status_code != 200:
        print(f"Failed to stream video from {video_url}")
        return None, None, None, None

    # Use OpenCV to process the video stream
    video_data = np.asarray(bytearray(response.content), dtype=np.uint8)
    video_array = cv2.imdecode(video_data, cv2.IMREAD_COLOR)

    # Convert video array to GPU-compatible format (if supported)
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        gpu_frame = cv2.cuda_GpuMat()
        gpu_frame.upload(video_array)
        cap = cv2.cuda.createVideoReader(gpu_frame)
    else:
        cap = cv2.VideoCapture(video_array)

    if not cap.isOpened():
        print("Cannot open video stream.")
        return None, None, None, None

    t, x_positions, y_positions, z_positions = [], [], [], []
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / frame_rate
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Use GPU for frame conversion to RGB (if available)
        if cv2.cuda.getCudaEnabledDeviceCount() > 0:
            gpu_frame.upload(frame)
            frame = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2RGB).download()
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        t.append(frame_count / frame_rate / duration)
        frame_count += 1

        # Detect landmarks
        results = hands.process(frame)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
                y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                z = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].z
                x_positions.append(x)
                y_positions.append(y)
                z_positions.append(z)
        else:
            x_positions.append(np.nan)
            y_positions.append(np.nan)
            z_positions.append(np.nan)

    cap.release()
    return t, x_positions, y_positions, z_positions

def plot_results(t, x, y, z):
    """
    Plots the results of the hand landmark positions.
    Args:
        t (list): Time points.
        x (list): X positions.
        y (list): Y positions.
        z (list): Z positions.
    """
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
        plt.plot(t_fit, x_fit, label="X Position")
        plt.legend()

        plt.subplot(3, 1, 2)
        plt.plot(t_fit, y_fit, label="Y Position")
        plt.legend()

        plt.subplot(3, 1, 3)
        plt.plot(t_fit, z_fit, label="Z Position")
        plt.legend()

        plt.tight_layout()
        plt.show()
