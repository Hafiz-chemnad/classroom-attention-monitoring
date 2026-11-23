import time
from collections import defaultdict

class TemporalAttention:
    def __init__(self):
        self.data = defaultdict(lambda: {
            "present_time": 0.0,
            "attentive_time": 0.0,
            "last_update": None
        })

    def update(self, reg_no, attentive):
        now = time.time()
        student = self.data[reg_no]

        if student["last_update"] is None:
            student["last_update"] = now
            return

        delta = now - student["last_update"]
        student["last_update"] = now

        # വീഡിയോ പ്ലേ ആകുന്നതിനനുസരിച്ച് സമയം കൂട്ടുന്നു
        student["present_time"] += delta

        if attentive:
            student["attentive_time"] += delta

    def get_percentage(self, reg_no):
        d = self.data[reg_no]
        if d["present_time"] <= 0:
            return 0
        return round((d["attentive_time"] / d["present_time"]) * 100, 2)

    def reset(self):
        self.data.clear()