# 🚨 Drowsiness Detection System

A real-time drowsiness detection system using MediaPipe and computer vision to help prevent accidents caused by driver fatigue or sleepiness during work.

## 🎯 Features

- **Real-time face detection** using MediaPipe Face Mesh
- **Eye Aspect Ratio (EAR) calculation** for drowsiness detection
- **Customizable audio alerts** with multiple audio library support
- **Visual feedback** with eye contour highlighting
- **Cross-platform compatibility** (Windows, macOS, Linux)
- **Configurable thresholds** for sensitivity adjustment

## 🛠️ How It Works

The system uses the **Eye Aspect Ratio (EAR)** technique:

1. **Face Detection**: MediaPipe detects facial landmarks in real-time
2. **Eye Tracking**: Extracts specific eye landmarks for both eyes
3. **EAR Calculation**: Computes the ratio between eye height and width
4. **Drowsiness Detection**: When EAR drops below threshold for consecutive frames, triggers alarm
5. **Alert System**: Plays audio alarm and shows visual warnings

### EAR Formula
```
EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
```

Where p1-p6 are eye landmark points.

## 📋 Requirements

- Python 3.7+
- Webcam
- Audio file for alarm (optional - system beep as fallback)

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/drowsiness-detection.git
cd drowsiness-detection
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **For audio support, install at least one of these:**
```bash
# Recommended: pygame (cross-platform)
pip install pygame

# Alternative options:
pip install playsound  # Simple but may have issues
pip install pydub simpleaudio  # Flexible, requires ffmpeg
```

## 🎵 Audio Setup

### Option 1: Use Custom Audio File
1. Place your audio file (`.wav`, `.mp3`, `.ogg`, `.flac`) in the project directory
2. Update the `ALARM_FILE` variable in the code with your file path:
```python
ALARM_FILE = "path/to/your/alarm/sound.wav"
```

### Option 2: Use System Beep
If no audio file is found or audio libraries fail, the system will automatically fall back to system beep sounds.

## 🎮 Usage

1. **Basic usage:**
```bash
python drowsiness_detector.py
```

2. **Customize settings** by editing these variables:
```python
EYE_THRESHOLD = 0.68        # Lower = more sensitive
NUM_CONSECUTIVE_FRAMES = 100  # Frames before triggering alarm
WEBCAM = 0                  # Camera index
```

3. **Controls:**
- Press `q` to quit the application
- Green contours = normal eye state
- Red contours = drowsiness detected

## ⚙️ Configuration

### Sensitivity Adjustment
- **EYE_THRESHOLD**: Lower values (0.2-0.25) = more sensitive, Higher values (0.3-0.35) = less sensitive
- **NUM_CONSECUTIVE_FRAMES**: Lower values = faster detection, Higher values = fewer false positives

### Audio Libraries Priority
The system tries audio libraries in this order:
1. **pygame** (recommended - most reliable)
2. **playsound** (simple but may have compatibility issues)
3. **pydub** (requires simpleaudio for playback)
4. **winsound** (Windows only, .wav files only)
5. **System beep** (fallback)

## 🔧 Troubleshooting

### Common Issues

**"No audio library found"**
```bash
pip install pygame  # Most reliable solution
```

**Camera not found**
- Check camera permissions
- Try different WEBCAM indices (0, 1, 2...)
- Ensure no other applications are using the camera

**High CPU usage**
- Reduce frame size in the code
- Increase sleep time between frames
- Use fewer face mesh points

**False positives/negatives**
- Adjust `EYE_THRESHOLD` based on lighting conditions
- Modify `NUM_CONSECUTIVE_FRAMES` for your needs
- Ensure good lighting on your face

### Platform-Specific Notes

**Linux:**
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
sudo apt-get install ffmpeg  # for pydub support
```

**macOS:**
```bash
brew install portaudio
brew install ffmpeg  # for pydub support
```

**Windows:**
- Windows users should have fewer audio issues
- `.wav` files work with built-in winsound

## 📊 Technical Details

- **Face Detection**: MediaPipe Face Mesh (468 landmarks)
- **Eye Landmarks**: 16 points per eye for contour detection
- **EAR Calculation**: 6 specific points per eye
- **Processing**: ~30 FPS on modern hardware
- **Memory**: ~50-100MB RAM usage

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] GUI interface
- [ ] Mobile app version
- [ ] Advanced drowsiness metrics
- [ ] Data logging and analytics
- [ ] Integration with vehicle systems
- [ ] Machine learning improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Based on Adrian Rosebrock's drowsiness detection work
- MediaPipe team for excellent face mesh technology
- Computer vision community for EAR technique development

## ⚠️ Disclaimer

This system is intended as a supplementary safety tool and should not be relied upon as the primary method for preventing drowsy driving or workplace accidents. Always prioritize proper rest and safe practices.

---

**Stay Alert, Stay Safe! 🚨**