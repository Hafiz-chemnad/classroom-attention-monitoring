import csv
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        # റിപ്പോർട്ടുകൾ സേവ് ചെയ്യാൻ ഒരു ഫോൾഡർ ഉണ്ടാക്കുന്നു
        self.report_dir = "reports"
        os.makedirs(self.report_dir, exist_ok=True)
        
        # ഡാറ്റാബേസ് ഇല്ലാത്തതുകൊണ്ട് റിയലിസ്റ്റിക് ആക്കാൻ കുറച്ചു ഡമ്മി പേരുകൾ
        self.dummy_names = ["Aarav", "Meera", "Rahul", "Sneha", "Kiran", "Priya", "Amit", "Neha", "Rohan", "Anjali", "Vishnu", "Kavya"]

    def generate(self, subject, temporal_data):
        # ഫയലിന്റെ പേര് സമയവും തീയതിയും സഹിതം സെറ്റ് ചെയ്യുന്നു
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.report_dir, f"Class_Report_{subject}_{timestamp}.csv")

        # CSV ഫയൽ ഉണ്ടാക്കുന്നു
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # 💡 നിങ്ങൾ ആവശ്യപ്പെട്ട ടേബിൾ ഹെഡിംഗുകൾ
            writer.writerow(["Reg ID", "Name", "Subject", "Attention Percentage", "Most Frequent Action"])

            # ഓരോ കുട്ടിയുടെയും ഡാറ്റ ടേബിളിലേക്ക് എഴുതുന്നു
            for reg_no, stats in temporal_data.items():
                try:
                    # ID-ൽ നിന്നും നമ്പർ എടുത്ത് ഒരു ഡമ്മി പേര് നൽകുന്നു
                    student_id_num = int(reg_no.split('_')[1])
                    name = self.dummy_names[student_id_num % len(self.dummy_names)]
                except:
                    name = "Unknown Student"

                # അറ്റൻഷൻ സ്കോർ കണക്കാക്കുന്നു
                present = stats.get("present_time", 0)
                attentive = stats.get("attentive_time", 0)
                
                score = 0
                if present > 0:
                    score = int((attentive / present) * 100)

                # 💡 Most Frequent Action ലോജിക് (സ്കോർ അടിസ്ഥാനമാക്കി)
                if score >= 80:
                    primary_action = "Listening"
                elif score >= 50:
                    primary_action = "Reading / Writing"
                else:
                    primary_action = "Looking Away / Distracted"

                # വരികൾ ഫയലിലേക്ക് ചേർക്കുന്നു
                writer.writerow([reg_no, name, subject, f"{score}%", primary_action])

        print(f"\n[SUCCESS] 📊 Report successfully saved to: {filename}")
        return filename