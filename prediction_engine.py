def predict_next(ctx):
    future_temp = ctx["temperature"] + ctx["people"] * 0.05
    return {
        "predicted_temp": round(future_temp, 1),
        "message": "Overheating in 10 mins" if future_temp > 30 else "Normal"
    }
