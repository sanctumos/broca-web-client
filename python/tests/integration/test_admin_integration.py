import pytest
import json
from tests.conftest import client, auth_headers, app_context

class TestAdminIntegration:
    """Integration tests for admin functionality"""
    
    def test_admin_interface_page(self, client, app_context):
        """Test admin interface page loads"""
        response = client.get('/admin/')
        assert response.status_code == 200
        assert b'Admin' in response.data or b'admin' in response.data.lower()
    
    def test_admin_sessions_endpoint(self, client, auth_headers, app_context):
        """Test admin sessions endpoint"""
        response = client.get('/admin/api/sessions', headers=auth_headers['admin_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'sessions' in data['data']
        assert 'pagination' in data['data']
    
    def test_admin_sessions_with_pagination(self, client, auth_headers, app_context):
        """Test admin sessions with pagination parameters"""
        response = client.get('/admin/api/sessions?limit=10&offset=0&active=true', 
                            headers=auth_headers['admin_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['pagination']['limit'] == 10
        assert data['data']['pagination']['offset'] == 0
    
    def test_admin_session_messages(self, client, auth_headers, app_context):
        """Test admin session messages endpoint"""
        # First create a session and message
        session_id = 'session_admin_test_123'
        message_data = {
            'session_id': session_id,
            'message': 'Test message for admin'
        }
        
        # Create message via API
        response = client.post('/api/v1/', 
                             query_string={'action': 'messages'},
                             json=message_data,
                             headers={'Authorization': 'Bearer test_api_key_123'})
        assert response.status_code == 200
        
        # Now get session messages via admin
        response = client.get(f'/admin/api/session_messages?session_id={session_id}', 
                            headers=auth_headers['admin_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'session' in data['data']
        assert 'messages' in data['data']
        assert 'responses' in data['data']
    
    def test_admin_session_messages_missing_session(self, client, auth_headers, app_context):
        """Test admin session messages with missing session_id"""
        response = client.get('/admin/api/session_messages', headers=auth_headers['admin_key'])
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Missing session_id' in data['error']
    
    def test_admin_session_messages_nonexistent(self, client, auth_headers, app_context):
        """Test admin session messages with non-existent session"""
        response = client.get('/admin/api/session_messages?session_id=nonexistent', 
                            headers=auth_headers['admin_key'])
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'Session not found' in data['error']
    
    def test_admin_config_get(self, client, auth_headers, app_context):
        """Test admin config retrieval"""
        response = client.get('/admin/api/config', headers=auth_headers['admin_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        # Should contain at least api_key and admin_key
        assert 'api_key' in data['data'] or 'admin_key' in data['data']
    
    def test_admin_config_update(self, client, auth_headers, app_context):
        """Test admin config update"""
        config_data = {
            'test_config_key': 'test_config_value'
        }
        
        response = client.post('/admin/api/config', 
                             json=config_data,
                             headers=auth_headers['admin_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == 'Success'
        
        # Verify the config was updated
        response = client.get('/admin/api/config', headers=auth_headers['admin_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['data'].get('test_config_key') == 'test_config_value'
    
    def test_admin_config_update_invalid_json(self, client, auth_headers, app_context):
        """Test admin config update with invalid JSON"""
        response = client.post('/admin/api/config', 
                             data='invalid json',
                             headers=auth_headers['admin_key'])
        assert response.status_code == 415  # Flask returns 415 for invalid media type
        # Flask doesn't return JSON for 415 errors, so we can't check the response body
    
    def test_admin_manual_cleanup(self, client, auth_headers, app_context):
        """Test admin manual cleanup"""
        response = client.post('/admin/api/cleanup', headers=auth_headers['admin_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == 'Success'
        assert 'cleaned_count' in data['data']
    
    def test_admin_clear_all_data(self, client, auth_headers, app_context):
        """Test admin clear all data"""
        response = client.post('/admin/api/clear_data', headers=auth_headers['admin_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == 'Success'
        assert 'cleaned_data' in data['data']
        assert 'sessions' in data['data']['cleaned_data']
        assert 'messages' in data['data']['cleaned_data']
        assert 'responses' in data['data']['cleaned_data']
    
    def test_admin_cleanup_logs(self, client, auth_headers, app_context):
        """Test admin cleanup logs"""
        response = client.post('/admin/api/cleanup_logs', headers=auth_headers['admin_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == 'Success'
        assert 'current_log_size_mb' in data['data']
        assert 'backup_files_count' in data['data']
        assert 'retention_days' in data['data']
        assert 'max_size_mb' in data['data']
    
    def test_admin_unauthorized_access(self, client, app_context):
        """Test admin endpoints without authentication"""
        # Test GET endpoints
        get_endpoints = [
            '/admin/api/sessions',
            '/admin/api/session_messages?session_id=test',
            '/admin/api/config'
        ]
        
        for endpoint in get_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
            data = response.get_json()
            assert data['success'] is False
            assert 'Authentication required' in data['error']
        
        # Test POST endpoints
        post_endpoints = [
            '/admin/api/cleanup',
            '/admin/api/clear_data',
            '/admin/api/cleanup_logs'
        ]
        
        for endpoint in post_endpoints:
            response = client.post(endpoint)
            assert response.status_code == 401
            data = response.get_json()
            assert data['success'] is False
            assert 'Authentication required' in data['error']
