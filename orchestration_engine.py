def decide_actions(ctx, comfort):
    if ctx["people"] == 0:
        return {"lights":"OFF","fan":"OFF","ac":"OFF","mode":"Idle"}

    return {
        "lights":"ON",
        "fan":"ON" if comfort < 75 else "OFF",
        "ac":"ON" if comfort < 60 else "OFF",
        "mode":"Normal"
    }
