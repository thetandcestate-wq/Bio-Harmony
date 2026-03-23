import cv2
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

# 1. Data Acquisition: Extracting the Optical Resonance
def extract_optical_signal(video_path):
    print("Extracting optical data from video...")
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    red_signal = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # OpenCV reads images in BGR (Blue, Green, Red) format. 
        # We isolate the Red channel (index 2) as it penetrates tissue best.
        avg_red = np.mean(frame[:, :, 2])
        red_signal.append(avg_red)
        
    cap.release()
    return np.array(red_signal), fps

# 2. Signal Processing Layer: The Bandpass Filter
def clean_biological_noise(data, lowcut, highcut, fs, order=4):
    # This filter isolates frequencies strictly within the human biological range.
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    
    # Butterworth bandpass filter configuration
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

# 3. The Unification Engine: Baseline Calculation
def establish_baseline(video_path):
    # Extract raw data
    raw_signal, fps = extract_optical_signal(video_path)
    
    if len(raw_signal) == 0:
        print("Error: Could not read video data.")
        return
        
    # Apply filter: Human heart rate falls between 0.8 Hz (48 BPM) and 3.0 Hz (180 BPM)
    filtered_signal = clean_biological_noise(raw_signal, 0.8, 3.0, fps)
    
    # Detect the acoustic/kinetic peaks translated into the optical data
    # distance=fps/2.5 ensures we don't count double-beats
    peaks, _ = find_peaks(filtered_signal, distance=fps/2.5) 
    
    if len(peaks) < 2:
        print("Not enough biological data detected. Ensure the flash was fully covered.")
        return
        
    # Calculate the exact beat-to-beat intervals (HRV baseline)
    beat_intervals = np.diff(peaks) / fps
    average_heart_rate = 60.0 / np.mean(beat_intervals)
    
    print("\n--- Bio-Harmony Baseline Established ---")
    print(f"Total Frames Analyzed: {len(raw_signal)}")
    print(f"Detected Heartbeats: {len(peaks)}")
    print(f"Baseline Rhythm: {average_heart_rate:.2f} BPM")
    
    return average_heart_rate, filtered_signal

# Execution Block
if __name__ == "__main__":
    # Transfer your 60-second video to the same folder as this script 
    # and update the filename below.
    video_file = "my_chest_video.mp4" 
    establish_baseline(video_file)
