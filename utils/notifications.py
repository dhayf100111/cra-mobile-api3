"""
Notification utilities for the CRA Mobile API
"""
import logging
from pyfcm import FCMNotification
from twilio.rest import Client
from config.settings import Config

# Dictionary to store device tokens for FCM
# In a real application, this would be stored in a database
DEVICE_TOKENS = {}

def send_fcm_notification(user_id, title, message, data=None):
    """
    Send a Firebase Cloud Messaging notification
    
    Args:
        user_id (str): User ID to send notification to
        title (str): Notification title
        message (str): Notification message
        data (dict, optional): Additional data to send
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if we have a device token for this user
        if user_id not in DEVICE_TOKENS or not DEVICE_TOKENS[user_id]:
            logging.warning(f"No device token found for user {user_id}")
            return False
            
        # Check if FCM API key is configured
        if not Config.FCM_API_KEY:
            logging.warning("FCM API key not configured")
            return False
            
        # Initialize FCM
        push_service = FCMNotification(api_key=Config.FCM_API_KEY)
        
        # Prepare data payload
        data_payload = data or {}
        data_payload.update({
            "title": title,
            "body": message
        })
        
        # Send notification
        result = push_service.notify_single_device(
            registration_id=DEVICE_TOKENS[user_id],
            message_title=title,
            message_body=message,
            data_message=data_payload
        )
        
        logging.info(f"FCM notification sent to user {user_id}: {result}")
        return True
    except Exception as e:
        logging.error(f"Error sending FCM notification: {e}")
        return False

def register_device(user_id, device_token):
    """
    Register a device token for a user
    
    Args:
        user_id (str): User ID
        device_token (str): FCM device token
        
    Returns:
        bool: True if successful
    """
    try:
        DEVICE_TOKENS[user_id] = device_token
        logging.info(f"Device token registered for user {user_id}")
        return True
    except Exception as e:
        logging.error(f"Error registering device token: {e}")
        return False

def unregister_device(user_id):
    """
    Unregister a device token for a user
    
    Args:
        user_id (str): User ID
        
    Returns:
        bool: True if successful
    """
    try:
        if user_id in DEVICE_TOKENS:
            del DEVICE_TOKENS[user_id]
            logging.info(f"Device token unregistered for user {user_id}")
        return True
    except Exception as e:
        logging.error(f"Error unregistering device token: {e}")
        return False

def send_whatsapp_alert(patient_id, test_name, value):
    """
    Send a WhatsApp alert using Twilio
    
    Args:
        patient_id (str): Patient file number
        test_name (str): Test name
        value (str): Test value
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if Twilio credentials are configured
        if not all([
            Config.TWILIO_ACCOUNT_SID,
            Config.TWILIO_AUTH_TOKEN,
            Config.TWILIO_FROM_WHATSAPP,
            Config.TWILIO_TO_WHATSAPP
        ]):
            logging.warning("Twilio credentials not fully configured")
            return False
            
        # Initialize Twilio client
        client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        
        # Create message body
        message_body = f"🚨 *Critical Lab Result Alert* 🚨\nPatient File: {patient_id}\nTest: {test_name}\nValue: {value}"
        
        # Send message
        message = client.messages.create(
            body=message_body,
            from_=Config.TWILIO_FROM_WHATSAPP,
            to=Config.TWILIO_TO_WHATSAPP
        )
        
        logging.info(f"WhatsApp alert sent: SID={message.sid}")
        return True
    except Exception as e:
        logging.error(f"Error sending WhatsApp alert: {e}")
        return False

def notify_new_alert(alert_data):
    """
    Send notifications for a new alert to all receivers
    
    Args:
        alert_data (dict): Alert data
        
    Returns:
        bool: True if at least one notification was sent
    """
    try:
        # Get all users with receiver role
        from auth.auth import USERS
        receivers = [user["id"] for user in USERS if user["role"] == "receiver"]
        
        # Send FCM notifications to all receivers
        notification_sent = False
        for receiver_id in receivers:
            title = "تنبيه نتيجة حرجة"
            message = f"رقم الملف: {alert_data['file_number']}\nالفحص: {alert_data['test_name']}\nالقيمة: {alert_data['value']}"
            
            # Send FCM notification
            fcm_sent = send_fcm_notification(
                receiver_id,
                title,
                message,
                {"alert_id": alert_data["id"]}
            )
            
            if fcm_sent:
                notification_sent = True
        
        # Send WhatsApp notification
        whatsapp_sent = send_whatsapp_alert(
            alert_data["file_number"],
            alert_data["test_name"],
            alert_data["value"]
        )
        
        if whatsapp_sent:
            notification_sent = True
            
        return notification_sent
    except Exception as e:
        logging.error(f"Error notifying about new alert: {e}")
        return False
