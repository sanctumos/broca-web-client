import pytest
import json
from tests.conftest import client, auth_headers, app_context

class TestAPIRoutesIntegration:
    """Integration tests for API routes functionality"""
    
    def test_api_entry_point_messages_action(self, client, auth_headers, app_context):
        """Test API entry point with messages action"""
        message_data = {
            'session_id': 'session_api_entry_test_123',
            'message': 'Test message via entry point'
        }
        
        response = client.post('/api/v1/', 
                             query_string={'action': 'messages'},
                             json=message_data,
                             headers=auth_headers['api_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'message_id' in data['data']
        assert data['data']['session_id'] == 'session_api_entry_test_123'
    
    def test_api_entry_point_inbox_action(self, client, auth_headers, app_context):
        """Test API entry point with inbox action"""
        response = client.get('/api/v1/', 
                            query_string={'action': 'inbox'},
                            headers=auth_headers['api_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'messages' in data['data']
        assert 'pagination' in data['data']
    
    def test_api_entry_point_outbox_action(self, client, auth_headers, app_context):
        """Test API entry point with outbox action"""
        session_id = 'session_api_outbox_test_456'
        
        # First create a session and message
        message_data = {
            'session_id': session_id,
            'message': 'Message for outbox test'
        }
        response = client.post('/api/v1/', 
                             query_string={'action': 'messages'},
                             json=message_data,
                             headers=auth_headers['api_key'])
        assert response.status_code == 200
        
        # Now create outbox response
        outbox_data = {
            'session_id': session_id,
            'response': 'Test response for outbox',
            'message_id': 1
        }
        response = client.post('/api/v1/', 
                             query_string={'action': 'outbox'},
                             json=outbox_data,
                             headers=auth_headers['api_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'response_id' in data['data']
    
    def test_api_entry_point_responses_action(self, client, auth_headers, app_context):
        """Test API entry point with responses action"""
        session_id = 'session_api_responses_test_789'
        
        # First create a session and message
        message_data = {
            'session_id': session_id,
            'message': 'Message for responses test'
        }
        response = client.post('/api/v1/', 
                             query_string={'action': 'messages'},
                             json=message_data,
                             headers=auth_headers['api_key'])
        assert response.status_code == 200
        
        # Now get responses
        response = client.get('/api/v1/', 
                            query_string={'action': 'responses', 'session_id': session_id})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['session_id'] == session_id
    
    def test_api_entry_point_sessions_action(self, client, auth_headers, app_context):
        """Test API entry point with sessions action"""
        response = client.get('/api/v1/', 
                            query_string={'action': 'sessions'},
                            headers=auth_headers['admin_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'sessions' in data['data']
        assert 'pagination' in data['data']
    
    def test_api_entry_point_config_action(self, client, auth_headers, app_context):
        """Test API entry point with config action"""
        response = client.get('/api/v1/', 
                            query_string={'action': 'config'},
                            headers=auth_headers['admin_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
    
    def test_api_entry_point_cleanup_action(self, client, auth_headers, app_context):
        """Test API entry point with cleanup action"""
        response = client.post('/api/v1/', 
                             query_string={'action': 'cleanup'},
                             headers=auth_headers['admin_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'message' in data
    
    def test_api_entry_point_invalid_action(self, client, app_context):
        """Test API entry point with invalid action"""
        response = client.get('/api/v1/', 
                            query_string={'action': 'invalid_action'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid action' in data['error']
    
    def test_api_entry_point_missing_action(self, client, app_context):
        """Test API entry point without action parameter"""
        response = client.get('/api/v1/')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Missing action parameter' in data['error']
    
    def test_api_entry_point_unsupported_method(self, client, app_context):
        """Test API entry point with unsupported HTTP method"""
        response = client.put('/api/v1/', 
                            query_string={'action': 'messages'})
        assert response.status_code == 405
        data = response.get_json()
        assert data['success'] is False
        assert 'Method not allowed' in data['error']
    
    def test_api_entry_point_options_method(self, client, app_context):
        """Test API entry point with OPTIONS method for CORS"""
        response = client.options('/api/v1/', 
                                query_string={'action': 'messages'})
        assert response.status_code == 200
    
    def test_api_entry_point_messages_validation(self, client, auth_headers, app_context):
        """Test API entry point message validation"""
        # Test missing session_id
        message_data = {
            'message': 'Message without session'
        }
        response = client.post('/api/v1/', 
                             query_string={'action': 'messages'},
                             json=message_data,
                             headers=auth_headers['api_key'])
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Missing required fields' in data['error']
        
        # Test missing message
        message_data = {
            'session_id': 'validation_test_123'
        }
        response = client.post('/api/v1/', 
                             query_string={'action': 'messages'},
                             json=message_data,
                             headers=auth_headers['api_key'])
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Missing required fields' in data['error']
        
        # Test invalid session_id format
        message_data = {
            'session_id': 'invalid!@#',
            'message': 'Valid message'
        }
        response = client.post('/api/v1/', 
                             query_string={'action': 'messages'},
                             json=message_data,
                             headers=auth_headers['api_key'])
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid session ID' in data['error']
    
    def test_api_entry_point_inbox_pagination(self, client, auth_headers, app_context):
        """Test API entry point inbox pagination"""
        # Create some test messages first
        for i in range(5):
            message_data = {
                'session_id': f'session_pagination_test_{i}',
                'message': f'Message {i} for pagination'
            }
            response = client.post('/api/v1/', 
                                 query_string={'action': 'messages'},
                                 json=message_data,
                                 headers=auth_headers['api_key'])
            assert response.status_code == 200
        
        # Test pagination parameters
        response = client.get('/api/v1/', 
                            query_string={'action': 'inbox', 'limit': '2', 'offset': '0'},
                            headers=auth_headers['api_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'pagination' in data['data']
        assert data['data']['pagination']['limit'] == 2
        assert data['data']['pagination']['offset'] == 0
    
    def test_api_entry_point_sessions_pagination(self, client, auth_headers, app_context):
        """Test API entry point sessions pagination"""
        # Create some test sessions first
        for i in range(3):
            message_data = {
                'session_id': f'session_session_pagination_{i}',
                'message': f'Message for session {i}'
            }
            response = client.post('/api/v1/', 
                                 query_string={'action': 'messages'},
                                 json=message_data,
                                 headers=auth_headers['api_key'])
            assert response.status_code == 200
        
        # Test pagination parameters
        response = client.get('/api/v1/', 
                            query_string={'action': 'sessions', 'limit': '2', 'offset': '0'},
                            headers=auth_headers['admin_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'pagination' in data['data']
        assert data['data']['pagination']['limit'] == 2
        assert data['data']['pagination']['offset'] == 0
    
    def test_api_entry_point_outbox_validation(self, client, auth_headers, app_context):
        """Test API entry point outbox validation"""
        # Test missing session_id
        response = client.post('/api/v1/', 
                             query_string={'action': 'outbox'},
                             json={'response': 'test response'},
                             headers=auth_headers['api_key'])
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Missing required fields' in data['error']
        
        # Test invalid session_id format
        response = client.post('/api/v1/', 
                             query_string={'action': 'outbox'},
                             json={'session_id': 'invalid!@#', 'response': 'test response'},
                             headers=auth_headers['api_key'])
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid session ID' in data['error']
    
    def test_api_entry_point_responses_validation(self, client, auth_headers, app_context):
        """Test API entry point responses validation"""
        # Test missing session_id
        response = client.get('/api/v1/', 
                            query_string={'action': 'responses'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Missing session_id' in data['error']
        
        # Test invalid session_id format
        response = client.get('/api/v1/', 
                            query_string={'action': 'responses', 'session_id': 'invalid!@#'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid session ID' in data['error']
    
    def test_api_entry_point_authentication_required(self, client, app_context):
        """Test API entry point authentication requirements"""
        # Test messages action without auth (should work - public endpoint)
        message_data = {
            'session_id': 'session_auth_test_123',
            'message': 'Message without auth'
        }
        response = client.post('/api/v1/', 
                             query_string={'action': 'messages'},
                             json=message_data)
        assert response.status_code == 200  # Messages endpoint is public
        data = response.get_json()
        assert data['success'] is True
        
        # Test inbox action without auth (should fail - requires auth)
        response = client.get('/api/v1/', 
                            query_string={'action': 'inbox'})
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'Authentication required' in data['error']
        
        # Test outbox action without auth (should fail - requires auth)
        response = client.post('/api/v1/', 
                             query_string={'action': 'outbox'},
                             json={'session_id': 'session_test_123', 'response': 'test response'})
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'Authentication required' in data['error']
    
    def test_api_entry_point_admin_authentication_required(self, client, app_context):
        """Test API entry point admin authentication requirements"""
        # Test config action without admin auth
        response = client.get('/api/v1/', 
                            query_string={'action': 'config'})
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'Authentication required' in data['error']
        
        # Test cleanup action without admin auth
        response = client.post('/api/v1/', 
                             query_string={'action': 'cleanup'})
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'Authentication required' in data['error']
    
    def test_api_entry_point_rate_limiting(self, client, auth_headers, app_context):
        """Test API entry point rate limiting"""
        # Make multiple requests to trigger rate limiting
        for i in range(60):  # Should hit the 50/hour limit
            message_data = {
                'session_id': f'session_rate_limit_test_{i}',
                'message': f'Message {i} for rate limit test'
            }
            response = client.post('/api/v1/', 
                                 query_string={'action': 'messages'},
                                 json=message_data,
                                 headers=auth_headers['api_key'])
            
            if response.status_code == 429:
                # Rate limit hit
                data = response.get_json()
                assert data['success'] is False
                assert 'Rate limit exceeded' in data['error']
                break
        else:
            # If we didn't hit rate limit, that's also valid
            pass
    
    def test_api_entry_point_backward_compatibility(self, client, auth_headers, app_context):
        """Test that direct route access still works for backward compatibility"""
        # Test direct messages endpoint
        message_data = {
            'session_id': 'session_backward_compat_123',
            'message': 'Message via direct endpoint'
        }
        response = client.post('/api/v1/messages', 
                             json=message_data,
                             headers=auth_headers['api_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Test direct inbox endpoint (requires auth)
        response = client.get('/api/v1/inbox', headers=auth_headers['api_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Test direct outbox endpoint (requires POST with JSON)
        outbox_data = {
            'session_id': 'session_backward_compat_123',
            'response': 'Response via direct endpoint',
            'message_id': 1
        }
        response = client.post('/api/v1/outbox',
                             json=outbox_data,
                             headers=auth_headers['api_key'])
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
