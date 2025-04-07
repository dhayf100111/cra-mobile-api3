"""
CRA Mobile API - Main Application File
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config.settings import Config
from api.routes import register_routes

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    JWTManager(app)
    
    # Register API routes
    register_routes(app)
    
    return app

# This is the application instance that gunicorn will use
application = create_app()
# Also create 'app' variable for backward compatibility
app = application

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)
