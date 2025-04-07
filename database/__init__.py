"""
Initialize the database package
"""
from .db import (
    get_db_connection,
    get_pending_alerts,
    get_alerts,
    add_alert,
    close_alert,
    get_alert_stats,
    log_security_event
)
