import re
from app.config import SPAM_CORPUS

def analyze_linguistics(bio: str, username: str = "") -> dict:
    risk = 0.0
    flags = []
    
    clean_bio = (bio or "").lower()
    clean_user = (username or "").lower().replace("@", "")

    # 1. Bot handle patterns: trailing 4+ random digits or bot keywords
    if re.search(r"\d{5,}$", clean_user):
        risk += 0.35
        flags.append("Algorithmic handle detected: excessive numeric sequence")
    if re.search(r"(promo|airdrop|giveaway|hack|deals|freecrypto|claim_bot)", clean_user):
        risk += 0.40
        flags.append("Username contains high-risk promotional keyword tokens")

    # 2. Bio spam corpus keyword matching
    matched = [kw for kw in SPAM_CORPUS if kw in clean_bio]
    if matched:
        keyword_risk = min(0.60, len(matched) * 0.25)
        risk += keyword_risk
        flags.append(f"Spam linguistic markers matched: {', '.join(matched)}")

    # 3. Dangerous off-platform redirection links
    if re.search(r"(t\.me/|wa\.me/|bit\.ly/|linktr\.ee/|whatsapp)", clean_bio):
        risk += 0.30
        flags.append("External unverified off-platform redirection link in bio")

    if not flags:
        flags.append("Authentic linguistic structure: No spam markers detected")

    # Clean zero-floor
    score = round(min(1.0, max(0.0, risk)), 3)
    return {"score": score, "flags": flags}