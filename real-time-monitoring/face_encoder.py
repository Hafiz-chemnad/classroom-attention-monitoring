# face_encoder.py
import logging

class FaceEncoder:
    def __init__(self):
        self.active = False
        try:
            # We only try to import when needed to prevent startup crashes
            import tensorflow as tf
            import keras
            tf.keras = keras
            from deepface import DeepFace
            self.active = True
        except Exception as e:
            logging.warning(f"Face Recognition disabled due to library conflict: {e}")

    def encode(self, face_img):
        if not self.active or face_img is None or face_img.size == 0:
            return None
            
        try:
            from deepface import DeepFace
            embedding = DeepFace.represent(
                img_path = face_img,
                model_name = "Facenet512",
                enforce_detection = False,
                detector_backend = 'skip'
            )
            return embedding[0]["embedding"] if embedding else None
        except:
            return None