# Trust Shield — AI-Powered Social Media Profile Forensics

Trust Shield is a full-stack, AI-assisted cybersecurity and digital identity intelligence platform. It analyzes social media profiles, account URLs, and profile screenshots to detect suspicious signals, synthetic patterns, typo-squatting impersonators, and automated bot accounts across Instagram, LinkedIn, Twitter/X, and Facebook.

---

## Key Features

- **Interactive Hero — “Two Profiles. Two Stories.”**: Compare authentic and suspicious profiles side-by-side with real-time forensic indicator overlays on hover/tap.
- **Authentic Multi-Platform Showcase**: Pixel-accurate profile interfaces mirroring real Instagram, LinkedIn, Facebook, and X desktop and mobile layouts.
- **Multi-Vector Forensic Engine**:
  - **Behavioral Velocity**: Evaluates posting volume, activity cadences, and timing patterns.
  - **Linguistic NLP**: Measures Shannon entropy, handle generation anomalies, and promotional spam phrasing.
  - **Vision & OCR Forensics**: Extracts profile metrics directly from uploaded mobile or desktop screenshots using high-speed native OCR with character normalization.
  - **Network Reciprocity**: Assesses follower-to-following ratios, institutional connection depth, and follow-churn dynamics.
- **Fair & Calibrated Scoring**: Eliminates false bot-penalties on authentic human accounts while reliably identifying synthetic bot-farms and impersonators.
- **Auditing & History**: Real-time dossier logging with radar signal charts, evidence rationales, and exportable findings.

---

## Quick Start Guide

### 1. Requirements
- Python 3.10+ (tested on Python 3.11, 3.12, 3.14)
- Windows 10/11 (for native Windows Media OCR) or Linux/macOS with Tesseract OCR

### 2. Installation
Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Running the Application
Launch the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Or on Windows, simply double-click `run_app.bat`.

Once running, navigate to:
- **Landing Page**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **URL Scanner**: [http://127.0.0.1:8000/scan/url](http://127.0.0.1:8000/scan/url)
- **Screenshot Scanner**: [http://127.0.0.1:8000/scan/photo](http://127.0.0.1:8000/scan/photo)
- **Session History**: [http://127.0.0.1:8000/history](http://127.0.0.1:8000/history)
- **Analyst Console**: [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
- **Interactive API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Project Structure

```
├── app/
│   ├── api/
│   │   ├── auth.py             # Authentication routes
│   │   └── scan.py             # URL and Screenshot scan API endpoints
│   ├── core/
│   │   ├── behavioral.py       # Activity cadence and posting rate analyzer
│   │   ├── ensemble.py         # Multi-model risk score aggregator
│   │   ├── linguistic.py       # Text entropy and spam keyword detector
│   │   ├── network.py          # Follower/following ratio analyzer
│   │   ├── ocr_engine.py       # OCR parser for screenshots
│   │   ├── url_resolver.py     # Live social profile scraper/resolver
│   │   └── vision.py           # Deepfake and compression artifact scanner
│   ├── db/
│   │   ├── database.py         # SQLite connection manager
│   │   └── models.py           # Audit log and user schemas
│   └── main.py                 # FastAPI application factory
├── data/                       # Training datasets
├── ml/                         # Trained model artifacts and scalers
├── notebooks/                  # Model research and exploration notebooks
├── static/                     # CSS stylesheets, brand tokens, and images
├── templates/                  # Jinja2 HTML templates
├── trustshield.db              # Active SQLite database
├── requirements.txt            # Python dependencies
├── run_app.bat                 # Windows one-click launcher
└── README.md                   # Project documentation
```
