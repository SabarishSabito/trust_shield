import re
from fastapi import APIRouter, Form, HTTPException
from app.db.memory import USERS_DB

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    clean_email = email.strip().lower()
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", clean_email):
        raise HTTPException(status_code=400, detail="Invalid corporate moderator email address")
    if len(password) < 6:
        raise HTTPException(status_code=401, detail="Authentication token must have at least 6 characters")
    
    user_info = USERS_DB.get(clean_email, {"role": "Investigator", "name": clean_email.split("@")[0].title()})
    return {"status": "authenticated", "email": clean_email, "profile": user_info}