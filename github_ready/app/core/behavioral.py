def analyze_behavior(posts: int, age_days: int, msgs_per_hr: float, platform: str = "Instagram") -> dict:
    risk = 0.0
    flags = []

    safe_age = max(int(age_days), 1)
    posts_cnt = max(int(posts), 0)
    msg_rate = max(float(msgs_per_hr), 0.0)

    # 1. Posting Velocity
    posts_per_day = posts_cnt / safe_age

    if posts_per_day > 40:
        risk += 0.65
        flags.append(f"High-frequency automated posting anomaly: {posts_per_day:.1f} posts/day")
    elif posts_per_day > 15:
        risk += 0.25
        flags.append(f"Elevated publication velocity ({posts_per_day:.1f} posts/day)")

    # 2. Automated Messaging / DM Rates
    if msg_rate > 45:
        risk += 0.60
        flags.append(f"Scripted mass-DM cadence: {msg_rate:.1f} msgs/hr")
    elif msg_rate > 20:
        risk += 0.25
        flags.append(f"Above-average messaging velocity: {msg_rate:.1f} msgs/hr")

    # 3. Zero-engagement throwaway accounts
    if posts_cnt == 0 and safe_age > 120 and msg_rate > 10:
        risk += 0.45
        flags.append("Disposable account pattern: 0 public posts paired with active outbound messaging")

    if not flags:
        flags.append("Standard organic behavioral cadence verified")

    score = round(min(1.0, max(0.0, risk)), 3)
    return {"score": score, "flags": flags}