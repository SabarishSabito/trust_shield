def analyze_network(platform: str, followers: int, following: int, mutuals: int = 0) -> dict:
    risk = 0.0
    flags = []

    f_cnt = max(int(followers), 0)
    fg_cnt = max(int(following), 0)
    m_cnt = max(int(mutuals), 0)
    safe_fg = max(fg_cnt, 1)
    ratio = f_cnt / safe_fg

    plat = platform.lower()

    # Genuine high-follower or balanced organic thresholds (0% Risk)
    if f_cnt >= 1000 and ratio >= 0.8:
        return {"score": 0.0, "flags": [f"High-authority authentic {platform} network topology"]}

    if f_cnt >= 100 and ratio >= 0.3:
        return {"score": 0.0, "flags": [f"Balanced organic {platform} connection distribution"]}

    # Platform Specific Anomalies
    if plat == "linkedin":
        if fg_cnt > 500 and f_cnt < 30 and m_cnt == 0:
            risk += 0.70
            flags.append("Sybil connection harvesting: high outbound requests with 0 mutual connections")
        elif ratio < 0.1 and fg_cnt > 300:
            risk += 0.40
            flags.append(f"Unbalanced professional network (Connections: {f_cnt} vs Outbound: {fg_cnt})")

    elif plat == "twitter":
        if fg_cnt > 800 and ratio < 0.05:
            risk += 0.80
            flags.append(f"Automated follow-churn bot pattern (Following: {fg_cnt} vs Followers: {f_cnt})")
        elif fg_cnt > 2000 and f_cnt < 100:
            risk += 0.90
            flags.append("Mass follow-farming infrastructure anomaly")

    elif plat == "facebook":
        if fg_cnt > 600 and m_cnt == 0 and f_cnt < 25:
            risk += 0.65
            flags.append("Isolated cluster topology: 0 mutual friends across active network")

    else:  # Instagram
        if fg_cnt > 750 and ratio < 0.04:
            risk += 0.75
            flags.append(f"Severe follow-churn ratio: following {fg_cnt} accounts with {f_cnt} followers")
        elif fg_cnt > 350 and ratio < 0.1:
            risk += 0.35
            flags.append(f"Asymmetric follower acquisition ratio ({ratio:.3f})")

    if not flags:
        flags.append("Natural organic network connectivity")

    score = round(min(1.0, max(0.0, risk)), 3)
    return {"score": score, "flags": flags}