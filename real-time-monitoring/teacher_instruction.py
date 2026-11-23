class TeacherInstruction:
    def __init__(self):
        # തുടക്കത്തിൽ listening മാത്രം സെറ്റ് ചെയ്യുന്നു
        self.current_instruction = "listening"

    def set_instruction(self, instruction):
        self.current_instruction = instruction
        # 💡 നമ്മൾ ഡ്രോപ്പ്-ഡൗൺ മാറ്റുമ്പോൾ ടെർമിനലിൽ ഈ മെസ്സേജ് വരണം
        print(f"\n[INFO] 🎯 Teacher Instruction changed to: ---> {instruction.upper()} <---")

    def is_attentive(self, student_action):
        # 💡 കോംബോ ഇൻസ്ട്രക്ഷൻസ് 
        if self.current_instruction == "listening":
            return student_action == "listening"
            
        elif self.current_instruction == "reading":
            return student_action == "reading"
            
        elif self.current_instruction == "writing":
            return student_action == "writing"
            
        elif self.current_instruction == "listen_read":
            return student_action in ["listening", "reading"]
            
        elif self.current_instruction == "listen_write":
            return student_action in ["listening", "writing"]
            
        elif self.current_instruction == "read_write":
            return student_action in ["reading", "writing"]
            
        # 💡 ഫ്രീ ടൈമിൽ കുട്ടി എന്ത് ചെയ്താലും അറ്റൻഷൻ 100% ആയിരിക്കും (കുറയില്ല)
        elif self.current_instruction == "free_time":
            return True 

        return False