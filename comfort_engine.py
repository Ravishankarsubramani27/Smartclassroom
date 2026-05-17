def comfort_score(ctx):
    score = 100
    score -= abs(ctx["temperature"] - 25) * 2
    score -= ctx["noise"]
    score -= ctx["people"] * 1.5
    return max(int(score), 0)
