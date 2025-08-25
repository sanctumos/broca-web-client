#!/usr/bin/env python3
"""
Test script for the Web Chat Bridge Flask API
This script demonstrates all the main API endpoints and functionality
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "ObeyG1ant"
ADMIN_KEY = "FreeUkra1ne"

def test_message_submission():
    """Test message submission endpoint"""
    print("=== Testing Message Submission ===")
    
    url = f"{BASE_URL}/api/v1/messages"
    data = {
        "session_id": "session_test_demo",
        "message": "This is a test message from the demo script"
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return response.json()

def test_get_responses():
    """Test getting responses for a session"""
    print("=== Testing Get Responses ===")
    
    url = f"{BASE_URL}/api/v1/responses"
    params = {"session_id": "session_test_demo"}
    
    response = requests.get(url, params=params)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return response.json()

def test_inbox_with_auth():
    """Test inbox endpoint with API key authentication"""
    print("=== Testing Inbox with Authentication ===")
    
    url = f"{BASE_URL}/api/v1/inbox"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return response.json()

def test_outbox_with_auth():
    """Test outbox endpoint with API key authentication"""
    print("=== Testing Outbox with Authentication ===")
    
    url = f"{BASE_URL}/api/v1/outbox"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {
        "session_id": "session_test_demo",
        "response": "This is a test response from the plugin",
        "message_id": 1
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return response.json()

def test_admin_sessions():
    """Test admin sessions endpoint"""
    print("=== Testing Admin Sessions ===")
    
    url = f"{BASE_URL}/admin/api/sessions"
    headers = {"Authorization": f"Bearer {ADMIN_KEY}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return response.json()

def test_admin_config():
    """Test admin config endpoint"""
    print("=== Testing Admin Config ===")
    
    url = f"{BASE_URL}/admin/api/config"
    headers = {"Authorization": f"Bearer {ADMIN_KEY}"}
    
    # Get current config
    response = requests.get(url, headers=headers)
    print(f"GET Status: {response.status_code}")
    print(f"Current Config: {json.dumps(response.json(), indent=2)}")
    
    # Update config
    update_data = {
        "rate_limit_max_requests": "1500"
    }
    
    response = requests.post(url, json=update_data, headers=headers)
    print(f"POST Status: {response.status_code}")
    print(f"Update Response: {json.dumps(response.json(), indent=2)}")
    
    # Get updated config
    response = requests.get(url, headers=headers)
    print(f"Updated Config: {json.dumps(response.json(), indent=2)}")
    print()

def test_rate_limiting():
    """Test rate limiting by making multiple requests"""
    print("=== Testing Rate Limiting ===")
    
    url = f"{BASE_URL}/api/v1/messages"
    
    for i in range(5):
        data = {
            "session_id": f"session_rate_test_{i}",
            "message": f"Rate test message {i}"
        }
        
        response = requests.post(url, json=data)
        print(f"Request {i+1}: Status {response.status_code}")
        
        if response.status_code == 429:
            print("Rate limit hit!")
            break
        
        time.sleep(0.1)  # Small delay between requests
    
    print()

def test_error_handling():
    """Test various error conditions"""
    print("=== Testing Error Handling ===")
    
    # Test invalid session ID
    url = f"{BASE_URL}/api/v1/messages"
    data = {
        "session_id": "invalid_session_id",
        "message": "Test message"
    }
    
    response = requests.post(url, json=data)
    print(f"Invalid session ID - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test missing fields
    data = {"session_id": "session_test"}
    
    response = requests.post(url, json=data)
    print(f"Missing message field - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test unauthorized access
    url = f"{BASE_URL}/api/v1/inbox"
    response = requests.get(url)
    print(f"Unauthorized access - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print()

def main():
    """Run all tests"""
    print("Web Chat Bridge Flask API - Comprehensive Test")
    print("=" * 50)
    print()
    
    try:
        # Test basic functionality
        test_message_submission()
        test_get_responses()
        test_inbox_with_auth()
        test_outbox_with_auth()
        
        # Test admin functionality
        test_admin_sessions()
        test_admin_config()
        
        # Test advanced features
        test_rate_limiting()
        test_error_handling()
        
        print("All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the Flask server.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main()
