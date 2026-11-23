import cv2
import mediapipe as mp

class HeadPoseEstimator:
    def __init__(self):
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True
        )

    def get_pose(self, frame):
        """Returns (yaw, pitch) to help distinguish reading/writing from looking forward."""
        if frame is None or frame.size == 0:
            return None, None

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None, None

        landmarks = results.multi_face_landmarks[0].landmark

        # Landmarks: 1=Nose, 33=Left Eye, 263=Right Eye, 10=Forehead, 152=Chin
        nose = landmarks[1]
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        forehead = landmarks[10]
        chin = landmarks[152]

        # --- YAW CALCULATION (Side-to-Side) ---
        eye_center_x = (left_eye.x + right_eye.x) / 2
        yaw = (nose.x - eye_center_x) * 100 # Normalized side-rotation

        # --- PITCH CALCULATION (Up-and-Down) ---
        # Calculate the midpoint of the face vertically
        face_center_y = (forehead.y + chin.y) / 2
        # If nose is below the center, pitch is positive (looking down)
        pitch = (nose.y - face_center_y) * 100 

        return yaw, pitch