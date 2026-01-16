from baseline.learner import compute_baseline

def detect_attack(current_window_count):
    baseline = compute_baseline()

    # 🔥 instant protection
    if current_window_count > 100:
        return "ATTACK"

    if not baseline:
        return "LEARNING"

    mean = baseline["mean"]
    std = baseline["std"]

    if current_window_count > mean + 2 * std:
        return "ATTACK"
    elif current_window_count > mean + 1 * std:
        return "SUSPICIOUS"
    else:
        return "NORMAL"

