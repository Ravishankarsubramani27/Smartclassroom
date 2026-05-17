from flask import Flask, render_template, jsonify, request, redirect, Response
import threading, os, cv2, time
from datetime import datetime
from realtime_engine import realtime_loop
from state import state

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔴 CHANGE THIS TO YOUR MOBILE IP
CAMERA_URL = "http://172.24.198.41:8080/video"

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/data")
def data():
    now = datetime.now().time()
    tt = state["timetable"]

    if tt["start"] and tt["end"] and tt["start"] <= now <= tt["end"]:
        subject = tt["subject"]
        class_type = tt["type"]
    else:
        subject = "No Class"
        class_type = "free"

    return jsonify({
        "subject": subject,
        "class_type": class_type,
        "people": state["people"],
        "comfort": state["comfort"],
        "context": state["context"],
        "actions": state["actions"],
        "camera_online": state["camera_online"]
    })

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["timetable"]
    file.save(os.path.join(UPLOAD_FOLDER, "timetable.jpg"))
    return redirect("/")

def generate_frames():
    while True:
        cap = cv2.VideoCapture(CAMERA_URL)

        if not cap.isOpened():
            state["camera_online"] = False
            time.sleep(2)
            continue

        state["camera_online"] = True

        while True:
            success, frame = cap.read()
            if not success:
                cap.release()
                state["camera_online"] = False
                break

            # 🔮 YOLO overlay hook (future)
            # frame = yolo_detect(frame)

            _, buffer = cv2.imencode(".jpg", frame)
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" +
                   buffer.tobytes() + b"\r\n")

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

if __name__ == "__main__":
    threading.Thread(target=realtime_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
