import time
from datetime import datetime
from state import state

def realtime_loop():
    while True:
        now = datetime.now().time()

        if now.hour >= 9 and now.hour <= 11:
            state["timetable"]["start"] = now.replace(hour=9, minute=0)
            state["timetable"]["end"] = now.replace(hour=11, minute=0)
            state["timetable"]["subject"] = "AI"
            state["timetable"]["type"] = "lecture"
            state["people"] = 5
        else:
            state["people"] = 0

        if state["people"] > 0:
            state["actions"]["lights"] = "ON"
            state["actions"]["fan"] = "ON"
            state["actions"]["ac"] = "ON"
            state["actions"]["mode"] = "Normal"
        else:
            state["actions"]["lights"] = "OFF"
            state["actions"]["fan"] = "OFF"
            state["actions"]["ac"] = "OFF"
            state["actions"]["mode"] = "Idle"

        time.sleep(3)
