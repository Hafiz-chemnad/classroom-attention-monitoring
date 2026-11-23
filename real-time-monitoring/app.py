import os
import threading
import time
import cv2
import uvicorn
import tensorflow as tf
import keras
import traceback 

# Patch for Keras
tf.keras = keras 

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse # FileResponse കൂടി ചേർത്തു

app = FastAPI(title="AI Classroom Monitoring System")

# app.py -ൽ ഈ മാറ്റം വരുത്തുക
os.makedirs("static", exist_ok=True) # "main/static" മാറ്റി "static" ആക്കി
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates") # "main/templates" മാറ്റി "templates" ആക്കി

# --- INITIALIZATION ---
try:
    from phase4_main import ClassroomAI
    from session_manager import SessionManager
    from report_generator import ReportGenerator
    
    ai_engine = ClassroomAI()
    session_manager = SessionManager()
    reporter = ReportGenerator()
    is_dummy_mode = False
    print("[DEBUG] All Engines Loaded Successfully.")

except Exception as e:
    print(f"[CRITICAL ERROR] {e}")
    traceback.print_exc()
    is_dummy_mode = True
    ai_engine = None
    session_manager = None
    reporter = None

latest_frame = None

def ai_worker():
    global latest_frame
    while True:
        if ai_engine:
            frame, _ = ai_engine.get_processed_frame()
            if frame is not None:
                _, buffer = cv2.imencode('.jpg', frame)
                latest_frame = buffer.tobytes()
            else:
                time.sleep(0.1)
        else:
            time.sleep(1)

if not is_dummy_mode:
    threading.Thread(target=ai_worker, daemon=True).start()

@app.get("/")
async def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
# app.py ഉള്ളിൽ ഈ വരികൾ ഉണ്ടെന്ന് ഉറപ്പുവരുത്തുക
@app.get("/admin")
async def admin_portal(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/student/{reg_no}")
async def student_portal(request: Request, reg_no: str):
    return templates.TemplateResponse("student.html", {"request": request, "reg_no": reg_no})    

# app.py -ലെ മാറ്റം
@app.get("/video_feed")
async def video_feed():
    def stream():
        while True:
            if ai_engine:
                frame, _ = ai_engine.get_processed_frame()
                if frame is not None:
                    # Quality 70% ആക്കി കുറയ്ക്കുന്നു (സ്പീഡ് കൂടാൻ)
                    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                # 💡 ബ്രൗസറിന് ശ്വസിക്കാൻ സമയം നൽകുന്നു
                time.sleep(0.05) 
    return StreamingResponse(stream(), media_type="multipart/x-mixed-replace; boundary=frame")

# --- 💡 അപ്ഡേറ്റ് ചെയ്ത ലൈവ് ഡാറ്റ (With Total Score) ---
@app.get("/live_data")
async def get_all_data():
    formatted_data = []
    total_score_sum = 0
    valid_students = 0
    
    source_data = {}
    if ai_engine and hasattr(ai_engine, 'temporal'):
        source_data = ai_engine.temporal.data
    
    for reg_no, stats in source_data.items():
        score = 0
        if stats.get("present_time", 0) > 0:
            score = int((stats["attentive_time"] / stats["present_time"]) * 100)
            total_score_sum += score
            valid_students += 1
            
        current_action = "Unknown"
        clean_id = reg_no.replace("Student_", "")
        
        if hasattr(ai_engine, 'student_cache'):
            if clean_id in ai_engine.student_cache:
                current_action = ai_engine.student_cache[clean_id]['action']

        formatted_data.append({
            "id": reg_no,
            "action": current_action,
            "score": score
        })
    
    # മൊത്തത്തിലുള്ള ക്ലാസ്സ് സ്കോർ
    class_average = int(total_score_sum / valid_students) if valid_students > 0 else 0
        
    return JSONResponse(content={
        "students": formatted_data,
        "class_score": class_average
    })

@app.post("/start_session")
async def start_session(request: Request):
    data = await request.json()
    subject = data.get("subject", "Unknown Subject")
    if session_manager: session_manager.start(subject)
    if ai_engine and hasattr(ai_engine, 'temporal'): ai_engine.temporal.reset()
    return {"status": "started", "subject": subject}

@app.post("/stop_session")
async def stop_session():
    global class_active
    class_active = False 
    
    if not session_manager or not session_manager.is_active():
        return {"status": "error", "message": "No active session"}
    
    subject = session_manager.subject
    session_manager.end()
    
    report_filename = None
    # റിപ്പോർട്ട് ജനറേറ്റ് ചെയ്യുന്നു
    if reporter and ai_engine and ai_engine.temporal.data:
        report_path = reporter.generate(subject, ai_engine.temporal.data)
        report_filename = os.path.basename(report_path) # ഫയലിന്റെ പേര് മാത്രം എടുക്കുന്നു
        
    return {
        "status": "stopped", 
        "message": "Session Ended. Report Saved!", 
        "report_file": report_filename # ബ്രൗസറിലേക്ക് ഫയലിന്റെ പേര് അയക്കുന്നു
    }

# 💡 റിപ്പോർട്ട് ഡൗൺലോഡ് ചെയ്യാനുള്ള പുതിയ റൂട്ട്
@app.get("/download/{filename}")
async def download_report(filename: str):
    file_path = os.path.join("reports", filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename, media_type='text/csv')
    return JSONResponse(content={"error": "File not found"}, status_code=404)
# 💡 UI-ൽ നിന്നും instruction സ്വീകരിക്കാനുള്ള റൂട്ട്
@app.post("/set_instruction/{cmd}")
async def set_instruction(cmd: str):
    print(f"[DEBUG] Received UI Command: {cmd}") # ഇത് വർക്ക് ആകുന്നുണ്ടോ എന്ന് അറിയാൻ
    if ai_engine and hasattr(ai_engine, 'instruction'):
        ai_engine.instruction.set_instruction(cmd)
    return {"status": "success"}    
# 💡 Nudge സിസ്റ്റത്തിന് വേണ്ടിയുള്ള കോഡ്
nudge_store = {}

@app.post("/nudge/{reg_no}")
async def send_nudge(reg_no: str):
    # അഡ്മിൻ പാനലിൽ നിന്ന് വരുന്ന ഐഡി "Student_1" എന്ന രീതിയിലായിരിക്കും
    nudge_store[reg_no] = True
    return {"status": "Nudge sent successfully!"}

@app.get("/check_nudge/{reg_no}")
async def check_nudge(reg_no: str):
    # കുട്ടിക്ക് അലേർട്ട് ഉണ്ടോ എന്ന് ചെക്ക് ചെയ്യുന്നു
    has_nudge = nudge_store.get(reg_no, False)
    if has_nudge:
        nudge_store[reg_no] = False # അലേർട്ട് കാണിച്ച ശേഷം അത് ഓഫ് ചെയ്യുന്നു
    return {"nudge": has_nudge}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)