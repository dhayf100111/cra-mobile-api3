"""
Configuration settings for the CRA Mobile API
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database settings
    DATABASE_PATH = os.environ.get('DATABASE_PATH', '/home/ubuntu/cra_improved/data/alerts.db')
    
    # Firebase Cloud Messaging settings
    FCM_API_KEY = os.environ.get('FCM_API_KEY', '')
    
    # Twilio settings (for WhatsApp notifications)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
    TWILIO_FROM_WHATSAPP = os.environ.get('TWILIO_FROM_WHATSAPP', '')
    TWILIO_TO_WHATSAPP = os.environ.get('TWILIO_TO_WHATSAPP', '')
