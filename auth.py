"""
Simple authentication helpers using flask-jwt-extended and passlib.
Provides registration and login helpers that app.py can call from endpoints.
"""

from passlib.context import CryptContext
from datetime import timedelta, datetime
from uuid import uuid4
from database import get_db_instance, LearnerProfile, init_db, close_db
from config import settings
from flask_jwt_extended import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def register_learner(learner_data: dict) -> dict:
    """Register a user. Expects keys: email, password, name (optional).
    Returns dict with status and id on success.
    """
    # Minimal validation
    if "email" not in learner_data or "password" not in learner_data:
        return {"status": "error", "error": "email and password required"}

    try:
        db = get_db_instance()
        dao = LearnerProfile(db)

        email = learner_data["email"].lower().strip()
        existing = dao.collection.find_one({"email": email})
        if existing:
            return {"status": "error", "error": "user already exists"}

        hashed = hash_password(learner_data["password"])
        profile = {
            "learner_id": learner_data.get("learner_id") or str(uuid4()),
            "email": email,
            "name": learner_data.get("name"),
            "password_hash": hashed,
            "created_at": datetime.utcnow(),
            "roles": learner_data.get("roles", ["learner"]) 
        }

        result = dao.collection.insert_one(profile)
        return {"status": "created", "id": str(result.inserted_id)}
    except Exception as e:
        return {"status": "error", "error": f"Registration failed: {str(e)}"}


def login_learner(email: str, password: str) -> dict:
    """Attempt login. Return access token on success."""
    try:
        db = get_db_instance()
        dao = LearnerProfile(db)

        user = dao.collection.find_one({"email": email.lower().strip()})
        if not user:
            return {"status": "error", "error": "invalid credentials"}

        if not verify_password(password, user.get("password_hash", "")):
            return {"status": "error", "error": "invalid credentials"}

        expires = timedelta(seconds=settings.jwt_access_token_expires)
        identity = {"learner_id": user.get("learner_id"), "email": user.get("email")}
        token = create_access_token(identity=identity, expires_delta=expires)
        return {"status": "ok", "access_token": token}
    except Exception as e:
        return {"status": "error", "error": f"Login failed: {str(e)}"}
