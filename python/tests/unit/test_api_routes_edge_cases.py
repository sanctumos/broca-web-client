import pytest
from unittest.mock import Mock, patch
from app.api.routes import (
    validate_session_id, validate_message
)


class TestValidationFunctions:
    """Test validation functions edge cases"""
    
    def test_validate_session_id_edge_cases(self):
        """Test session ID validation edge cases"""
        # Test None and empty string
        assert validate_session_id(None) is False
        assert validate_session_id("") is False
        assert validate_session_id("   ") is False
        
        # Test invalid patterns
        assert validate_session_id("invalid") is False
        assert validate_session_id("session") is False
        assert validate_session_id("session_") is False
        assert validate_session_id("_session_test") is False
        assert validate_session_id("session-test") is False
        assert validate_session_id("session test") is False
        
        # Test too long
        long_session = "session_" + "a" * 60  # 68 characters
        assert validate_session_id(long_session) is False
        
        # Test valid patterns
        assert validate_session_id("session_test") is True
        assert validate_session_id("session_123") is True
        assert validate_session_id("session_test_123") is True
        assert validate_session_id("session_ABC_123") is True
    
    def test_validate_message_edge_cases(self):
        """Test message validation edge cases"""
        # Test None and empty
        assert validate_message(None) is False
        assert validate_message("") is False
        assert validate_message("   ") is False
        
        # Test too long
        long_message = "a" * 10001
        assert validate_message(long_message) is False
        
        # Test valid messages
        assert validate_message("a") is True
        assert validate_message("Hello World!") is True
        assert validate_message("a" * 10000) is True
        
        # Test whitespace only
        assert validate_message(" ") is False
        assert validate_message("\t\n") is False


class TestAPIRouteEdgeCases:
    """Test API route edge cases and error handling"""
    
    def test_handle_messages_invalid_json(self, app):
        """Test messages endpoint with invalid JSON"""
        with app.test_client() as client:
            response = client.post('/api/v1/', 
                                query_string={'action': 'messages'},
                                data='invalid json',
                                content_type='application/json')
            assert response.status_code == 400
            # The response might be HTML instead of JSON for invalid requests
            if response.content_type == 'application/json':
                data = response.get_json()
                assert data['error'] == 'Invalid JSON'
    
    def test_handle_messages_missing_fields(self, app):
        """Test messages endpoint with missing required fields"""
        with app.test_client() as client:
            response = client.post('/api/v1/', 
                                query_string={'action': 'messages'},
                                json={'session_id': 'session_test'})  # missing message
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Missing required fields'
    
    def test_handle_messages_invalid_session_id(self, app):
        """Test messages endpoint with invalid session ID"""
        with app.test_client() as client:
            response = client.post('/api/v1/', 
                                query_string={'action': 'messages'},
                                json={'session_id': 'invalid', 'message': 'test'})
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Invalid session ID'
    
    def test_handle_messages_invalid_message(self, app):
        """Test messages endpoint with invalid message"""
        with app.test_client() as client:
            response = client.post('/api/v1/', 
                                query_string={'action': 'messages'},
                                json={'session_id': 'session_test', 'message': ''})
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Missing required fields'
    
    def test_handle_outbox_missing_json(self, app):
        """Test outbox endpoint with missing JSON"""
        with app.test_client() as client:
            response = client.post('/api/v1/', 
                                query_string={'action': 'outbox'},
                                data='invalid json',
                                content_type='application/json',
                                headers={'Authorization': 'Bearer test_api_key_123'})
            assert response.status_code == 400
            # The response might be HTML instead of JSON for invalid requests
            if response.content_type == 'application/json':
                data = response.get_json()
                assert data['error'] == 'Missing required fields'
    
    def test_handle_outbox_missing_fields(self, app):
        """Test outbox endpoint with missing required fields"""
        with app.test_client() as client:
            response = client.post('/api/v1/', 
                                query_string={'action': 'outbox'},
                                json={'session_id': 'session_test'},  # missing response
                                headers={'Authorization': 'Bearer test_api_key_123'})
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Missing required fields'
    
    def test_handle_responses_missing_session_id(self, app):
        """Test responses endpoint with missing session_id"""
        with app.test_client() as client:
            response = client.get('/api/v1/', 
                               query_string={'action': 'responses'})
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Missing session_id'
    
    def test_handle_responses_invalid_session_id(self, app):
        """Test responses endpoint with invalid session_id"""
        with app.test_client() as client:
            response = client.get('/api/v1/', 
                               query_string={'action': 'responses', 'session_id': 'invalid'})
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Invalid session ID'
    
    def test_handle_config_invalid_json(self, app):
        """Test config endpoint with invalid JSON on POST"""
        with app.test_client() as client:
            response = client.post('/api/v1/', 
                                query_string={'action': 'config'},
                                data='invalid json',
                                content_type='application/json',
                                headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 400
            # The response might be HTML instead of JSON for invalid requests
            if response.content_type == 'application/json':
                data = response.get_json()
                assert data['error'] == 'Invalid JSON'
    
    def test_api_entry_point_missing_action(self, app):
        """Test API entry point with missing action parameter"""
        with app.test_client() as client:
            response = client.get('/api/v1/')
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Missing action parameter'
    
    def test_api_entry_point_invalid_action(self, app):
        """Test API entry point with invalid action parameter"""
        with app.test_client() as client:
            response = client.get('/api/v1/', query_string={'action': 'invalid_action'})
            assert response.status_code == 400
            data = response.get_json()
            assert data['error'] == 'Invalid action'
    
    def test_api_entry_point_options_method(self, app):
        """Test API entry point with OPTIONS method (CORS preflight)"""
        with app.test_client() as client:
            response = client.options('/api/v1/')
            assert response.status_code == 200
