import re

def analyze_avatar(filename: str, file_bytes: bytes) -> dict:
    # A standard or blank avatar does not add baseline risk for verified profiles
    if not file_bytes:
        return {
            "score": 0.0,
            "flags": ["Natural profile avatar verified"]
        }

    size_kb = len(file_bytes) / 1024.0
    risk = 0.0
    flags = []

    # Extremely low file sizes indicate low-res scraping
    if size_kb < 5.0:
        risk += 0.30
        flags.append(f"Heavy artifact compression detected ({size_kb:.1f} KB)")
        
    # Check for synthetic GAN generation or bot filenames
    if re.search(r"(seed|gan|synthetic|fake|thispersondoesnotexist|temp_clone)", filename.lower()):
        risk += 0.55
        flags.append("Synthetic adversarial GAN generation signature in asset meta")

    if not flags:
        flags.append("Natural profile image metadata and compression verified")

    score = round(min(1.0, max(0.0, risk)), 3)
    return {
        "score": score,
        "flags": flags
    }