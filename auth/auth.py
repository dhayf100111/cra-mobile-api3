"""
Authentication utilities for the CRA Mobile API
"""
import bcrypt
import logging
from flask_jwt_extended import create_access_token, create_refresh_token
from database import log_security_event

# User data - in a real application, this would be stored in a database
# This matches the user data from the original CRA system
USERS = [
    {"id": "EMP001", "password_hash": None, "role": "sender", "name": "موظف المختبر 1"},
    {"id": "EMP002", "password_hash": None, "role": "receiver", "name": "طبيب 1"},
    {"id": "EMP003", "password_hash": None, "role": "sender", "name": "موظف المختبر 2"},
    {"id": "admin", "password_hash": None, "role": "admin", "name": "المسؤول"}
]

# Initial passwords (used only for initialization)
INITIAL_PASSWORDS = {
    "EMP001": "1234",
    "EMP002": "abcd",
    "EMP003": "lab123",
    "admin": "admin123"
}

def initialize_user_passwords():
    """
    Initialize user passwords with bcrypt hashing
    """
    for user in USERS:
        if user["id"] in INITIAL_PASSWORDS and not user["password_hash"]:
            password = INITIAL_PASSWORDS[user["id"]]
            user["password_hash"] = hash_password(password)
            logging.info(f"Initialized password for user {user['id']}")

def hash_password(password):
    """
    Hash a password using bcrypt
    
    Args:
        password (str): Plain text password
        
    Returns:
        bytes: Hashed password
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed_password):
    """
    Check if a password matches the hashed version
    
    Args:
        password (str): Plain text password
        hashed_password (bytes): Hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def authenticate_user(user_id, password, required_role=None):
    """
    Authenticate a user
    
    Args:
        user_id (str): User ID
        password (str): Password
        required_role (str, optional): Required role
        
    Returns:
        dict: User data if authentication successful, None otherwise
    """
    # Ensure passwords are initialized
    initialize_user_passwords()
    
    for user in USERS:
        if user["id"] == user_id:
            # Check password
            if check_password(password, user["password_hash"]):
                # Check role if required
                if required_role is None or user["role"] == required_role or user["role"] == "admin":
                    # Log successful login
                    log_security_event("login_success", user_id)
                    return user
                else:
                    # Log failed login due to insufficient role
                    log_security_event("login_failure", user_id, f"Insufficient role: {user['role']}, required: {required_role}")
                    return None
            else:
                # Log failed login due to invalid password
                log_security_event("login_failure", user_id, "Invalid password")
                return None
    
    # Log failed login due to user not found
    log_security_event("login_failure", user_id, "User not found")
    return None

def get_user_by_id(user_id):
    """
    Get user data by ID
    
    Args:
        user_id (str): User ID
        
    Returns:
        dict: User data if found, None otherwise
    """
    for user in USERS:
        if user["id"] == user_id:
            # Return a copy without the password hash
            user_copy = user.copy()
            user_copy.pop("password_hash", None)
            return user_copy
    return None

def generate_tokens(user):
    """
    Generate JWT tokens for a user
    
    Args:
        user (dict): User data
        
    Returns:
        dict: Access and refresh tokens
    """
    # Create a copy of user data without the password hash
    identity = {
        "id": user["id"],
        "role": user["role"],
        "name": user["name"]
    }
    
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": identity
    }
