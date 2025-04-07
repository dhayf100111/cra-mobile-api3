"""
Test script for the CRA Mobile API
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000/api"

def test_auth():
    """Test authentication endpoints"""
    print("\n=== Testing Authentication ===")
    
    # Test login
    print("\nTesting login...")
    login_data = {
        "user_id": "EMP001",
        "password": "1234"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("Login successful!")
        data = response.json()
        access_token = data.get("access_token")
        print(f"User: {data.get('user')}")
        return access_token
    else:
        print(f"Login failed: {response.text}")
        return None

def test_alerts(access_token):
    """Test alert endpoints"""
    print("\n=== Testing Alerts ===")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test get alerts
    print("\nTesting get alerts...")
    response = requests.get(f"{BASE_URL}/alerts", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total alerts: {data.get('total')}")
        print(f"Current page: {data.get('page')}")
    
    # Test create alert
    print("\nTesting create alert...")
    alert_data = {
        "file_number": "TEST123",
        "test_name": "Glucose",
        "value": "500"
    }
    response = requests.post(f"{BASE_URL}/alerts", headers=headers, json=alert_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"Alert created with ID: {data.get('id')}")
        alert_id = data.get('id')
        
        # Test close alert
        print("\nTesting close alert...")
        response = requests.put(f"{BASE_URL}/alerts/{alert_id}/close", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Alert closed successfully!")

def test_notifications(access_token):
    """Test notification endpoints"""
    print("\n=== Testing Notifications ===")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test register device
    print("\nTesting register device...")
    device_data = {
        "device_token": "test_device_token_123"
    }
    response = requests.post(f"{BASE_URL}/notifications/register", headers=headers, json=device_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Device registered successfully!")
        
        # Test test notification
        print("\nTesting send test notification...")
        response = requests.post(f"{BASE_URL}/notifications/test", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Test notification sent successfully!")
        
        # Test unregister device
        print("\nTesting unregister device...")
        response = requests.delete(f"{BASE_URL}/notifications/unregister", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Device unregistered successfully!")

def run_tests():
    """Run all tests"""
    print("Starting CRA Mobile API tests...")
    
    # Test authentication
    access_token = test_auth()
    if not access_token:
        print("Authentication failed, cannot continue tests.")
        return
    
    # Test alerts
    test_alerts(access_token)
    
    # Test notifications
    test_notifications(access_token)
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    run_tests()
