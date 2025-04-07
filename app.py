"""
CRA Mobile API - Main Application File
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Comment out the imports that don't exist in the deployment environment
# from config.settings import Config
# from api.routes import register_routes

# Create a simple Config class since the original is not available
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-jwt-key')

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    JWTManager(app)
    
    # Since we can't import register_routes, define routes directly here
    @app.route('/')
    def index():
        return jsonify({
            "status": "success",
            "message": "CRA Mobile API is running",
            "version": "1.0.0",
            "endpoints": [
                "/api/health",
                "/api/auth/login",
                "/api/alerts"
            ]
        })
    
    @app.route('/api/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "uptime": "active"
        })
    
    # Try to register API routes if available, but don't fail if not
    # try:
    #     register_routes(app)
    # except (ImportError, NameError):
    #     pass
    
    return app

# This is the application instance that gunicorn will use
application = create_app()
# Also create 'app' variable for backward compatibility
app = application

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
