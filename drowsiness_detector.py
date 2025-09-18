# Drowsiness Detection System using MediaPipe
# Based on Adrian Rosebrock's project, adapted for MediaPipe
# Modified to use external audio file as alarm

import os

# import necessary packages
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from threading import Thread
import numpy as np
import imutils
import time
import mediapipe as mp
import cv2
import matplotlib.pyplot as plt

# define constants
WEBCAM = 0 # webcam index (0 for default webcam)
EYE_THRESHOLD = 0.68 # Eye aspect ratio (EAR) threshold
NUM_CONSECUTIVE_FRAMES = 100 # Number of consecutive frames to trigger alarm
COUNTER = 0 # Consecutive frames counter
ALARM_ON = False # Alarm state
ALARM_THREAD = None # Alarm thread

# AUDIO FILE CONFIGURATION
# Put the path to your audio file here
ALARM_FILE = "G:/Guilherme/Sigmoidal/Masterclass Visao/sonolencia/buzina.wav"  # Example: "C:/Users/your_user/Desktop/alarm.wav"
# Supported formats: .wav, .mp3, .ogg, .flac (depending on available library)

# Variable to control which audio library to use
AUDIO_LIBRARY = None

# Eye landmark indices in MediaPipe Face Mesh
# Left eye (from person's perspective)
LEFT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
# Right eye (from person's perspective)
RIGHT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]

# Specific points for EAR (Eye Aspect Ratio) calculation
# Format: [outer corner, top, inner corner, bottom, top, bottom]
LEFT_EYE_EAR_POINTS = [33, 159, 133, 145, 158, 153]  # left
RIGHT_EYE_EAR_POINTS = [362, 385, 263, 374, 386, 380]  # right


def check_audio_library():
    """
    Check which audio library is available and test the file
    
    :return: string indicating available library or None
    """
    global AUDIO_LIBRARY
    
    # Check if file exists
    if not os.path.exists(ALARM_FILE):
        print(f"[WARNING] Audio file not found: {ALARM_FILE}")
        print("[INFO] Using system alarm as fallback")
        return None
    
    # Try pygame (best option - multiplatform)
    try:
        import pygame
        pygame.mixer.init()
        # Test if it can load the file
        pygame.mixer.Sound(ALARM_FILE)
        AUDIO_LIBRARY = "pygame"
        print(f"[INFO] Using pygame to play: {ALARM_FILE}")
        return "pygame"
    except ImportError:
        print("[INFO] pygame not found")
    except Exception as e:
        print(f"[WARNING] Error loading file with pygame: {e}")
    
    # Try playsound (simple but effective)
    try:
        import playsound
        # Test playback (silent, just to check if it works)
        AUDIO_LIBRARY = "playsound"
        print(f"[INFO] Using playsound to play: {ALARM_FILE}")
        return "playsound"
    except ImportError:
        print("[INFO] playsound not found")
    except Exception as e:
        print(f"[WARNING] Error testing playsound: {e}")
    
    # Try pydub + simpleaudio
    try:
        from pydub import AudioSegment
        from pydub.playback import play
        # Test if it can load the file
        AudioSegment.from_file(ALARM_FILE)
        AUDIO_LIBRARY = "pydub"
        print(f"[INFO] Using pydub to play: {ALARM_FILE}")
        return "pydub"
    except ImportError:
        print("[INFO] pydub not found")
    except Exception as e:
        print(f"[WARNING] Error loading file with pydub: {e}")
    
    # Try winsound (Windows only, for .wav files)
    try:
        import winsound
        import platform
        if platform.system() == "Windows" and ALARM_FILE.lower().endswith('.wav'):
            AUDIO_LIBRARY = "winsound"
            print(f"[INFO] Using winsound to play: {ALARM_FILE}")
            return "winsound"
    except ImportError:
        pass
    except Exception as e:
        print(f"[WARNING] Error testing winsound: {e}")
    
    print("[WARNING] No compatible audio library found")
    print("[INFO] Using system alarm as fallback")
    return None


def play_audio_file():
    """
    Play audio file using available library
    
    :return: True if successful, False otherwise
    """
    try:
        if AUDIO_LIBRARY == "pygame":
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            sound = pygame.mixer.Sound(ALARM_FILE)
            sound.play()
            # Wait for sound to finish or until interrupted
            while pygame.mixer.get_busy() and ALARM_ON:
                time.sleep(0.1)
            return True
            
        elif AUDIO_LIBRARY == "playsound":
            import playsound
            playsound.playsound(ALARM_FILE, block=False)
            time.sleep(1)  # Small pause between reproductions
            return True
            
        elif AUDIO_LIBRARY == "pydub":
            from pydub import AudioSegment
            from pydub.playback import play
            audio = AudioSegment.from_file(ALARM_FILE)
            play(audio)
            return True
            
        elif AUDIO_LIBRARY == "winsound":
            import winsound
            winsound.PlaySound(ALARM_FILE, winsound.SND_FILENAME | winsound.SND_ASYNC)
            time.sleep(1)
            return True
            
    except Exception as e:
        print(f"[ERROR] Failed to play audio: {e}")
    
    return False


def trigger_continuous_alarm():
    """
    Trigger continuous sound alarm using external file or system alarm
    
    :return: None
    """
    global ALARM_ON
    
    while ALARM_ON:
        # Try to play audio file first
        if AUDIO_LIBRARY and play_audio_file():
            # If managed to play file, wait a bit before next reproduction
            time.sleep(0.5)
            continue
        
        # Fallback to system alarm if file doesn't work
        try:
            # Method 1: Windows - winsound (more reliable)
            import winsound
            if ALARM_ON:
                winsound.Beep(1000, 200)
                time.sleep(0.3)
            continue
        except ImportError:
            pass
        except Exception as e:
            print(f"Error with winsound: {e}")
        
        try:
            # Method 2: Basic terminal beep (multiplatform)
            import sys
            if ALARM_ON:
                for i in range(3):
                    if not ALARM_ON:
                        break
                    sys.stdout.write('\a')
                    sys.stdout.flush()
                    time.sleep(0.1)
                time.sleep(0.5)
            continue
        except Exception as e:
            print(f"Error with basic beep: {e}")
        
        try:
            # Method 3: Linux/Mac - system command
            import subprocess
            import platform
            
            system = platform.system().lower()
            if ALARM_ON:
                if 'linux' in system:
                    try:
                        subprocess.run(['beep', '-f', '1000', '-l', '200'], check=False)
                    except FileNotFoundError:
                        subprocess.run(['speaker-test', '-t', 'sine', '-f', '1000', '-l', '1'], 
                                     timeout=1, check=False, capture_output=True)
                elif 'darwin' in system:  # Mac
                    subprocess.run(['say', 'Drowsiness alert'], check=False)
                
                time.sleep(1)
            continue
        except Exception as e:
            print(f"Error with system command: {e}")
        
        # Final method: visual warning only
        if ALARM_ON:
            print("🚨 DROWSINESS ALERT! 🚨")
            time.sleep(1)


def calculate_eye_ratio(landmarks, eye_points):
    """
    Calculate eye aspect ratio using MediaPipe landmarks
    
    :param landmarks: facial landmarks from MediaPipe
    :param eye_points: eye point indices for calculation
    :return: eye aspect ratio (EAR)
    """
    # Extract coordinates of specific eye points
    eye_coords = []
    for point in eye_points:
        x = landmarks[point].x
        y = landmarks[point].y
        eye_coords.append([x, y])
    
    eye_coords = np.array(eye_coords)
    
    # Calculate euclidean distances
    # Vertical distances
    A = dist.euclidean(eye_coords[1], eye_coords[5])  # top-bottom 1
    B = dist.euclidean(eye_coords[2], eye_coords[4])  # top-bottom 2
    
    # Horizontal distance
    C = dist.euclidean(eye_coords[0], eye_coords[3])  # outer corner - inner corner
    
    # Calculate EAR
    if C > 0:
        ear = (A + B) / (2.0 * C)
    else:
        ear = 0
        
    return ear


def extract_eye_coordinates(landmarks, eye_landmarks):
    """
    Extract eye landmark coordinates for visualization
    
    :param landmarks: facial landmarks
    :param eye_landmarks: eye landmark indices
    :return: array with eye point coordinates
    """
    coords = []
    for point in eye_landmarks:
        x = int(landmarks[point].x * frame.shape[1])
        y = int(landmarks[point].y * frame.shape[0])
        coords.append([x, y])
    return np.array(coords)


# Check available audio library
print("[INFO] Checking audio libraries...")
check_audio_library()

# Initialize MediaPipe
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Configure Face Mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# initialize video stream
print("[INFO] Starting video stream...")
vs = VideoStream(src=WEBCAM).start()
time.sleep(2.0)

print("[INFO] Drowsiness detector started. Press 'q' to quit.")
print(f"[INFO] Eye threshold: {EYE_THRESHOLD}")
print(f"[INFO] Required consecutive frames: {NUM_CONSECUTIVE_FRAMES}")
if AUDIO_LIBRARY:
    print(f"[INFO] Alarm file: {ALARM_FILE}")
else:
    print("[INFO] Using system alarm")

# loop over video frames
while True:
    frame = vs.read()
    if frame is None:
        continue
        
    frame = imutils.resize(frame, width=800)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process frame with MediaPipe
    results = face_mesh.process(rgb_frame)
    
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Calculate EAR for both eyes
            left_ear = calculate_eye_ratio(face_landmarks.landmark, LEFT_EYE_EAR_POINTS)
            right_ear = calculate_eye_ratio(face_landmarks.landmark, RIGHT_EYE_EAR_POINTS)
            
            # Average EAR
            ear = (left_ear + right_ear) / 2.0
            
            # Extract coordinates to draw eye contours
            left_eye_coords = extract_eye_coordinates(face_landmarks.landmark, LEFT_EYE_LANDMARKS)
            right_eye_coords = extract_eye_coordinates(face_landmarks.landmark, RIGHT_EYE_LANDMARKS)
            
            # Draw eye contours
            left_hull = cv2.convexHull(left_eye_coords)
            right_hull = cv2.convexHull(right_eye_coords)
            cv2.drawContours(frame, [left_hull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [right_hull], -1, (0, 255, 0), 1)
            
            # Check if EAR is below threshold
            if ear < EYE_THRESHOLD:
                COUNTER += 1
                
                # If reached consecutive frames number, start alarm
                if COUNTER >= NUM_CONSECUTIVE_FRAMES:
                    if not ALARM_ON:
                        ALARM_ON = True
                        print(f"[ALERT] Drowsiness detected! EAR: {ear:.3f}")
                        # Start continuous alarm thread
                        ALARM_THREAD = Thread(target=trigger_continuous_alarm)
                        ALARM_THREAD.daemon = True
                        ALARM_THREAD.start()
                    
                    # Show alert on screen (with more intense color)
                    cv2.putText(frame, "[ALERT] DROWSINESS DETECTED!", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
                    cv2.putText(frame, "WAKE UP! STOP TO REST!", (10, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            else:
                # EAR returned to normal - turn off alarm only if it was active
                if ALARM_ON:
                    ALARM_ON = False
                    print(f"[INFO] Alarm turned off. EAR returned to normal: {ear:.3f}")
                
                # Reset counter only when EAR returns to normal
                COUNTER = 0
            
            # Show EAR on screen with color based on status
            ear_color = (0, 0, 255) if ALARM_ON else (0, 255, 0)
            cv2.putText(frame, "EAR: {:.3f}".format(ear), (500, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, ear_color, 2)
            
            # Show counter
            cv2.putText(frame, "Counter: {}".format(COUNTER), (500, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, ear_color, 2)
            
            # Show alarm status
            status_text = "ALARM: ACTIVE" if ALARM_ON else "ALARM: INACTIVE"
            status_color = (0, 0, 255) if ALARM_ON else (0, 255, 0)
            cv2.putText(frame, status_text, (500, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            # Show type of alarm being used
            alarm_type = AUDIO_LIBRARY if AUDIO_LIBRARY else "System"
            cv2.putText(frame, f"Audio: {alarm_type}", (500, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    else:
        # No face detected - keep alarm if it was active
        cv2.putText(frame, "No face detected", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Show frame
    cv2.imshow("Drowsiness Detector - MediaPipe", frame)
    key = cv2.waitKey(1) & 0xFF
    
    # Exit with 'q'
    if key == ord("q"):
        break

# Cleanup
print("[INFO] Shutting down...")
ALARM_ON = False  # Stop alarm before shutting down

# Wait for alarm thread to finish
if ALARM_THREAD and ALARM_THREAD.is_alive():
    time.sleep(0.5)

# Clean pygame if it was used
if AUDIO_LIBRARY == "pygame":
    try:
        import pygame
        pygame.mixer.quit()
    except:
        pass

cv2.destroyAllWindows()
vs.stop()
face_mesh.close()
print("[INFO] System shut down.")