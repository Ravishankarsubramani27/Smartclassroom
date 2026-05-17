from datetime import time
from state import state

def load_timetable():
    state["timetable"] = {
        "start": time(17, 0),   # 5 PM
        "end": time(19, 0),     # 7 PM
        "subject": "AI Systems",
        "type": "theory"
    }
