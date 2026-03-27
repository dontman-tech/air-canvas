import cv2
import numpy as np
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --------------------- Helper Function for Drawing ---------------------
def draw_hand_landmarks(image, hand_landmarks):
    h, w, _ = image.shape
    landmarks = []

    for lm in hand_landmarks:
        x = int(lm.x * w)
        y = int(lm.y * h)
        landmarks.append((x, y))

    connections = [
        (0,1),(1,2),(2,3),(3,4), (0,5),(5,6),(6,7),(7,8),
        (0,9),(9,10),(10,11),(11,12), (0,13),(13,14),(14,15),(15,16),
        (0,17),(17,18),(18,19),(19,20), (5,9),(9,13),(13,17)
    ]

    for start, end in connections:
        if start < len(landmarks) and end < len(landmarks):
            cv2.line(image, landmarks[start], landmarks[end], (0, 255, 0), 2)

    for x, y in landmarks:
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)

    return image


def main():
    print("Starting Air Canvas with Color Picker + Eraser...")

    model_path = 'hand_landmarker.task'
    if not os.path.exists(model_path):
        print("ERROR: 'hand_landmarker.task' not found!")
        print("Download it with:")
        print("   curl -O https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task")
        input("Press Enter to exit...")
        return

    # MediaPipe Setup
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.8,
        min_hand_presence_confidence=0.8,
        min_tracking_confidence=0.8
    )
    hand_landmarker = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    canvas = None
    prev_x, prev_y = 0, 0
    current_color = (255, 0, 255)   # Default: Magenta
    thickness = 8
    eraser_thickness = 30

    # Color Palette: [BGR colors]
    colors = [
        (0, 0, 255),    # Red
        (0, 165, 255),  # Orange
        (0, 255, 255),  # Yellow
        (0, 255, 0),    # Green
        (255, 0, 0),    # Blue
        (255, 0, 255)   # Magenta (default)
    ]
    color_names = ["Red", "Orange", "Yellow", "Green", "Blue", "Magenta"]
    palette_y = 20
    box_width = 60
    box_height = 50

    print("\n--- Controls ---")
    print("1. Index finger only              → DRAW with current color")
    print("2. Index + Middle                 → HOVER")
    print("3. Index + Middle + Ring          → ERASER")
    print("4. Index + Middle + Ring + Pinky  → COLOR PICKER (pinch to select)")
    print("5. Press c                        → CLEAR canvas")
    print("6. Press q                        → QUIT")
    print("----------------\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        if canvas is None:
            canvas = np.zeros_like(frame)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        detection_result = hand_landmarker.detect(mp_image)

        # Draw color palette at the top
        for i, color in enumerate(colors):
            x1 = 50 + i * (box_width + 10)
            x2 = x1 + box_width
            y1 = palette_y
            y2 = y1 + box_height
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.putText(frame, color_names[i][:3], (x1+5, y2-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Show current color
        cv2.putText(frame, "Current:", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.rectangle(frame, (130, 100), (190, 140), current_color, -1)

        if detection_result.hand_landmarks:
            for hand_landmarks in detection_result.hand_landmarks:
                frame = draw_hand_landmarks(frame, hand_landmarks)

                h, w, _ = frame.shape
                lm_list = [[int(lm.x * w), int(lm.y * h)] for lm in hand_landmarks]

                if len(lm_list) >= 21:
                    x1, y1 = lm_list[8]   # Index tip
                    thumb_x, thumb_y = lm_list[4]   # Thumb tip

                    index_up  = lm_list[8][1]  < lm_list[6][1]
                    middle_up = lm_list[12][1] < lm_list[10][1]
                    ring_up   = lm_list[16][1] < lm_list[14][1]
                    pinky_up  = lm_list[20][1] < lm_list[18][1]

                    # ==================== COLOR PICKER MODE ====================
                    if index_up and middle_up and ring_up and pinky_up:
                        cv2.putText(frame, "COLOR PICKER - Pinch over color", (20, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

                        # Check if index finger is over any color box
                        for i, color in enumerate(colors):
                            box_x1 = 50 + i * (box_width + 10)
                            box_x2 = box_x1 + box_width
                            if box_x1 < x1 < box_x2 and palette_y < y1 < palette_y + box_height:
                                cv2.rectangle(frame, (box_x1-5, palette_y-5),
                                              (box_x2+5, palette_y+box_height+5), (255, 255, 255), 3)

                                # Pinch detection (thumb close to index)
                                distance = np.hypot(thumb_x - x1, thumb_y - y1)
                                if distance < 40:   # Pinch threshold
                                    current_color = color
                                    cv2.putText(frame, f"Selected: {color_names[i]}", (20, 180),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                                    break

                        prev_x, prev_y = 0, 0

                    # ==================== ERASER MODE ====================
                    elif index_up and middle_up and ring_up:
                        cv2.circle(frame, (x1, y1), eraser_thickness, (255, 255, 255), 2)
                        cv2.putText(frame, "ERASER MODE", (20, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                        if prev_x != 0 or prev_y != 0:
                            cv2.line(canvas, (prev_x, prev_y), (x1, y1), (0, 0, 0), eraser_thickness)
                        prev_x, prev_y = x1, y1

                    # ==================== DRAWING MODE ====================
                    elif index_up and not middle_up:
                        cv2.circle(frame, (x1, y1), 15, current_color, cv2.FILLED)
                        cv2.putText(frame, "Drawing Mode", (20, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                        if prev_x == 0 and prev_y == 0:
                            prev_x, prev_y = x1, y1

                        cv2.line(canvas, (prev_x, prev_y), (x1, y1), current_color, thickness)
                        prev_x, prev_y = x1, y1

                    # ==================== HOVER MODE ====================
                    else:
                        prev_x, prev_y = 0, 0

        else:
            prev_x, prev_y = 0, 0

        # Merge canvas
        gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_canvas, 1, 255, cv2.THRESH_BINARY_INV)
        frame_bg = cv2.bitwise_and(frame, frame, mask=mask)
        final_frame = cv2.bitwise_or(frame_bg, canvas)

        cv2.imshow("Air Canvas AI - Color Picker", final_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            canvas = np.zeros_like(frame)
            print("Canvas cleared!")

    cap.release()
    cv2.destroyAllWindows()
    print("Air Canvas closed.")


if __name__ == "__main__":
    main()