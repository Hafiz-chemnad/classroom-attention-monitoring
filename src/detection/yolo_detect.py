import cv2
import math
from ultralytics import YOLO

DISTANCE_THRESHOLD = 80
MAX_MISSING_FRAMES = 15

def get_centroid(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) // 2, (y1 + y2) // 2)

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def start_detection():
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(0)

    next_id = 1
    tracked = {}  # id -> {"centroid": (x,y), "missing": 0}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, stream=True)
        detections = []

        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == 0:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    centroid = get_centroid((x1, y1, x2, y2))
                    detections.append((x1, y1, x2, y2, centroid))

        assigned_ids = set()
        updated = {}

        for det in detections:
            x1, y1, x2, y2, centroid = det
            best_id = None
            min_dist = DISTANCE_THRESHOLD

            for sid, data in tracked.items():
                if sid in assigned_ids:
                    continue
                d = distance(centroid, data["centroid"])
                if d < min_dist:
                    min_dist = d
                    best_id = sid

            if best_id is None:
                best_id = next_id
                next_id += 1

            assigned_ids.add(best_id)
            updated[best_id] = {"centroid": centroid, "missing": 0}

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"Student_{best_id}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        # Handle missing students
        for sid, data in tracked.items():
            if sid not in updated:
                data["missing"] += 1
                if data["missing"] <= MAX_MISSING_FRAMES:
                    updated[sid] = data

        tracked = updated

        cv2.imshow("Stable Student Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_detection()
