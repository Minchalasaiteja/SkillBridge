# SkillBridge Capstone — Complete Setup & Running Guide

## ✅ Application Status: RUNNING

The Flask application is **successfully running** on:
- **Local:** http://localhost:5000 or http://127.0.0.1:5000
- **Network:** http://192.168.131.228:5000

## Quick Start

### 1. Start the Application (PowerShell)
```powershell
C:/Users/prajw/anaconda3/Scripts/conda.exe run -p C:\Users\prajw\anaconda3 --no-capture-output python .\app.py
```

The app will:
- Initialize OpenTelemetry (Jaeger tracing, Prometheus metrics)
- Connect to MongoDB (or log a warning if unavailable)
- Initialize the multi-agent orchestrator
- Start the Flask development server on port 5000
- Enable auto-reload when files change

### 2. Test Endpoints (from a NEW PowerShell terminal)

#### Health Check
```powershell
curl.exe http://localhost:5000/api/health
```
Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-30T...",
  "version": "1.0.0",
  "service": "SkillBridge Multi-Agent System"
}
```

#### Status
```powershell
curl.exe http://localhost:5000/api/status
```

#### Register a User
```powershell
$body = @{
  "email" = "user@example.com"
  "password" = "password123"
  "name" = "Test User"
} | ConvertTo-Json

curl.exe -X POST http://localhost:5000/api/auth/register `
  -ContentType "application/json" `
  -Body $body
```

#### Login
```powershell
$body = @{
  "email" = "user@example.com"
  "password" = "password123"
} | ConvertTo-Json

curl.exe -X POST http://localhost:5000/api/auth/login `
  -ContentType "application/json" `
  -Body $body
```

Expected response on success:
```json
{
  "status": "ok",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Database Operations

### Seed Resources (500 course entries)
Dry-run (no DB writes):
```powershell
C:/Users/prajw/anaconda3/Scripts/conda.exe run -p C:\Users\prajw\anaconda3 --no-capture-output python .\seeder.py --count 500
```

Commit to MongoDB:
```powershell
C:/Users/prajw/anaconda3/Scripts/conda.exe run -p C:\Users\prajw\anaconda3 --no-capture-output python .\seeder.py --count 500 --commit
```

### Check Resource Count in MongoDB
```powershell
C:/Users/prajw/anaconda3/Scripts/conda.exe run -p C:\Users\prajw\anaconda3 --no-capture-output python -c @'
import os, pymongo
c = pymongo.MongoClient(os.environ['MONGODB_URI'])
db = c.get_database(os.environ.get('MONGODB_DB_NAME', 'skillbridge'))
print('resources count:', db.resources.count_documents({}))
'@
```

---

## Docker Deployment (Recommended for Production)

Requires Docker Desktop installed and running.

### Start Full Stack (App + Jaeger + Prometheus)
```powershell
docker compose up --build
```

Access:
- **App:** http://localhost:5000
- **Jaeger UI:** http://localhost:16686 (traces and spans)
- **Prometheus:** http://localhost:9090 (metrics)

---

## Project Structure

```
skillbridge/
├── app.py                      # Flask entry point
├── config.py                   # Pydantic settings (.env loader)
├── database.py                 # MongoDB DAOs and connection
├── agents.py                   # Multi-agent system (Gemini-powered)
├── observability.py            # Structured logging, tracing, metrics
├── auth.py                     # JWT and password hashing
├── otel_setup.py               # OpenTelemetry initialization
├── seeder.py                   # Resource database seeder
├── test_api.py                 # API smoke tests
├── index.html                  # Frontend UI
├── style.css                   # Styling
├── script.js                   # Frontend JavaScript
├── requirements.txt            # Python dependencies
├── .env                        # Secrets (NOT in version control)
├── .env.example                # Template for .env
├── docker-compose.yml          # Docker stack definition
├── Dockerfile                  # App container image
├── prometheus.yml              # Prometheus config
├── README.md                   # Project overview
├── ARCHITECTURE.md             # Architecture & design docs
├── DEPLOYMENT.md               # Deployment instructions
├── KAGGLE_SUBMISSION.md        # Kaggle submission materials
└── skillbridge_complete.py     # Legacy multi-agent code (reference)
```

---

## Configuration (.env)

Key environment variables (copy from `.env.example` and fill in):
- `GEMINI_API_KEY` — Google Gemini API key
- `MONGODB_URI` — MongoDB connection string
- `JWT_SECRET_KEY` — Secret for JWT token signing
- `FLASK_ENV` — `development` or `production`
- `FLASK_PORT` — Default: 5000
- `JAEGER_HOST` — Default: localhost
- `JAEGER_PORT` — Default: 6831

---

## Known Issues & Fixes

| Issue | Fix |
|-------|-----|
| MongoDB connection timeout | Ensure `MONGODB_URI` is correct and IP is whitelisted. |
| Gemini API errors | Verify `GEMINI_API_KEY` is valid; watch quotas. |
| Windows socket errors (Prometheus) | Running in Docker avoids this; local dev disables Prometheus HTTP server. |
| Missing packages on pip install | Run `python -m pip install --upgrade pip setuptools` first. |
| CORS errors | Check `CORS_ORIGINS` in `.env` and `config.py`. |

---

## Features Implemented

✅ **Authentication:** JWT-based user registration and login  
✅ **Multi-Agent System:** Goal analysis, resource research, roadmap synthesis (Gemini-powered)  
✅ **Database:** MongoDB with DAOs for learners, pathways, sessions, resources, logs  
✅ **Observability:** Structured JSON logging, OpenTelemetry tracing (Jaeger), Prometheus metrics  
✅ **Resource Seeding:** Programmatic generation of 500+ course entries  
✅ **Modern Frontend:** HTML/CSS/JS with particles, animations, theme toggle  
✅ **API Documentation:** Endpoints for auth, pathways, learner profiles, observability  
✅ **Docker Support:** docker-compose with Jaeger and Prometheus for local testing  

---

## Next Steps

1. **Test the app** — Use the endpoints above to verify functionality.
2. **Populate the DB** — Run `python seeder.py --count 500 --commit` to seed resources.
3. **Run Kaggle submission** — See `KAGGLE_SUBMISSION.md` for materials.
4. **Deploy to Docker** — `docker compose up --build` for a production-like environment.
5. **Add unit tests** — Expand `test_api.py` with more comprehensive tests.

---

## Troubleshooting

**App won't start:**
- Ensure all dependencies are installed: `python -m pip install -r requirements.txt`
- Check `.env` file exists and is readable.
- Verify Python version is 3.10+.

**API returns 500 errors:**
- Check Flask console output for tracebacks.
- MongoDB connection issues? Disable in DB and use health/status endpoints which don't require DB.
- Missing JWT or auth headers? Register and login first to get a token.

**Database not connecting:**
- This is non-blocking — the app will run, but DB operations fail gracefully.
- Verify `MONGODB_URI` in `.env`.
- Test with: `python -c "import pymongo; pymongo.MongoClient(uri)"`

---

**Application is running and ready for testing!** 🚀
