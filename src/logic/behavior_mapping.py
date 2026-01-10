class BehaviorMapper:
    def __init__(self):
        self.command_behavior_map = {
            "pay attention": "looking_forward",
            "look here": "looking_forward",
            "write": "writing",
            "read": "reading",
            "raise hand": "hand_raised"
        }

    def get_expected_behavior(self, command):
        # No command → any behavior is acceptable
        if command is None:
            return "any"

        return self.command_behavior_map.get(command, "unknown")


# Test block
if __name__ == "__main__":
    mapper = BehaviorMapper()

    test_commands = [
        "pay attention",
        "write",
        "read",
        "sleep",
        None
    ]

    for cmd in test_commands:
        behavior = mapper.get_expected_behavior(cmd)
        print(f"Command: {cmd} -> Expected Behavior: {behavior}")
