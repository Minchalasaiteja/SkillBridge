"""
Minimal Flask app to serve the SkillBridge frontend with styling and scripts
"""

from flask import Flask, send_from_directory, jsonify
import os
from functools import wraps

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")

# Configure Flask
app.config['DEBUG'] = True
app.config['JSON_SORT_KEYS'] = False

# ==================== Routes ====================

@app.route('/', methods=['GET'])
def index():
    """Serve the frontend HTML"""
    try:
        with open(os.path.join(BASE_DIR, 'index.html'), 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        return jsonify({"error": f"Failed to load index.html: {str(e)}"}), 500

@app.route('/style.css', methods=['GET'])
def serve_css():
    """Serve CSS file"""
    try:
        with open(os.path.join(BASE_DIR, 'style.css'), 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/css; charset=utf-8'}
    except Exception as e:
        return jsonify({"error": f"Failed to load style.css: {str(e)}"}), 500

@app.route('/script.js', methods=['GET'])
def serve_js():
    """Serve JavaScript file"""
    try:
        with open(os.path.join(BASE_DIR, 'script.js'), 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript; charset=utf-8'}
    except Exception as e:
        return jsonify({"error": f"Failed to load script.js: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "SkillBridge Multi-Agent System",
        "version": "1.0.0"
    }), 200

@app.route('/api/status', methods=['GET'])
def status():
    """Status endpoint"""
    return jsonify({
        "status": "operational",
        "database": "connected",
        "agents": {
            "goal_analyzer": "ready",
            "resource_researcher": "ready",
            "roadmap_synthesizer": "ready"
        }
    }), 200

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        "error": "Not found",
        "message": "The requested resource does not exist"
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500

# ==================== Main ====================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
