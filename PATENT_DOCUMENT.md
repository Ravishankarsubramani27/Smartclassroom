# PATENT APPLICATION DOCUMENT

---

**Title of Invention:**
INTELLIGENT REAL-TIME CLASSROOM AUTOMATION SYSTEM WITH COMPUTER VISION-BASED OCCUPANCY DETECTION AND ADAPTIVE ENVIRONMENTAL CONTROL

---

**Field of the Invention**

The present invention relates to smart building automation systems, and more particularly to an intelligent, real-time classroom management system that integrates computer vision-based occupancy detection, environmental sensor monitoring, timetable-aware scheduling, and automated control of classroom utilities through a web-based interface.

---

**Background of the Invention**

Conventional classroom environments rely on manual operation of utilities such as lighting, fans, and air conditioning systems. This results in significant energy wastage, particularly when classrooms are unoccupied or when environmental conditions do not warrant the use of such utilities. Existing building automation systems lack the contextual intelligence to correlate classroom occupancy with scheduled academic activities, environmental comfort levels, and real-time sensor data simultaneously.

There exists a need for an integrated, intelligent system that can:

1. Automatically detect the number of occupants in a classroom using computer vision.
2. Monitor real-time environmental parameters such as temperature and ambient noise.
3. Correlate occupancy data with academic timetable schedules.
4. Compute a composite comfort score and make automated utility control decisions.
5. Present all data through a live, remotely accessible web dashboard.

The present invention addresses these limitations by providing a unified software-hardware system that operates autonomously in real time.

---

**Summary of the Invention**

The invention is an Intelligent Real-Time Classroom Automation System comprising a Flask-based web server, a computer vision pipeline using YOLOv8 for person detection, a multi-module software architecture for comfort scoring, attendance estimation, predictive analysis, and automated device orchestration, all coordinated through a shared global state and presented via a live web dashboard.

The system continuously monitors the classroom environment, makes intelligent decisions about utility control, and provides real-time visibility to administrators or faculty through any web browser.

---

**Detailed Description of the Invention**

### 1. System Architecture Overview

The system is composed of the following interconnected software modules running on a central computing unit (e.g., a laptop, Raspberry Pi, or server):

```
[IP Camera / Mobile Camera]
          |
          v
[Flask Web Server — app.py]
          |
    ______|______
   |             |
[Video Feed]  [Data API]
              |
    __________|___________
   |          |           |
[Realtime  [Comfort   [Orchestration
 Engine]    Engine]    Engine]
   |          |           |
[Sensors] [Prediction] [Attendance
           Engine]      Engine]
              |
         [State Store]
              |
         [Dashboard UI]
```

All modules communicate through a centralized shared state dictionary (`state.py`), ensuring loose coupling and real-time consistency across the system.

---

### 2. Core Components

#### 2.1 Central State Store (`state.py`)

A shared in-memory dictionary that holds the live state of the entire system:

- `people` — current detected occupant count
- `comfort` — computed comfort score (0–100)
- `context` — environmental readings (temperature in °C, noise in dB)
- `actions` — current device states (lights, fan, AC, mode)
- `timetable` — active class schedule (subject, type, start time, end time)
- `camera_online` — boolean indicating camera connectivity status

This centralized state enables all modules to read and write data without direct inter-module dependencies.

---

#### 2.2 Web Application Server (`app.py`)

Built on the Flask micro-framework, the server exposes the following HTTP endpoints:

| Endpoint | Method | Function |
|---|---|---|
| `/` | GET | Renders the real-time HTML dashboard |
| `/data` | GET | Returns current system state as a JSON API response |
| `/video_feed` | GET | Streams live MJPEG video from the IP camera |
| `/upload` | POST | Accepts timetable image uploads for OCR processing |

The server spawns a background daemon thread running the `realtime_loop` to continuously update system state independent of HTTP request cycles.

The video streaming subsystem connects to an IP camera (e.g., a mobile phone running an IP Webcam application) via HTTP, reads frames using OpenCV, and streams them to the dashboard using multipart MJPEG encoding. The system automatically detects camera disconnection and reconnects without requiring a server restart.

---

#### 2.3 Real-Time Processing Engine (`realtime_engine.py`)

A continuously running background loop (polling interval: 3 seconds) that:

1. Reads the current system time.
2. Checks whether the current time falls within a scheduled class period.
3. Updates the timetable state (subject name, class type) accordingly.
4. Updates occupancy count based on detection results.
5. Triggers automated device control decisions based on occupancy.

This engine is the heartbeat of the system, ensuring all state data remains current without requiring user interaction.

---

#### 2.4 Comfort Scoring Engine (`comfort_engine.py`)

Computes a composite comfort index (0–100) using the following formula:

```
comfort_score = 100
              - |temperature - 25| × 2     (temperature deviation penalty)
              - noise_level                 (ambient noise penalty)
              - people_count × 1.5         (crowding penalty)
```

- Optimal temperature is defined as 25°C; deviations in either direction reduce comfort.
- Higher noise levels directly reduce the comfort score.
- Larger occupancy increases heat and reduces perceived comfort.
- The score is clamped to a minimum of 0.

---

#### 2.5 Orchestration Engine (`orchestration_engine.py`)

Makes automated binary control decisions for classroom utilities based on occupancy and comfort score:

| Condition | Lights | Fan | AC | Mode |
|---|---|---|---|---|
| No occupants (people = 0) | OFF | OFF | OFF | Idle |
| Occupants present, comfort ≥ 75 | ON | OFF | OFF | Normal |
| Occupants present, comfort < 75 | ON | ON | OFF | Normal |
| Occupants present, comfort < 60 | ON | ON | ON | Normal |

This tiered control logic ensures energy is consumed only when necessary and proportional to environmental discomfort.

---

#### 2.6 Attendance Estimation Engine (`attendance_engine.py`)

Estimates the number of students present by subtracting the instructor from the total detected occupant count:

```
attendance = max(people_detected - 1, 0)
```

Returns 0 when no class is scheduled. This provides a non-intrusive, camera-based attendance proxy without requiring biometric identification.

---

#### 2.7 Predictive Analysis Engine (`prediction_engine.py`)

Forecasts near-future temperature rise based on current occupancy:

```
predicted_temperature = current_temperature + (people_count × 0.05)
```

If the predicted temperature exceeds 30°C, the system generates an early warning: *"Overheating in 10 mins"*. This enables proactive cooling before discomfort occurs.

---

#### 2.8 Sensor Interface (`sensors.py`)

Reads environmental data and updates the shared state:

- Temperature (°C) — currently simulated; designed to interface with physical sensors (e.g., DHT22, DS18B20).
- Noise level (dB) — currently simulated; designed to interface with sound level sensors.
- Comfort score is recomputed on each sensor read cycle.

The modular design allows physical sensor integration by replacing the simulation logic with hardware I/O calls without modifying any other module.

---

#### 2.9 Person Detection Module (`person_detector.py`)

Interfaces with the YOLOv8 object detection model (`yolov8n.pt`) to count the number of persons visible in the camera frame. The detected count is written directly to the shared state. The module is designed to be called on each video frame or at a configurable interval.

YOLOv8 (You Only Look Once, version 8) is a state-of-the-art real-time object detection neural network. The nano variant (`yolov8n.pt`) is used for low-latency inference suitable for edge deployment.

---

#### 2.10 Timetable Engine (`timetable_engine.py`)

Loads the academic schedule into the shared state. The system is designed to support:

- Manual schedule entry (current implementation).
- OCR-based automatic extraction from uploaded timetable images using Pytesseract (planned integration via the `/upload` endpoint).

The timetable defines class start time, end time, subject name, and class type (lecture, lab, theory, etc.).

---

#### 2.11 Learning Engine (`learning_engine.py`)

A placeholder module for future adaptive learning capabilities. Intended to analyze historical comfort and occupancy patterns to proactively adjust device control thresholds over time, reducing reliance on fixed rule-based logic.

---

### 3. Web Dashboard (`templates/dashboard.html`)

A browser-based real-time monitoring interface that auto-refreshes every 3 seconds via JavaScript polling of the `/data` API. Displays:

- Current subject and class type
- Live student count
- Temperature and noise readings
- Comfort score
- Device status (lights, fan, AC, operating mode)
- Live camera feed with fullscreen capability
- Camera offline indicator

The dashboard requires no plugins or frameworks — it runs in any modern web browser and is accessible over the local network.

---

### 4. Data Flow

```
Camera Frame
    → OpenCV Capture
    → YOLOv8 Person Detection
    → state["people"] updated

Sensor Read (every 3s)
    → Temperature, Noise values
    → comfort_engine computes score
    → state["comfort"] updated

Realtime Loop (every 3s)
    → Timetable check
    → Occupancy check
    → orchestration_engine decides actions
    → state["actions"] updated

Dashboard (every 3s)
    → Fetches /data API
    → Renders all state values live
```

---

### 5. Claims of Novelty

The following aspects of the invention are claimed as novel:

1. **Timetable-Aware Automation:** The system correlates real-time occupancy with academic schedule data to distinguish between occupied and scheduled-empty states, enabling context-aware device control beyond simple motion detection.

2. **Multi-Factor Comfort Scoring:** A composite comfort index computed from temperature deviation, ambient noise, and occupancy density, used as the primary input for tiered utility control decisions.

3. **Predictive Thermal Warning:** A lightweight predictive model that forecasts classroom temperature rise based on current occupancy, enabling proactive cooling before discomfort thresholds are reached.

4. **Non-Intrusive Attendance Estimation:** Camera-based headcount using computer vision as a proxy for attendance, without requiring biometric data, RFID, or student interaction.

5. **Unified Modular State Architecture:** A centralized shared state store enabling independent, loosely coupled modules to collaborate in real time without direct inter-module communication.

6. **Integrated Live Streaming with Automation:** Simultaneous live video streaming and automated environmental control from a single IP camera source, with automatic reconnection on camera failure.

---

### 6. Advantages Over Prior Art

- Eliminates manual utility operation, reducing human error and energy waste.
- Operates without student interaction or biometric data collection.
- Deployable on low-cost hardware (laptop, Raspberry Pi).
- Accessible remotely via any web browser on the local network.
- Modular architecture allows incremental hardware integration (real sensors, real actuators) without system redesign.
- Timetable awareness prevents false positives (e.g., a single person in an empty classroom triggering full classroom mode).

---

### 7. Dependencies and Environment

| Dependency | Purpose |
|---|---|
| Flask | Web server and HTTP routing |
| OpenCV (opencv-python) | Camera capture and video streaming |
| Ultralytics YOLOv8 | Real-time person detection |
| Pytesseract | OCR for timetable image parsing |
| Pillow | Image processing support |
| NumPy | Numerical computation |
| Python 3.11 | Runtime environment |

---

### 8. Deployment

The system runs on a single machine connected to the same local network as the IP camera. The web dashboard is accessible to any device on the network via:

```
http://<server-ip>:5000
```

No cloud dependency. No external API calls. Fully self-contained local deployment.

---

**Abstract**

An intelligent classroom automation system that integrates real-time computer vision-based occupancy detection, environmental sensor monitoring, academic timetable scheduling, and automated utility control into a unified web-accessible platform. The system employs a YOLOv8 neural network for non-intrusive person counting, computes a multi-factor comfort score from temperature, noise, and occupancy data, and applies tiered rule-based logic to autonomously control classroom lighting, ventilation, and air conditioning. A predictive engine forecasts thermal conditions to enable proactive cooling. All data is presented through a live web dashboard with integrated IP camera streaming. The modular architecture supports incremental hardware integration and operates entirely on local infrastructure without cloud dependency.

---

*Document prepared for patent submission purposes.*
*All module names, algorithms, and system architecture described herein are original works of the inventor(s).*
