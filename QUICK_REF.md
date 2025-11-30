# SkillBridge — Quick Reference Card

## 🚀 START THE APP

```powershell
C:/Users/prajw/anaconda3/Scripts/conda.exe run -p C:\Users\prajw\anaconda3 --no-capture-output python .\app.py
```

**App URL:** http://localhost:5000

---

## 🧪 TEST ENDPOINTS

### Health
```powershell
curl.exe http://localhost:5000/api/health
```

### Status
```powershell
curl.exe http://localhost:5000/api/status
```

### Register
```powershell
$body = @{ "email"="user@example.com"; "password"="pass123"; "name"="User" } | ConvertTo-Json
curl.exe -X POST http://localhost:5000/api/auth/register -ContentType "application/json" -Body $body
```


---

## 🗄️ DATABASE

### Seed Resources
```powershell
# Dry-run (no writes)
python .\seeder.py --count 500

# Commit to MongoDB
python .\seeder.py --count 500 --commit
```

### Check Resource Count
```powershell
python -c "import os, pymongo; c = pymongo.MongoClient(os.environ['MONGODB_URI']); db = c.skillbridge; print('count:', db.resources.count_documents({}))"
```

---

## 🐳 DOCKER

### Start Full Stack
```powershell
docker compose up --build
```

### Access
- App: http://localhost:5000
- Jaeger: http://localhost:16686
- Prometheus: http://localhost:9090

---

## 📁 KEY FILES

| File | Purpose |
|------|---------|
| `app.py` | Flask app & routes |
| `config.py` | Settings loader |
| `database.py` | MongoDB DAOs |
| `agents.py` | Multi-agent system |
| `auth.py` | JWT & password utils |
| `otel_setup.py` | Observability |
| `seeder.py` | DB seeder |
| `test_api.py` | Smoke tests |

---

## 📖 DOCUMENTATION

- `SETUP.md` — Complete setup guide
- `DEPLOYMENT.md` — Production deployment
- `ARCHITECTURE.md` — System design
- `PROJECT_SUMMARY.md` — Feature overview
- `KAGGLE_SUBMISSION.md` — Submission materials
- `DELIVERABLES.md` — Completion checklist

---

## ⚙️ CONFIGURATION

`.env` key variables:
- `GEMINI_API_KEY` — Your Gemini API key
- `MONGODB_URI` — MongoDB connection string
- `JWT_SECRET_KEY` — Token secret (change in production!)
- `FLASK_PORT` — Port (default 5000)

See `.env.example` for complete list.

---

## 🔧 TROUBLESHOOTING

| Issue | Fix |
|-------|-----|
| App won't start | `pip install -r requirements.txt` |
| 404 on `/` | This is normal; use `/api/health` |
| DB connection error | Check `MONGODB_URI` in `.env` |
| JWT errors | Ensure `JWT_SECRET_KEY` is set |
| Prometheus issues | Running in Docker; disabled on Windows local dev |

---

## ✨ STATUS

✅ **Application running**  
✅ **All endpoints functional**  
✅ **Database seeded**  
✅ **Auth system active**  
✅ **Observability configured**  
✅ **Ready for submission**

---

**Last Updated:** November 30, 2025  
**Next Step:** Review documentation or test endpoints!
