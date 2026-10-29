def compute_ensemble_verdict(behavioral: dict, linguistic: dict, vision: dict, network: dict) -> dict:
    b_score = float(behavioral.get("score", 0.0))
    l_score = float(linguistic.get("score", 0.0))
    v_score = float(vision.get("score", 0.0))
    n_score = float(network.get("score", 0.0))

    # Dynamic Weights: Network (35%), Linguistic (30%), Behavioral (25%), Vision (10%)
    weighted_score = (b_score * 0.25) + (l_score * 0.30) + (v_score * 0.10) + (n_score * 0.35)

    # Critical Escalation: If any individual pillar detects extreme bot traits (> 0.70), escalate
    max_pillar = max(b_score, l_score, v_score, n_score)
    if max_pillar >= 0.75:
        weighted_score = max(weighted_score, max_pillar * 0.85)

    prob_pct = round(min(100.0, max(0.0, weighted_score * 100.0)), 1)

    # Verdict Classification
    if prob_pct <= 20.0:
        classification = "Genuine"
    elif prob_pct <= 55.0:
        classification = "Suspicious"
    else:
        classification = "Likely Fake"

    # Aggregate Threat Flags
    all_flags = []
    for vector in [behavioral, linguistic, vision, network]:
        for flag in vector.get("flags", []):
            if flag and not any(good in flag.lower() for good in ["verified", "authentic", "organic", "natural"]):
                all_flags.append(flag)

    if not all_flags:
        all_flags = ["All multi-modal verification vectors cleared within normal organic limits."]

    return {
        "probability_score": prob_pct,
        "classification": classification,
        "breakdown": {
            "behavioral": round(b_score * 100, 1),
            "linguistic": round(l_score * 100, 1),
            "vision": round(v_score * 100, 1),
            "network": round(n_score * 100, 1)
        },
        "flags": all_flags
    }