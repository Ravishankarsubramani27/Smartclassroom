import random
from state import state

def read_sensors():
    state["context"]["temperature"] = random.randint(26, 32)
    state["context"]["noise"] = random.randint(20, 60)
    state["comfort"] = max(0, 100 - abs(28 - state["context"]["temperature"]) * 5)
