import re
from playwright.async_api import async_playwright

def _parse_shorthand(val_str: str) -> int:
    """Parses numeric abbreviations like 271M, 12.5k, 1,400 to plain integers."""
    if not val_str:
        return 0
    clean = val_str.upper().replace(',', '').strip()
    try:
        if 'M' in clean:
            return int(float(clean.replace('M', '')) * 1_000_000)
        if 'K' in clean:
            return int(float(clean.replace('K', '')) * 1_000)
        return int(float(clean))
    except (ValueError, TypeError):
        return 0

def clean_instagram_target(raw_input: str) -> str:
    """Strips full URLs, query parameters (?hl=en, ?igsh=...), and leading @ symbols."""
    text = raw_input.strip()
    # Strip URL prefix
    text = re.sub(r'^(https?://)?(www\.)?instagram\.com/', '', text, flags=re.IGNORECASE)
    # Strip query parameters and trailing slash
    text = text.split('?')[0].split('&')[0].strip('/')
    # Strip @
    text = text.lstrip('@')
    # Match valid username syntax
    match = re.search(r'^[a-zA-Z0-9._]+', text)
    return match.group(0).lower() if match else text.lower()

async def fetch_real_instagram_profile(raw_target: str) -> dict:
    username = clean_instagram_target(raw_target)
    target_url = f"https://www.instagram.com/{username}/"

    result = {
        "username": username,
        "full_name": "",
        "is_verified": False,
        "has_profile_pic": False,
        "bio": "",
        "posts_count": 0,
        "followers_count": 0,
        "following_count": 0,
        "ratio": 0.0,
        "success": False,
        "error": None
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use a realistic desktop browser context
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = await context.new_page()

        # Intercept backend GraphQL / user info responses
        async def on_response(response):
            if "/api/v1/users/web_profile_info/" in response.url:
                try:
                    payload = await response.json()
                    user = payload.get("data", {}).get("user", {})
                    if user:
                        result["full_name"] = user.get("full_name", "")
                        result["is_verified"] = user.get("is_verified", False)
                        result["has_profile_pic"] = not user.get("has_anonymous_profile_picture", True)
                        result["bio"] = user.get("biography", "")
                        result["posts_count"] = user.get("edge_owner_to_timeline_media", {}).get("count", 0)
                        result["followers_count"] = user.get("edge_followed_by", {}).get("count", 0)
                        result["following_count"] = user.get("edge_follow", {}).get("count", 0)
                        result["success"] = True
                except Exception:
                    pass

        page.on("response", on_response)

        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=25000)
            await page.wait_for_timeout(3500)  # Allow dynamic page scripts to render

            # Fallback 1: Parse meta tags if API response was bypassed
            if not result["success"]:
                content = await page.content()
                
                # Title often contains: "Name (@username) • Instagram photos and videos"
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                if title_match:
                    raw_title = title_match.group(1)
                    if "•" in raw_title:
                        result["full_name"] = raw_title.split("(")[0].strip()

                # Meta description contains: "123M Followers, 450 Following, 1,200 Posts"
                desc_match = re.search(r'<meta content="([^"]+)" name="description"', content)
                if desc_match:
                    desc_text = desc_match.group(1)
                    f_match = re.search(r'([\d\.,]+[KkMm]?)\s*Followers', desc_text, re.IGNORECASE)
                    fg_match = re.search(r'([\d\.,]+[KkMm]?)\s*Following', desc_text, re.IGNORECASE)
                    p_match = re.search(r'([\d\.,]+[KkMm]?)\s*Posts', desc_text, re.IGNORECASE)

                    if f_match:
                        result["followers_count"] = _parse_shorthand(f_match.group(1))
                    if fg_match:
                        result["following_count"] = _parse_shorthand(fg_match.group(1))
                    if p_match:
                        result["posts_count"] = _parse_shorthand(p_match.group(1))

                    result["is_verified"] = bool(re.search(r'Verified|aria-label="Verified"', content, re.IGNORECASE))
                    result["has_profile_pic"] = True
                    if result["followers_count"] > 0 or result["posts_count"] > 0:
                        result["success"] = True

        except Exception as ex:
            result["error"] = str(ex)
        finally:
            await browser.close()

    # Calculate follower-to-following ratio
    following = max(result["following_count"], 1)
    result["ratio"] = round(result["followers_count"] / following, 4)
    return result