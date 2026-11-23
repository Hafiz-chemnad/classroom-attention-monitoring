# face_recognizer.py
import numpy as np

class FaceRecognizer:
    def __init__(self, threshold=0.6):
        self.threshold = threshold

    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def recognize(self, unknown_embedding, database):
        best_match = None
        best_score = -1

        for reg_no, known_embedding in database.items():
            score = self.cosine_similarity(
                np.array(unknown_embedding),
                known_embedding
            )

            if score > best_score:
                best_score = score
                best_match = reg_no

        if best_score >= self.threshold:
            return best_match

        return None
