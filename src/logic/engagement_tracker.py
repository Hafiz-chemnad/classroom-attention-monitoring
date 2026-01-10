class EngagementTracker:
    def __init__(self):
        # student_id -> {"total": int, "matched": int}
        self.student_stats = {}

    def update(self, student_id, behavior_matched, expected_behavior):
        """
        Update engagement stats for a student in current frame
        """

        # If no command / any behavior allowed → do nothing
        if expected_behavior == "any":
            return

        if student_id not in self.student_stats:
            self.student_stats[student_id] = {
                "total": 0,
                "matched": 0
            }

        self.student_stats[student_id]["total"] += 1

        if behavior_matched:
            self.student_stats[student_id]["matched"] += 1

    def reset(self):
        """
        Reset stats when a new command starts
        """
        self.student_stats = {}

    def get_stats(self):
        return self.student_stats


# Simple test
if __name__ == "__main__":
    tracker = EngagementTracker()

    # Simulate frames
    tracker.update(student_id=1, behavior_matched=True, expected_behavior="writing")
    tracker.update(student_id=1, behavior_matched=False, expected_behavior="writing")
    tracker.update(student_id=2, behavior_matched=True, expected_behavior="writing")

    print(tracker.get_stats())
