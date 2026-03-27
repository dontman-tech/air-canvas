# air-canvas
python script that allows user to draw in air with hand gestures

# 🎨 Air Canvas - Hand Gesture Drawing App

An interactive **Air Canvas** application that lets you draw in the air using hand gestures. Built with **MediaPipe** and **OpenCV**.


## ✨ Features

- **Freehand Drawing** – Draw with your index finger
- **Hover Mode** – Move without drawing (Index + Middle finger)
- **Eraser Mode** – Erase parts of your drawing (Index + Middle + Ring)
- **Color Picker** – Select from 6 colors using gesture (Index + Middle + Ring + Pinky + Pinch)
- **Clear Canvas** – Press `C` to clear everything
- **Real-time Hand Tracking** – Smooth landmark detection
- **Mirror View** – Natural webcam experience

## 🎮 Controls

| Gesture / Key                  | Action                          |
|-------------------------------|---------------------------------|
| **Index finger only**         | Draw with current color         |
| **Index + Middle**            | Hover (move without drawing)    |
| **Index + Middle + Ring**     | Eraser Mode                     |
| **Index + Middle + Ring + Pinky** | Color Picker Mode            |
| **Pinch** (in color picker)   | Select color                    |
| **`C` key**                   | Clear entire canvas             |
| **`Q` key**                   | Quit the application            |

### Color Palette
- Red, Orange, Yellow, Green, Blue, Magenta

## 📋 Requirements

- Python 3.10 or higher
- Webcam

## 🛠️ Installation

1. **Clone or download** this project

2. **Install dependencies**:
   ```bash
   pip install opencv-python mediapipe numpy
