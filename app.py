"""
Flask Backend for SkillBridge Capstone Project
Multi-agent AI system for personalized career pathway generation using Google Gemini
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session as FlaskSession
from datetime import datetime, timedelta
import uuid
import os
from functools import wraps

from config import settings
from agents import SkillBridgeOrchestrator
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request
from auth import register_learner, login_learner
from otel_setup import initialize_otel
from database import (
    init_db, close_db, get_db_instance,
    LearnerProfile, Pathway, Session as DBSession, AgentLog
)
from observability import get_logger, get_observability_summary
from bson import ObjectId
from datetime import datetime as _dt


def sanitize_for_json(obj):
    """Recursively convert non-JSON-serializable objects to JSON-friendly types."""
    # ObjectId -> str, datetime -> isoformat
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, _dt):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    return obj

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = settings.session_type
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=settings.session_timeout)

# CORS Setup
CORS(app, resources={r"/api/*": {"origins": settings.cors_origins_list()}})

# Session Setup
FlaskSession(app)

# Initialize JWT
app.config["JWT_SECRET_KEY"] = settings.jwt_secret_key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.jwt_access_token_expires
jwt = JWTManager(app)

# Initialize OpenTelemetry (Jaeger / Prometheus)
try:
    initialize_otel(app, settings)
    logger = get_logger("app")
    logger.info("OpenTelemetry initialized")
except Exception:
    logger = get_logger("app")
    logger.warning("Failed to initialize OpenTelemetry (continuing without it)")

# Database Setup
logger = get_logger("app")

# Initialize orchestrator (don't block on DB)
orchestrator = SkillBridgeOrchestrator()

# Try to initialize database in the background
import threading
def init_db_async():
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database connection failed (app will continue): {str(e)}")

db_thread = threading.Thread(target=init_db_async, daemon=True)
db_thread.start()


# ==================== Authentication & Session Management ====================

def require_auth(f):
    """Decorator for routes requiring authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Prefer JWT if provided
        try:
            # If there is an Authorization header with a bearer token, this will
            # raise if invalid; otherwise it sets the context for get_jwt_identity().
            verify_jwt_in_request(optional=True)
            identity = None
            try:
                identity = get_jwt_identity()
            except Exception:
                identity = None

            if identity:
                # JWT is present and valid; attach to session for compatibility
                session['current_user'] = identity
                return f(*args, **kwargs)
        except Exception:
            # Token invalid or not present; fall back to session cookie behavior
            pass

        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            session['created_at'] = datetime.utcnow().isoformat()
        return f(*args, **kwargs)
    return decorated_function


# ==================== Root & Frontend ====================

@app.route('/', methods=['GET'])
def index():
    """Serve the frontend or redirect to API docs"""
    try:
        with open('index.html', 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    except Exception:
        # If index.html not found, show a simple API info page
        return jsonify({
            "message": "SkillBridge Multi-Agent Career Pathway Builder",
            "version": "1.0.0",
            "status": "running",
            "api_endpoints": {
                "health": "/api/health",
                "status": "/api/status",
                "auth": "/api/auth/register, /api/auth/login",
                "pathways": "/api/generate_pathway, /api/pathways/<learner_id>, /api/pathways/recent",
                "learners": "/api/learners, /api/learners/<learner_id>",
                "observability": "/api/observability/logs, /api/observability/summary"
            }
        }), 200


# ==================== Health & Status Endpoints ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "SkillBridge Multi-Agent System"
    }), 200


@app.route('/api/status', methods=['GET'])
def status():
    """Get system status"""
    return jsonify({
        "status": "operational",
        "database": "connected",
        "agents": {
            "goal_analyzer": "ready",
            "resource_researcher": "ready",
            "roadmap_synthesizer": "ready"
        },
        "timestamp": datetime.utcnow().isoformat()
    }), 200


# ==================== Authentication Endpoints ====================


@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    result = register_learner(data)
    if result.get("status") == "created":
        return jsonify(result), 201
    return jsonify(result), 400


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"status": "error", "error": "email and password required"}), 400

    result = login_learner(email, password)
    if result.get("status") == "ok":
        return jsonify(result), 200
    return jsonify(result), 401



# ==================== Pathway Generation Endpoints ====================

@app.route('/api/generate_pathway', methods=['POST'])
@require_auth
def generate_pathway():
    """Generate personalized learning pathway"""
    try:
        learner_input = request.get_json()
        
        if not learner_input:
            return jsonify({"error": "No input provided"}), 400
        
        # Generate learner ID if not provided
        if 'learner_id' not in learner_input:
            learner_input['learner_id'] = str(uuid.uuid4())
        
        logger.info(
            "Pathway generation requested",
            learner_id=learner_input.get('learner_id'),
            goal=learner_input.get('career_goal')
        )
        
        # Generate pathway using multi-agent system
        pathway = orchestrator.generate_pathway(learner_input)
        
        # Save to database
        if pathway['status'] == 'success':
            db = get_db_instance()
            
            # Save learner profile
            learner_profile_dao = LearnerProfile(db)
            learner_profile_dao.create(learner_input)
            
            # Save pathway
            pathway_dao = Pathway(db)
            pathway_dao.create(pathway)
            
            logger.info(
                "Pathway generated and saved",
                learner_id=pathway['learner_id'],
                score=pathway['evaluation_score']
            )
        
        return jsonify(sanitize_for_json(pathway)), 200
        
    except Exception as e:
        logger.error(f"Error generating pathway: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@app.route('/api/pathways/<learner_id>', methods=['GET'])
@require_auth
def get_learner_pathway(learner_id):
    """Get learner's pathway"""
    try:
        db = get_db_instance()
        pathway_dao = Pathway(db)
        pathway = pathway_dao.find_by_learner(learner_id)
        
        if not pathway:
            return jsonify({
                "error": "Pathway not found",
                "learner_id": learner_id
            }), 404
        
        return jsonify(sanitize_for_json(pathway)), 200
        
    except Exception as e:
        logger.error(f"Error retrieving pathway: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/pathways/recent', methods=['GET'])
@require_auth
def get_recent_pathways():
    """Get recent pathways"""
    try:
        limit = request.args.get('limit', default=10, type=int)
        db = get_db_instance()
        pathway_dao = Pathway(db)
        pathways = pathway_dao.find_recent(limit)
        
        return jsonify({
            "count": len(pathways),
            "pathways": sanitize_for_json(pathways)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving recent pathways: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ==================== Learner Profile Endpoints ====================

@app.route('/api/learners', methods=['POST'])
@require_auth
def create_learner():
    """Create new learner profile"""
    try:
        learner_data = request.get_json()
        
        db = get_db_instance()
        learner_dao = LearnerProfile(db)
        mongo_id = learner_dao.create(learner_data)
        
        logger.info(f"Learner profile created: {mongo_id}")
        
        return jsonify({
            "id": mongo_id,
            "status": "created",
            "timestamp": datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating learner: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/learners/<learner_id>', methods=['GET'])
@require_auth
def get_learner(learner_id):
    """Get learner profile"""
    try:
        db = get_db_instance()
        learner_dao = LearnerProfile(db)
        learner = learner_dao.find_by_id(learner_id)
        
        if not learner:
            return jsonify({
                "error": "Learner not found",
                "learner_id": learner_id
            }), 404
        
        return jsonify(learner), 200
        
    except Exception as e:
        logger.error(f"Error retrieving learner: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/learners/<learner_id>', methods=['PUT'])
@require_auth
def update_learner(learner_id):
    """Update learner profile"""
    try:
        update_data = request.get_json()
        
        db = get_db_instance()
        learner_dao = LearnerProfile(db)
        success = learner_dao.update(learner_id, update_data)
        
        if not success:
            return jsonify({"error": "Learner not found"}), 404
        
        logger.info(f"Learner profile updated: {learner_id}")
        
        return jsonify({
            "status": "updated",
            "learner_id": learner_id,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating learner: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ==================== Observability Endpoints ====================

@app.route('/api/observability/logs', methods=['GET'])
@require_auth
def get_logs():
    """Get system logs"""
    try:
        db = get_db_instance()
        agent_log_dao = AgentLog(db)
        
        learner_id = request.args.get('learner_id')
        agent_name = request.args.get('agent_name')
        limit = request.args.get('limit', default=50, type=int)
        
        if learner_id:
            logs = agent_log_dao.find_by_learner(learner_id, limit)
        elif agent_name:
            logs = agent_log_dao.find_by_agent(agent_name, limit)
        else:
            logs = []
        
        return jsonify({
            "count": len(logs),
            "logs": logs
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/observability/summary', methods=['GET'])
@require_auth
def observability_summary():
    """Get observability summary"""
    try:
        summary = get_observability_summary()
        return jsonify(summary), 200
    except Exception as e:
        logger.error(f"Error getting observability summary: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Not found",
        "status": 404
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "status": 500
    }), 500


# ==================== Cleanup ====================

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Cleanup on app shutdown"""
    if exception:
        logger.error(f"Shutting down with exception: {str(exception)}")


if __name__ == '__main__':
    app.run(
        host=settings.flask_host,
        port=settings.flask_port,
        debug=settings.flask_debug
    )
