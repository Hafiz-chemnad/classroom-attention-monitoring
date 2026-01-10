import cv2

def start_camera():
    # 0 = default laptop camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Error: Cannot access camera")
        return

    print("✅ Camera started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("❌ Failed to grab frame")
            break

        cv2.imshow("Classroom Live Feed", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_camera()
