import time

class SessionManager:
    def __init__(self, duration_minutes=60):
        self.duration = duration_minutes * 60
        self.start_time = None
        self.subject = None

    def start(self, subject_name):
        self.subject = subject_name
        self.start_time = time.time()
        print(f"[SESSION STARTED] Subject: {self.subject}")

    def is_active(self):
        if self.start_time is None:
            return False
        return (time.time() - self.start_time) < self.duration

    def remaining_time(self):
        if self.start_time is None:
            return 0
        return int(self.duration - (time.time() - self.start_time))

    def end(self):
        print(f"[SESSION ENDED] Subject: {self.subject}")
        self.start_time = None
        self.end_time = time.time()

