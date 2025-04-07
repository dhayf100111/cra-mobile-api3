"""
API routes for the CRA Mobile API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, create_access_token
)
from database import (
    get_pending_alerts, get_alerts, add_alert, 
    close_alert, get_alert_stats
)
from auth import authenticate_user, generate_tokens
from utils import register_device, unregister_device, notify_new_alert
from utils.notifications import send_fcm_notification

# Create blueprints for different API sections
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
alerts_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')
notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

# Authentication routes
@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint"""
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    user_id = request.json.get('user_id', None)
    password = request.json.get('password', None)
    
    if not user_id or not password:
        return jsonify({"error": "Missing user_id or password"}), 400
    
    user = authenticate_user(user_id, password)
    
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Generate tokens
    tokens = generate_tokens(user)
    
    return jsonify(tokens), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh token endpoint"""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    
    return jsonify(access_token=access_token), 200

@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    """Get current user endpoint"""
    current_user = get_jwt_identity()
    
    return jsonify(current_user), 200

# Alert routes
@alerts_bp.route('', methods=['GET'])
@jwt_required()
def get_all_alerts():
    """Get alerts endpoint"""
    current_user = get_jwt_identity()
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    show_closed = request.args.get('show_closed', 'false').lower() == 'true'
    
    # Get alerts
    alerts, total_count = get_alerts(page, per_page, show_closed)
    
    return jsonify({
        'alerts': alerts,
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'pages': (total_count + per_page - 1) // per_page
    }), 200

@alerts_bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending():
    """Get pending alerts endpoint"""
    current_user = get_jwt_identity()
    
    # Check if user has receiver role
    if current_user.get('role') not in ['receiver', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403
    
    # Get pending alerts
    alerts = get_pending_alerts()
    
    return jsonify(alerts), 200

@alerts_bp.route('', methods=['POST'])
@jwt_required()
def create_alert():
    """Create alert endpoint"""
    current_user = get_jwt_identity()
    
    # Check if user has sender role
    if current_user.get('role') not in ['sender', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403
    
    # Get request data
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    file_number = request.json.get('file_number', None)
    test_name = request.json.get('test_name', None)
    value = request.json.get('value', None)
    
    if not file_number or not test_name or not value:
        return jsonify({"error": "Missing required fields"}), 400
    
    # Add alert
    alert_id = add_alert(file_number, test_name, value)
    
    if not alert_id:
        return jsonify({"error": "Failed to add alert"}), 500
    
    # Get the alert data
    alerts, _ = get_alerts(1, 1, False)
    alert_data = next((a for a in alerts if a['id'] == alert_id), None)
    
    # Send notifications
    if alert_data:
        notify_new_alert(alert_data)
    
    return jsonify({"id": alert_id, "message": "Alert created successfully"}), 201

@alerts_bp.route('/<int:alert_id>/close', methods=['PUT'])
@jwt_required()
def mark_alert_closed(alert_id):
    """Close alert endpoint"""
    current_user = get_jwt_identity()
    
    # Close alert
    success = close_alert(alert_id, current_user.get('id'))
    
    if not success:
        return jsonify({"error": "Failed to close alert"}), 500
    
    return jsonify({"message": "Alert closed successfully"}), 200

@alerts_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get alert statistics endpoint"""
    current_user = get_jwt_identity()
    
    # Check if user has admin role
    if current_user.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    # Get days parameter
    days = request.args.get('days', 30, type=int)
    
    # Get statistics
    stats = get_alert_stats(days)
    
    return jsonify(stats), 200

# Notification routes
@notifications_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    """Register device for notifications endpoint"""
    current_user = get_jwt_identity()
    
    # Get request data
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    device_token = request.json.get('device_token', None)
    
    if not device_token:
        return jsonify({"error": "Missing device_token"}), 400
    
    # Register device
    success = register_device(current_user.get('id'), device_token)
    
    if not success:
        return jsonify({"error": "Failed to register device"}), 500
    
    return jsonify({"message": "Device registered successfully"}), 200

@notifications_bp.route('/unregister', methods=['DELETE'])
@jwt_required()
def unregister():
    """Unregister device for notifications endpoint"""
    current_user = get_jwt_identity()
    
    # Unregister device
    success = unregister_device(current_user.get('id'))
    
    if not success:
        return jsonify({"error": "Failed to unregister device"}), 500
    
    return jsonify({"message": "Device unregistered successfully"}), 200

@notifications_bp.route('/test', methods=['POST'])
@jwt_required()
def test_notification():
    """Test notification endpoint"""
    current_user = get_jwt_identity()
    
    # Send test notification
    success = send_fcm_notification(
        current_user.get('id'),
        "Test Notification",
        "This is a test notification from CRA Mobile API",
        {"test": True}
    )
    
    if not success:
        return jsonify({"error": "Failed to send test notification"}), 500
    
    return jsonify({"message": "Test notification sent successfully"}), 200

def register_routes(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(notifications_bp)
