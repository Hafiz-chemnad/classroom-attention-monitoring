# phase4_detector.py
from ultralytics import YOLO

class PersonDetector:
    def __init__(self):
        self.model = YOLO("models/yolov8n.pt")

    def detect(self, frame):
        # മാറ്റം 1: conf=0.25 ആക്കുക (ദൂരെയുള്ളവരെയും പിടിക്കാൻ)
        # മാറ്റം 2: iou=0.5 (അടുത്തടുത്ത് ഇരിക്കുന്നവരെ ഒഴിവാക്കാതിരിക്കാൻ)
        results = self.model(frame, classes=[0], conf=0.25, iou=0.5, verbose=False)

        boxes = []
        for r in results:
            for b in r.boxes:
                x1, y1, x2, y2 = map(int, b.xyxy[0])
                
                # തീരെ ചെറിയ ബോക്സുകൾ മാത്രം ഒഴിവാക്കുക
                if (x2 - x1) < 20 or (y2 - y1) < 20:
                    continue
                boxes.append((x1, y1, x2, y2))
        return boxes