import time

class TeacherCommandManager:
    def __init__(self):
        self.current_command = None
        self.command_start_time = None

    def set_command(self, command):
        self.current_command = command
        self.command_start_time = time.time()
        print(f"\n🧑‍🏫 New command started: '{command}'")

    def get_current_command(self):
        return self.current_command

    def get_command_duration(self):
        if self.command_start_time is None:
            return 0
        return int(time.time() - self.command_start_time)


def start_command_input():
    manager = TeacherCommandManager()

    print("Teacher Command Module Started")
    print("Type commands like: pay attention, read, write")
    print("Type 'exit' to stop\n")

    while True:
        command = input("Teacher Command ➜ ").strip().lower()

        if command == "exit":
            print("Command module stopped")
            break

        if command == "":
            print("Empty command ignored")
            continue

        manager.set_command(command)

        print(
            f"⏱ Command '{manager.get_current_command()}' running for "
            f"{manager.get_command_duration()} seconds"
        )


if __name__ == "__main__":
    start_command_input()
