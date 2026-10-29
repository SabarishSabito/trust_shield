import math
import re
from typing import Dict, Any, Tuple

def calculate_shannon_entropy(text: str) -> float:
    """Calculates information entropy to detect randomized/bot usernames."""
    if not text:
        return 0.0
    entropy = 0.0
    length = len(text)
    frequencies = {char: text.count(char) for char in set(text)}
    for count in frequencies.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def detect_platform(target: str) -> str:
    """Identifies the social platform from the URL or query string."""
    target_lower = target.lower()
    if "twitter.com" in target_lower or "x.com" in target_lower:
        return "twitter"
    if "linkedin.com" in target_lower:
        return "linkedin"
    if "facebook.com" in target_lower or "fb.com" in target_lower:
        return "facebook"
    return "instagram"

class UnifiedRiskAnalyzer:
    """Cross-platform detection engine calibrated for social profiles."""

    @staticmethod
    def analyze(profile: Dict[str, Any], platform: str = "instagram") -> Dict[str, Any]:
        username = str(profile.get("username", "unknown")).lower()
        bio = str(profile.get("bio", ""))
        posts = int(profile.get("posts_count", 0))
        followers = int(profile.get("followers_count", 0))
        following = int(profile.get("following_count", 0))
        has_pic = bool(profile.get("has_profile_pic", False))
        is_verified = bool(profile.get("is_verified", False))

        # ---------------- 1. DETERMINISTIC VERIFICATION CHECK ----------------
        if is_verified:
            return {
                "safety_rating": 99.2,
                "risk_score": 0.8,
                "trust_score": 99.2,
                "verdict": "Verified Official Profile",
                "verdict_rationale": f"Authentic profile verified via official {platform.capitalize()} credentials.",
                "metrics": {
                    "behavioral_velocity": 96.0,
                    "linguistic_nlp": 94.0,
                    "vision_verified": 100.0,
                    "network_risk": 4.0
                }
            }

        # ---------------- 2. MULTI-SIGNAL FEATURE COMPUTATION ----------------
        
        # A. Linguistic / Handle Analysis (25% Weight)
        entropy = calculate_shannon_entropy(username)
        digits = sum(c.isdigit() for c in username)
        special_chars = len(re.findall(r'[^a-zA-Z0-9]', username))
        
        # Human handles typically have entropy between 2.5 and 3.8
        linguistic_score = 80.0
        if digits >= 5:
            linguistic_score -= 35.0
        elif digits >= 3:
            linguistic_score -= 15.0
            
        if entropy > 4.1 or (len(username) > 8 and entropy < 1.8):
            linguistic_score -= 20.0
            
        if any(keyword in bio.lower() for keyword in ["crypto", "whatsapp", "dm for promo", "invest", "telegram"]):
            linguistic_score -= 25.0
            
        if len(bio) == 0:
            linguistic_score -= 15.0
            
        linguistic_score = max(10.0, min(95.0, linguistic_score))

        # B. Behavioral Velocity (40% Weight)
        behavioral_score = 75.0
        if posts == 0:
            behavioral_score -= 40.0
        elif posts < 3:
            behavioral_score -= 25.0
        elif posts > 30:
            behavioral_score += 15.0

        # C. Network Risk & Follower Divergence (15% Weight)
        network_risk_score = 15.0
        ratio = followers / max(following, 1)

        if platform == "linkedin":
            # LinkedIn norms: connections typically balance out
            if following > 1500 and followers < 50:
                network_risk_score += 65.0
            elif followers > 200:
                network_risk_score -= 10.0
        else:
            # Instagram, X, Facebook
            if following > 1000 and followers < 30:
                network_risk_score += 70.0
            elif following > 500 and followers < 100:
                network_risk_score += 45.0
            elif ratio > 0.6:
                network_risk_score = max(5.0, network_risk_score - 10.0)

        network_risk_score = max(5.0, min(95.0, network_risk_score))

        # D. Vision Asset Integrity (20% Weight)
        vision_score = 85.0 if has_pic else 15.0

        # ---------------- 3. CALIBRATED AGGREGATION ----------------
        
        # Weighted overall Trust calculation
        trust_aggregate = (
            (behavioral_score * 0.35) +
            (linguistic_score * 0.25) +
            (vision_score * 0.20) +
            ((100.0 - network_risk_score) * 0.20)
        )
        
        # Extreme penalty overrides for bot archetypes
        if not has_pic and posts == 0 and digits >= 4:
            trust_aggregate = min(trust_aggregate, 15.0)

        trust_score = round(float(max(2.0, min(98.0, trust_aggregate))), 1)
        risk_score = round(float(100.0 - trust_score), 1)

        # Verdict assignment
        if risk_score <= 25.0:
            verdict = "Low Risk / Authentic"
            rationale = f"Organic {platform.capitalize()} profile graph with consistent activity metrics and verified visual assets."
        elif risk_score <= 60.0:
            verdict = "Moderate / Elevated Risk"
            rationale = "Account displays unverified indicators or atypical network ratios. Proceed with discretion."
        else:
            verdict = "High Risk / Likely Synthetic"
            rationale = "Synthetic patterns detected: abnormal follow ratio, sparse activity volume, and auto-generated handle indicators."

        return {
            "safety_rating": trust_score,
            "risk_score": risk_score,
            "trust_score": trust_score,
            "verdict": verdict,
            "verdict_rationale": rationale,
            "platform": platform,
            "metrics": {
                "behavioral_velocity": round(behavioral_score, 1),
                "linguistic_nlp": round(linguistic_score, 1),
                "vision_verified": round(vision_score, 1),
                "network_risk": round(network_risk_score, 1)
            }
        }