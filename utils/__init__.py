"""
Initialize the utils package
"""
from .notifications import (
    send_fcm_notification,
    register_device,
    unregister_device,
    send_whatsapp_alert,
    notify_new_alert
)
