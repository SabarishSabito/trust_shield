import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

# Ensure root and app directories are in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # app/
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Database initialization - type: ignore suppresses Pylance resolution warnings
DATABASE_READY = False
engine = None
Base = None

try:
    from db.database import engine, Base  # type: ignore
    DATABASE_READY = True
except Exception:
    try:
        from app.db.database import engine, Base  # type: ignore
        DATABASE_READY = True
    except Exception:
        DATABASE_READY = False

# Import modular API routers
from app.api.scan import router as scan_router  # type: ignore

try:
    from app.api.auth import router as auth_router  # type: ignore
except Exception:
    auth_router = None

STATIC_DIR = os.path.join(ROOT_DIR, "static")
TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if DATABASE_READY and Base is not None and engine is not None:
        try:
            Base.metadata.create_all(bind=engine)
            print("[TrustShield] Database tables verified.")
        except Exception as e:
            print(f"[TrustShield] Database initialization notice: {e}")
    yield

# Initialize FastAPI application
app = FastAPI(
    title="Trust Shield - AI Fake Profile Detection Platform",
    description="Automated social media forensic analyzer and ML detection suite",
    version="1.0.0",
    lifespan=lifespan
)

# Cross-Origin Resource Sharing (CORS) setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (CSS, JS, images)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Mount Jinja2 HTML Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR if os.path.exists(TEMPLATES_DIR) else "templates")

# Register API Routers
app.include_router(scan_router)
if auth_router:
    app.include_router(auth_router)

# Route 1: Home / Landing Page
@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_file):
        return templates.TemplateResponse(request=request, name="index.html")
    
    return HTMLResponse(
        content="""
        <html>
            <head><title>Trust Shield API</title></head>
            <body style="font-family:sans-serif; text-align:center; padding-top:50px;">
                <h1>Trust Shield Platform is Running</h1>
                <p>Interactive API docs available at <a href="/docs">/docs</a></p>
                <p>Open dashboard at <a href="/dashboard">/dashboard</a></p>
            </body>
        </html>
        """
    )

# Route 2: Dashboard Page
@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    dashboard_file = os.path.join(TEMPLATES_DIR, "dashboard.html")
    target_template = "dashboard.html" if os.path.exists(dashboard_file) else "index.html"
    return templates.TemplateResponse(request=request, name=target_template)

# Route 3: History Page
@app.get("/history", response_class=HTMLResponse)
async def serve_history(request: Request):
    history_file = os.path.join(TEMPLATES_DIR, "history.html")
    target_template = "history.html" if os.path.exists(history_file) else "dashboard.html"
    return templates.TemplateResponse(request=request, name=target_template)

# Route 4: Login Page
@app.get("/login", response_class=HTMLResponse)
async def serve_login(request: Request):
    login_file = os.path.join(TEMPLATES_DIR, "login.html")
    target_template = "login.html" if os.path.exists(login_file) else "index.html"
    return templates.TemplateResponse(request=request, name=target_template)

# Route 5: Health check
@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "service": "Trust Shield",
            "status": "online",
            "database_connected": DATABASE_READY
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
