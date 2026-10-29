import re
import urllib.parse
from typing import Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup

PLATFORM_PATTERNS = {
    "Instagram": r"(?:https?:\/\/)?(?:www\.)?instagram\.com\/([A-Za-z0-9_\.]{1,30})",
    "Twitter": r"(?:https?:\/\/)?(?:www\.)?(?:twitter\.com|x\.com)\/([A-Za-z0-9_]{1,15})",
    "LinkedIn": r"(?:https?:\/\/)?(?:[a-z]{2,3}\.)?linkedin\.com\/in\/([A-Za-z0-9\-_%]+)",
    "Facebook": r"(?:https?:\/\/)?(?:www\.)?facebook\.com\/([A-Za-z0-9\.]+)",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

def identify_platform_and_handle(input_url: str) -> tuple[Optional[str], Optional[str]]:
    """Identifies the social platform and extracts the raw handle from a URL or raw username."""
    clean_input = input_url.strip()

    for platform, pattern in PLATFORM_PATTERNS.items():
        match = re.search(pattern, clean_input, re.IGNORECASE)
        if match:
            return platform, match.group(1).rstrip("/")

    # Fallback if raw username is provided (e.g., @handle)
    if clean_input.startswith("@"):
        return "Instagram", clean_input.replace("@", "")

    return None, None

async def resolve_profile_metadata(target: str) -> Dict[str, Any]:
    """
    Validates account existence and extracts public OpenGraph metadata
    (profile image, title/name, public bio snippet).
    """
    platform, handle = identify_platform_and_handle(target)
    
    if not platform or not handle:
        return {
            "valid": False,
            "error": "Unrecognized social profile URL or invalid handle format."
        }

    # Normalize profile URL
    url_map = {
        "Instagram": f"https://www.instagram.com/{handle}/",
        "Twitter": f"https://x.com/{handle}",
        "LinkedIn": f"https://www.linkedin.com/in/{handle}/",
        "Facebook": f"https://www.facebook.com/{handle}",
    }
    target_url = url_map[platform]

    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, headers=HEADERS) as client:
        try:
            response = await client.get(target_url)
        except Exception as e:
            return {
                "valid": False,
                "platform": platform,
                "username": f"@{handle}",
                "error": f"Connection to {platform} failed: {str(e)}"
            }

    # 404 or specific redirection typically marks non-existent targets
    if response.status_code == 404:
        return {
            "valid": False,
            "platform": platform,
            "username": f"@{handle}",
            "error": f"Profile does not exist on {platform} (HTTP 404)."
        }

    soup = BeautifulSoup(response.text, "html.parser")

    def get_meta(prop_name: str) -> Optional[str]:
        tag = soup.find("meta", property=prop_name) or soup.find("meta", attrs={"name": prop_name})
        return tag["content"] if tag and tag.has_attr("content") else None

    # Extract OpenGraph Tags
    og_title = get_meta("og:title") or handle
    og_description = get_meta("og:description") or "Public profile data verified via web request."
    og_image = get_meta("og:image") or ""

    # Parse follower/following heuristics if present in description
    followers = 0
    following = 0
    posts = 0

    num_match = re.search(r"([\d\.,]+[km]?)\s+Followers", og_description, re.IGNORECASE)
    if num_match:
        followers = _parse_metric(num_match.group(1))

    return {
        "valid": True,
        "platform": platform,
        "username": f"@{handle}",
        "display_name": og_title.split("•")[0].strip(),
        "bio": og_description,
        "avatar_url": og_image,
        "followers": followers,
        "following": following,
        "posts": posts,
        "source_url": target_url
    }

def _parse_metric(raw_str: str) -> int:
    val = raw_str.replace(",", "").strip().lower()
    try:
        if val.endswith("k"):
            return int(float(val[:-1]) * 1000)
        if val.endswith("m"):
            return int(float(val[:-1]) * 1_000_000)
        return int(float(val))
    except Exception:
        return 0