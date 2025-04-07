"""
CRA Mobile API - README
"""

# CRA Mobile API

This is the backend API for the CRA (Critical Results Alert) Mobile Application. It provides a RESTful API for the mobile app to interact with the CRA system.

## Features

- User authentication with JWT
- Alert management (create, view, close)
- Push notifications via Firebase Cloud Messaging
- WhatsApp notifications via Twilio
- Statistics and reporting

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables (see .env.example)
4. Run the application:
   ```
   python app.py
   ```

## API Endpoints

### Authentication

- `POST /api/auth/login` - Login and get access token
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/user` - Get current user information

### Alerts

- `GET /api/alerts` - Get all alerts (with pagination)
- `GET /api/alerts/pending` - Get pending alerts
- `POST /api/alerts` - Create a new alert
- `PUT /api/alerts/:id/close` - Close an alert
- `GET /api/alerts/stats` - Get alert statistics

### Notifications

- `POST /api/notifications/register` - Register device for push notifications
- `DELETE /api/notifications/unregister` - Unregister device
- `POST /api/notifications/test` - Send test notification

## Testing

Run the test script to verify API functionality:
```
python test_api.py
```

## Integration with CRA System

This API integrates with the existing CRA system by:
1. Accessing the same SQLite database
2. Using the same authentication system
3. Leveraging the same critical value rules
4. Supporting both mobile and WhatsApp notifications
