import pytest
import json
from tests.conftest import client

class TestChatIntegration:
    """Integration tests for chat functionality"""
    
    def test_chat_interface_page(self, client, app_context):
        """Test chat interface page loads"""
        response = client.get('/chat/')
        assert response.status_code == 200
        assert b'Chat' in response.data or b'chat' in response.data.lower()
    
    def test_chat_widget_js(self, client, app_context):
        """Test chat widget JavaScript loads"""
        response = client.get('/chat/widget.js')
        assert response.status_code == 200
        assert 'application/javascript' in response.content_type
        # Should contain some JavaScript content
        assert len(response.data) > 0
    
    def test_chat_send_message_success(self, client, app_context):
        """Test successful message sending via chat interface"""
        message_data = {
            'session_id': 'chat_test_session_123',
            'message': 'Hello from chat interface!'
        }
        
        response = client.post('/chat/api/send_message', 
                             json=message_data,
                             headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'message_id' in data['data']
        assert data['data']['session_id'] == 'chat_test_session_123'
        assert 'uid' in data['data']
    
    def test_chat_send_message_existing_session(self, client, app_context):
        """Test sending message to existing session"""
        session_id = 'chat_existing_session_456'
        
        # Send first message
        message_data = {
            'session_id': session_id,
            'message': 'First message'
        }
        response = client.post('/chat/api/send_message', 
                             json=message_data,
                             headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        
        # Send second message to same session
        message_data = {
            'session_id': session_id,
            'message': 'Second message'
        }
        response = client.post('/chat/api/send_message', 
                             json=message_data,
                             headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['session_id'] == session_id
    
    def test_chat_send_message_missing_json(self, client, app_context):
        """Test message sending with missing JSON"""
        response = client.post('/chat/api/send_message', 
                             data='not json',
                             headers={'Content-Type': 'text/plain'})
        # Flask returns 415 for unsupported media type when expecting JSON
        assert response.status_code == 415
        # No JSON response for 415 errors
        assert response.get_json() is None
    
    def test_chat_send_message_missing_session_id(self, client, app_context):
        """Test message sending with missing session_id"""
        message_data = {
            'message': 'Hello without session'
        }
        
        response = client.post('/chat/api/send_message', 
                             json=message_data,
                             headers={'Content-Type': 'application/json'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Missing required fields' in data['error']
    
    def test_chat_send_message_missing_message(self, client):
        """Test message sending with missing message"""
        message_data = {
            'session_id': 'chat_test_session_789'
        }
        
        response = client.post('/chat/api/send_message', 
                             json=message_data,
                             headers={'Content-Type': 'application/json'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Missing required fields' in data['error']
    
    def test_chat_send_message_empty_fields(self, client, app_context):
        """Test message sending with empty fields"""
        message_data = {
            'session_id': '',
            'message': 'Hello with empty session'
        }
        
        response = client.post('/chat/api/send_message', 
                             json=message_data,
                             headers={'Content-Type': 'application/json'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Missing required fields' in data['error']
    
    def test_chat_get_responses_success(self, client, app_context):
        """Test successful response retrieval"""
        session_id = 'chat_responses_session_123'
        
        # First send a message to create session
        message_data = {
            'session_id': session_id,
            'message': 'Message to get responses for'
        }
        response = client.post('/chat/api/send_message', 
                             json=message_data,
                             headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        
        # Now get responses
        response = client.get(f'/chat/api/get_responses?session_id={session_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['session_id'] == session_id
        assert 'responses' in data['data']
    
    def test_chat_get_responses_with_since(self, client, app_context):
        """Test response retrieval with since parameter"""
        session_id = 'chat_since_session_456'
        
        # First send a message to create session
        message_data = {
            'session_id': session_id,
            'message': 'Message for since test'
        }
        response = client.post('/chat/api/send_message', 
                             json=message_data,
                             headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        
        # Get responses with since parameter
        since_time = '2024-01-01T00:00:00Z'
        response = client.get(f'/chat/api/get_responses?session_id={session_id}&since={since_time}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['session_id'] == session_id
    
    def test_chat_get_responses_missing_session_id(self, client, app_context):
        """Test response retrieval with missing session_id"""
        response = client.get('/chat/api/get_responses')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Missing session_id' in data['error']
    
    def test_chat_get_responses_nonexistent_session(self, client, app_context):
        """Test response retrieval for non-existent session"""
        response = client.get('/chat/api/get_responses?session_id=nonexistent_session')
        assert response.status_code == 200  # Should create session if doesn't exist
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['session_id'] == 'nonexistent_session'
        assert len(data['data']['responses']) == 0  # No responses for new session
    
    def test_chat_session_creation_automatic(self, client, app_context):
        """Test that sessions are created automatically when needed"""
        session_id = 'auto_created_session_789'
        
        # Try to get responses for non-existent session
        response = client.get(f'/chat/api/get_responses?session_id={session_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['session_id'] == session_id
        
        # Now send a message to the same session
        message_data = {
            'session_id': session_id,
            'message': 'Message to auto-created session'
        }
        response = client.post('/chat/api/send_message', 
                             json=message_data,
                             headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['session_id'] == session_id
    
    def test_chat_multiple_messages_same_session(self, client, app_context):
        """Test sending multiple messages to the same session"""
        session_id = 'multi_message_session_123'
        
        messages = [
            'First message',
            'Second message',
            'Third message'
        ]
        
        for i, message in enumerate(messages):
            message_data = {
                'session_id': session_id,
                'message': message
            }
            response = client.post('/chat/api/send_message', 
                                 json=message_data,
                                 headers={'Content-Type': 'application/json'})
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['session_id'] == session_id
            assert 'message_id' in data['data']
            assert 'uid' in data['data']
    
    def test_chat_concurrent_sessions(self, client, app_context):
        """Test handling multiple concurrent sessions"""
        session_ids = [
            'concurrent_session_1',
            'concurrent_session_2',
            'concurrent_session_3'
        ]
        
        for session_id in session_ids:
            message_data = {
                'session_id': session_id,
                'message': f'Message to {session_id}'
            }
            response = client.post('/chat/api/send_message', 
                                 json=message_data,
                                 headers={'Content-Type': 'application/json'})
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['session_id'] == session_id
        
        # Verify all sessions exist by getting responses
        for session_id in session_ids:
            response = client.get(f'/chat/api/get_responses?session_id={session_id}')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['session_id'] == session_id
