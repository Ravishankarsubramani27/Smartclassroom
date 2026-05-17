def estimate_attendance(subject, people):
    if subject == "No Class":
        return 0
    return max(people - 1, 0)
