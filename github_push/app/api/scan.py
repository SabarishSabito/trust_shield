import os
import sys
import re
import io
import time
import math
import hashlib
from typing import Optional, List, Dict, Any, Tuple
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Scan"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR if os.path.exists(TEMPLATES_DIR) else "templates")

SCAN_HISTORY_LOG: List[Dict[str, Any]] = []

# Bind Tesseract OCR Path for Windows
try:
    import pytesseract
    tesseract_candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"),
    ]
    for p in tesseract_candidates:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            print(f"[TrustShield OCR] Bound Tesseract OCR: {p}")
            break
except Exception as e:
    print(f"[TrustShield OCR Init Notice]: {e}")

def extract_clean_username_and_platform(raw_input: str) -> Tuple[str, str]:
    if not raw_input:
        return "instagram", "anonymous_user"
    
    text = str(raw_input).strip()
    platform = "instagram"
    text_lower = text.lower()
    
    if "twitter.com" in text_lower or "x.com" in text_lower:
        platform = "twitter"
    elif "linkedin.com" in text_lower:
        platform = "linkedin"
    elif "facebook.com" in text_lower or "fb.com" in text_lower:
        platform = "facebook"
        
    clean = re.sub(r'^https?://(www\.)?', '', text, flags=re.IGNORECASE)
    clean = re.sub(r'^(instagram\.com|x\.com|twitter\.com|linkedin\.com/in|facebook\.com)/', '', clean, flags=re.IGNORECASE)
    clean = clean.split('?')[0].split('#')[0].strip('/')
    clean = clean.replace('@', '')
    
    parts = [p for p in clean.split('/') if p]
    if parts:
        clean = parts[-1]
        
    return platform, clean if clean else "target_user"

from app.core.ocr_engine import (
    extract_ocr_from_image,
    parse_screenshot_forensics,
    evaluate_forensic_profile,
    calculate_shannon_entropy
)

def dynamic_forensic_algorithm(username: str, platform: str, custom_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    posts = custom_metrics.get("posts_count", 12) if custom_metrics else 12
    followers = custom_metrics.get("followers_count", 350) if custom_metrics else 350
    following = custom_metrics.get("following_count", 210) if custom_metrics else 210
    is_verified = custom_metrics.get("is_verified", False) if custom_metrics else False
    mutual_count = custom_metrics.get("mutual_count", 0) if custom_metrics else 0
    bio = custom_metrics.get("bio", "") if custom_metrics else ""
    full_text = custom_metrics.get("full_text", "") if custom_metrics else ""

    metrics = evaluate_forensic_profile(
        username=username,
        platform=platform,
        posts=posts,
        followers=followers,
        following=following,
        is_verified=is_verified,
        mutual_count=mutual_count,
        bio=bio,
        full_text=full_text
    )
    return {
        "safety_rating": metrics["safety_rating"],
        "risk_score": metrics["risk_score"],
        "behavioral": metrics["behavioral"],
        "linguistic": metrics["linguistic"],
        "vision": metrics["vision"],
        "network": metrics["network"],
        "verdict": metrics["verdict"],
        "rationale": metrics["verdict_rationale"]
    }

# --- PAGE ROUTES ---

@router.get("/scan/url", response_class=HTMLResponse)
@router.get("/scan-url", response_class=HTMLResponse)
async def serve_url_scan_page(request: Request):
    return templates.TemplateResponse(request=request, name="scan_url.html")

@router.get("/scan/photo", response_class=HTMLResponse)
@router.get("/scan-photo", response_class=HTMLResponse)
async def serve_photo_scan_page(request: Request):
    return templates.TemplateResponse(request=request, name="scan_photo.html")

@router.get("/api/history")
async def get_scan_history():
    return JSONResponse(content=SCAN_HISTORY_LOG[:50])

# --- API AUDIT ROUTES ---

@router.post("/api/scan-url")
@router.post("/scan-url")
async def scan_profile_url(request: Request):
    raw_target = None
    try:
        body = await request.json()
        if isinstance(body, dict):
            for k in ["target", "url", "target_url", "username", "account", "link"]:
                if body.get(k):
                    raw_target = str(body[k]).strip()
                    break
    except Exception:
        pass
        
    if not raw_target:
        try:
            form = await request.form()
            for k in ["target", "url", "target_url", "username", "account", "link"]:
                if form.get(k):
                    raw_target = str(form[k]).strip()
                    break
        except Exception:
            pass

    if not raw_target:
        for k in ["target", "url", "target_url", "username"]:
            if request.query_params.get(k):
                raw_target = str(request.query_params.get(k)).strip()
                break

    platform, username = extract_clean_username_and_platform(raw_target or "pcdoc_nanda")
    metrics = dynamic_forensic_algorithm(username, platform)
    audit_id = f"TS-{int(time.time()) % 100000:05d}"
    
    payload = {
        "status": "success",
        "audit_id": audit_id,
        "auditId": audit_id,
        "username": username,
        "target": username,
        "platform": platform.upper(),
        "safety_rating": metrics["safety_rating"],
        "safetyRating": metrics["safety_rating"],
        "safety": metrics["safety_rating"],
        "risk_score": metrics["risk_score"],
        "riskScore": metrics["risk_score"],
        "verdict": metrics["verdict"],
        "verdict_rationale": metrics["rationale"],
        "verdictRationale": metrics["rationale"],
        "behavioral_velocity": metrics["behavioral"],
        "behavioral": metrics["behavioral"],
        "linguistic_nlp": metrics["linguistic"],
        "linguistic": metrics["linguistic"],
        "vision_verified": metrics["vision"],
        "vision": metrics["vision"],
        "network_risk": metrics["network"],
        "network": metrics["network"],
        "timestamp": int(time.time())
    }
    SCAN_HISTORY_LOG.insert(0, payload)
    return JSONResponse(status_code=200, content=payload)

@router.post("/api/scan-photo")
@router.post("/scan-photo")
async def scan_profile_photo(file: Optional[UploadFile] = File(None), request: Request = None):
    upload = file
    if not upload and request:
        try:
            form = await request.form()
            for v in form.values():
                if isinstance(v, UploadFile):
                    upload = v
                    break
        except Exception:
            pass

    filename = upload.filename if upload and upload.filename else "screenshot.png"
    image_bytes = b""
    if upload:
        try:
            image_bytes = await upload.read()
            # Also persist in static/uploads for visual reference/history
            uploads_dir = os.path.join(ROOT_DIR, "static", "uploads")
            if os.path.exists(uploads_dir) and len(image_bytes) > 0:
                safe_name = f"scan_{int(time.time()) % 100000}_{filename.replace(' ', '_')}"
                with open(os.path.join(uploads_dir, safe_name), "wb") as f:
                    f.write(image_bytes)
        except Exception as e:
            print(f"[TrustShield Photo Read Notice]: {e}")

    # 1. Native Windows OCR with pytesseract fallback
    extracted_text, lines = extract_ocr_from_image(image_bytes, filename)
    print(f"[TrustShield OCR Output ({len(extracted_text)} chars)]:\n{extracted_text[:200]}...")

    # 2. Forensic parameter parsing
    parsed = parse_screenshot_forensics(extracted_text, lines, filename)
    username = parsed["username"]
    platform = parsed["platform"]
    posts = parsed["posts"]
    followers = parsed["followers"]
    following = parsed["following"]
    is_verified = parsed["is_verified"]
    mutual_count = parsed.get("mutual_count", 0)
    bio = parsed.get("bio", "")
    full_text = parsed.get("full_text", "")

    # 3. Calibrated multi-signal evaluation
    metrics = evaluate_forensic_profile(
        username=username,
        platform=platform,
        posts=posts,
        followers=followers,
        following=following,
        is_verified=is_verified,
        mutual_count=mutual_count,
        bio=bio,
        full_text=full_text
    )
    audit_id = f"TS-{int(time.time()) % 100000:05d}"
    
    payload = {
        "status": "success",
        "audit_id": audit_id,
        "auditId": audit_id,
        "username": username,
        "target": username,
        "platform": platform.upper(),
        "safety_rating": metrics["safety_rating"],
        "safetyRating": metrics["safety_rating"],
        "safety": metrics["safety_rating"],
        "risk_score": metrics["risk_score"],
        "riskScore": metrics["risk_score"],
        "verdict": metrics["verdict"],
        "verdict_rationale": metrics["verdict_rationale"],
        "verdictRationale": metrics["verdict_rationale"],
        "behavioral_velocity": metrics["behavioral"],
        "behavioral": metrics["behavioral"],
        "linguistic_nlp": metrics["linguistic"],
        "linguistic": metrics["linguistic"],
        "vision_verified": metrics["vision"],
        "vision": metrics["vision"],
        "network_risk": metrics["network"],
        "network": metrics["network"],
        "posts_detected": posts,
        "followers_detected": followers,
        "following_detected": following,
        "timestamp": int(time.time())
    }
    
    SCAN_HISTORY_LOG.insert(0, payload)
    return JSONResponse(status_code=200, content=payload)
    
    SCAN_HISTORY_LOG.insert(0, payload)
    return JSONResponse(status_code=200, content=payload)