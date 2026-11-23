import cv2
import time
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from teacher_instruction import TeacherInstruction
from phase4_temporal import TemporalAttention

class ClassroomAI:
    def __init__(self):
        # 1. AI മോഡൽ ലോഡ് ചെയ്യുന്നു
        self.detector = YOLO("best (3).pt") 
        self.instruction = TeacherInstruction()
        self.temporal = TemporalAttention()
        
        # 2. Hybrid ട്രാക്കർ സെറ്റിംഗ്സ്
        self.tracker = DeepSort(
            max_age=50, 
            n_init=3, 
            max_iou_distance=0.15 
        )
        
        # 3. നിങ്ങൾ നൽകിയ അതേ കളർ സെറ്റിംഗ്സ്
        self.colors = {
            "listening": (200, 255, 0),     
            "looking away": (80, 0, 255),    
            "reading": (255, 170, 0),       
            "sleeping": (255, 0, 255),      
            "writing": (0, 150, 255)        
        }
        
        self.cap = cv2.VideoCapture("vdeo.mp4")
        self.student_cache = {}

        # സ്പീഡ് ബൂസ്റ്റർ വേരിയബിളുകൾ
        self.frame_count = 0
        self.frame_skip = 3  # ഓരോ 3 ഫ്രെയിമിൽ ഒരിക്കൽ AI പ്രോസസ്സ് ചെയ്യുന്നു
        self.last_tracks = []

    def get_processed_frame(self):
        ret, frame = self.cap.read()
        
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret: return None, {}
        
        # ലാഗ് ഒഴിവാക്കാൻ റെസലൂഷൻ അല്പം കുറയ്ക്കുന്നു
        frame = cv2.resize(frame, (640, 360))
        self.frame_count += 1

        # 💡 ഹൈബ്രിഡ് ലോജിക്: നിശ്ചിത ഫ്രെയിമുകളിൽ മാത്രം AI ഡിറ്റക്ഷൻ
        if self.frame_count % self.frame_skip == 0:
            # iou=0.15 ഡ്യൂപ്ലിക്കേറ്റ് ബോക്സുകൾ ഒഴിവാക്കാൻ സഹായിക്കും
            results = self.detector(frame, conf=0.25, iou=0.15, verbose=False)[0]
            
            detections = []
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.detector.names[class_id]
                
                # --- 💡 നിങ്ങളുടെ സൂപ്പർ അഡ്വാൻസ്ഡ് PRIORITY LOGIC ---
                final_label = class_name
                
                # 1. Looking away 70% ൽ താഴെയാണെങ്കിൽ Listening
                if class_name == "looking away" and conf < 0.70:
                    final_label = "listening"
                # 2. Writing 35% ൽ താഴെയാണെങ്കിൽ Listening
                elif class_name == "writing" and conf < 0.35:
                    final_label = "listening"
                # 3. Listening 40% ൽ താഴെയാണെങ്കിൽ Reading
                elif class_name == "listening" and conf < 0.40:
                    final_label = "reading"
                
                detections.append(([x1, y1, x2-x1, y2-y1], conf, final_label))

            self.last_tracks = self.tracker.update_tracks(detections, frame=frame)

        # ബോക്സുകൾ വരയ്ക്കൽ
        for track in self.last_tracks:
            if not track.is_confirmed() or track.time_since_update > 2:
                continue
            
            reg_no = f"Student_{track.track_id}"
            short_id = f"S{track.track_id}"
            l, t, r, b = map(int, track.to_ltrb())
            
            # ട്രാക്കറിൽ നിന്നുള്ള ലേബൽ
            current_action = track.get_det_class() or "listening"
            
            # അറ്റൻഷൻ ഹിസ്റ്ററി അപ്‌ഡേറ്റ്
            attentive = self.instruction.is_attentive(current_action)
            self.temporal.update(reg_no, attentive)
            
            color = self.colors.get(current_action, (255, 255, 255))
            
            # UI ക്ലീൻ ആക്കാൻ കട്ടി കുറഞ്ഞ ബോക്സ്
            cv2.rectangle(frame, (l, t), (r, b), color, 1)
            cv2.putText(frame, short_id, (l, t-5), cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

            # app.py ടേബിളിന് വേണ്ടി
            self.student_cache[track.track_id] = {'action': current_action}

        return frame, self.temporal.data

    def stop(self):
        self.cap.release()