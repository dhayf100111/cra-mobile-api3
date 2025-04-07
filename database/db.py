"""
Database operations for the CRA Mobile API
"""
import sqlite3
import logging
from datetime import datetime
from config.settings import Config

def get_db_connection():
    """
    Create a connection to the SQLite database
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        raise

def get_pending_alerts():
    """
    Get alerts that have not been shown yet
    
    Returns:
        list: List of pending alerts
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM critical_alerts WHERE shown = 0")
        rows = cursor.fetchall()
        
        alerts = []
        for row in rows:
            alerts.append(dict(row))
        
        conn.close()
        return alerts
    except Exception as e:
        logging.error(f"Error getting pending alerts: {e}")
        return []

def get_alerts(page=1, per_page=20, show_closed=False):
    """
    Get alerts with pagination
    
    Args:
        page (int): Page number (starting from 1)
        per_page (int): Number of items per page
        show_closed (bool): Whether to include closed alerts
        
    Returns:
        tuple: (alerts, total_count)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query based on whether to show closed alerts
        query = "SELECT * FROM critical_alerts"
        count_query = "SELECT COUNT(*) FROM critical_alerts"
        
        if not show_closed:
            query += " WHERE shown = 0"
            count_query += " WHERE shown = 0"
        
        # Add ordering and pagination
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        
        # Get total count
        cursor.execute(count_query)
        total_count = cursor.fetchone()[0]
        
        # Get paginated results
        cursor.execute(query, (per_page, (page - 1) * per_page))
        rows = cursor.fetchall()
        
        alerts = []
        for row in rows:
            alerts.append(dict(row))
        
        conn.close()
        return (alerts, total_count)
    except Exception as e:
        logging.error(f"Error getting alerts: {e}")
        return ([], 0)

def add_alert(file_number, test_name, value):
    """
    Add a new critical alert
    
    Args:
        file_number (str): Patient file number
        test_name (str): Test name
        value (str): Test value
        
    Returns:
        int: ID of the new alert, or None if failed
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO critical_alerts 
            (file_number, test_name, value, timestamp, shown)
            VALUES (?, ?, ?, ?, 0)
        """, (file_number, test_name, value, timestamp))
        
        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logging.info(f"Added critical alert: ID={alert_id}, File={file_number}, Test={test_name}, Value={value}")
        return alert_id
    except Exception as e:
        logging.error(f"Error adding critical alert: {e}")
        return None

def close_alert(alert_id, user_id):
    """
    Mark an alert as closed
    
    Args:
        alert_id (int): Alert ID
        user_id (str): User ID who closed the alert
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE critical_alerts SET shown = 1, closed_by = ?, closed_at = ? WHERE id = ?",
            (user_id, now, alert_id)
        )
        
        conn.commit()
        conn.close()
        
        logging.info(f"Alert ID={alert_id} marked as closed by user {user_id}")
        return True
    except Exception as e:
        logging.error(f"Error marking alert as closed: {e}")
        return False

def get_alert_stats(days=30):
    """
    Get alert statistics for the specified number of days
    
    Args:
        days (int): Number of days to include in statistics
        
    Returns:
        dict: Statistics dictionary
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total alerts in the period
        cursor.execute("""
        SELECT COUNT(*) FROM critical_alerts 
        WHERE datetime(timestamp) >= datetime('now', ?)
        """, (f'-{days} days',))
        total_alerts = cursor.fetchone()[0]
        
        # Get closed alerts in the period
        cursor.execute("""
        SELECT COUNT(*) FROM critical_alerts 
        WHERE shown = 1 AND datetime(timestamp) >= datetime('now', ?)
        """, (f'-{days} days',))
        closed_alerts = cursor.fetchone()[0]
        
        # Get average response time (in minutes)
        cursor.execute("""
        SELECT AVG((julianday(closed_at) - julianday(timestamp)) * 24 * 60) 
        FROM critical_alerts 
        WHERE shown = 1 AND closed_at IS NOT NULL 
        AND datetime(timestamp) >= datetime('now', ?)
        """, (f'-{days} days',))
        avg_response_time = cursor.fetchone()[0] or 0
        
        # Get test type distribution
        cursor.execute("""
        SELECT test_name, COUNT(*) as count 
        FROM critical_alerts 
        WHERE datetime(timestamp) >= datetime('now', ?)
        GROUP BY test_name 
        ORDER BY count DESC
        """, (f'-{days} days',))
        test_distribution = {row['test_name']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_alerts': total_alerts,
            'closed_alerts': closed_alerts,
            'pending_alerts': total_alerts - closed_alerts,
            'avg_response_time_minutes': round(avg_response_time, 2),
            'test_distribution': test_distribution
        }
    except Exception as e:
        logging.error(f"Error getting alert statistics: {e}")
        return {
            'total_alerts': 0,
            'closed_alerts': 0,
            'pending_alerts': 0,
            'avg_response_time_minutes': 0,
            'test_distribution': {}
        }

def log_security_event(event_type, user_id, details=""):
    """
    Log a security event
    
    Args:
        event_type (str): Type of event (e.g., "login_attempt", "login_success")
        user_id (str): User ID
        details (str): Additional details
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO security_log (event_type, user_id, timestamp, details) VALUES (?, ?, ?, ?)",
            (event_type, user_id, timestamp, details)
        )
        
        conn.commit()
        conn.close()
        
        logging.info(f"Security event logged: {event_type} by {user_id}")
        return True
    except Exception as e:
        logging.error(f"Error logging security event: {e}")
        return False
