SPAM_CORPUS = [
    "crypto", "giveaway", "free money", "dm for promo", "invest", 
    "telegram", "earn daily", "link in bio", "whatsapp", "forex",
    "airdrop", "presale", "double your cash", "t.me"
]

ENSEMBLE_WEIGHTS = {
    "behavioral": 0.30,
    "linguistic": 0.25,
    "image": 0.25,
    "network": 0.20
}

RISK_TIERS = {
    "LIKELY_FAKE": 0.65,
    "SUSPICIOUS": 0.35,
    "GENUINE": 0.00
}