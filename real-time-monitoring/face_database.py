# face_database.py
import numpy as np

class FaceDatabase:
    def __init__(self):
        self.students = {}  # reg_no → embedding

    def add_student(self, reg_no, embedding):
        self.students[reg_no] = np.array(embedding)

    def get_all(self):
        return self.students
