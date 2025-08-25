"""
Integration tests for Web Chat Bridge Flask API
Tests complete API workflows with real database interactions
"""

import pytest
import json
import time
from app import create_app

class TestAPIIntegration:
    """Test complete API workflows"""
    
    def test_complete_message_workflow(self, client, test_db):
        """Test complete message submission and retrieval workflow"""
        # 1. Submit a message
        message_data = {
            'session_id': 'session_integration_test',
            'message': 'Integration test message'
        }
        
        response = client.post('/api/v1/?action=messages', 
                             json=message_data,
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        assert data['data']['message_id'] is not None
        assert data['data']['is_new_user'] is True
        
        message_id = data['data']['message_id']
        uid = data['data']['uid']
        
        # 2. Submit a response via outbox
        response_data = {
            'session_id': 'session_integration_test',
            'response': 'Integration test response'
        }
        
        response = client.post('/api/v1/?action=outbox',
                             json=response_data,
                             headers={'Authorization': 'Bearer test_api_key_123'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        assert data['data']['response_id'] is not None
        
        # 3. Retrieve responses for the session
        response = client.get('/api/v1/',
                            query_string={'action': 'responses', 'session_id': 'session_integration_test'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        assert len(data['data']['responses']) == 1
        assert data['data']['responses'][0]['response'] == 'Integration test response'
        
        # 4. Check inbox (should show the message as processed)
        response = client.get('/api/v1/',
                            query_string={'action': 'inbox'},
                            headers={'Authorization': 'Bearer test_api_key_123'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        # Message should be marked as processed, so inbox might be empty
        # But the response should be in the session
    
    def test_session_management_workflow(self, client, test_db):
        """Test complete session management workflow"""
        # 1. Create multiple sessions with messages
        sessions = ['session_1', 'session_2', 'session_3']
        
        for session_id in sessions:
            message_data = {
                'session_id': session_id,
                'message': f'Message for {session_id}'
            }
            
            response = client.post('/api/v1/?action=messages',
                                 json=message_data,
                                 headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 200
        
        # 2. Check admin sessions endpoint
        response = client.get('/api/v1/',
                            query_string={'action': 'sessions'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        assert len(data['data']['sessions']) >= 3  # At least our 3 sessions
        
        # 3. Check pagination
        response = client.get('/api/v1/',
                            query_string={'action': 'sessions', 'limit': '2', 'offset': '0'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        assert len(data['data']['sessions']) <= 2
        assert data['data']['pagination']['has_more'] is True
    
    def test_configuration_workflow(self, client, test_db):
        """Test configuration management workflow"""
        # 1. Get current configuration
        response = client.get('/api/v1/',
                            query_string={'action': 'config'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        original_config = data['data']
        
        # 2. Update configuration
        new_config = {
            'test_setting': 'test_value',
            'another_setting': 'another_value'
        }
        
        response = client.post('/api/v1/',
                             query_string={'action': 'config'},
                             json=new_config,
                             headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        
        # 3. Verify configuration was updated
        response = client.get('/api/v1/',
                            query_string={'action': 'config'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        updated_config = data['data']
        
        # Check that new settings were added
        assert 'test_setting' in updated_config
        assert updated_config['test_setting'] == 'test_value'
        assert 'another_setting' in updated_config
        assert updated_config['another_setting'] == 'another_value'
        
        # Check that original settings are preserved
        for key, value in original_config.items():
            if key not in new_config:
                assert key in updated_config
                assert updated_config[key] == value
    
    def test_rate_limiting_integration(self, client, test_db):
        """Test rate limiting in real API calls"""
        # 1. Make multiple requests to trigger rate limiting
        endpoint = '/api/v1/'
        headers = {'Content-Type': 'application/json'}
        
        # First request should succeed
        message_data = {
            'session_id': 'session_rate_test_1',
            'message': 'Rate test message 1'
        }
        
        response = client.post(endpoint, 
                             query_string={'action': 'messages'},
                             json=message_data, 
                             headers=headers)
        assert response.status_code == 200
        
        # Make many requests quickly to hit rate limit
        for i in range(60):  # More than the 50 limit
            message_data = {
                'session_id': f'session_rate_test_{i+2}',
                'message': f'Rate test message {i+2}'
            }
            
            response = client.post(endpoint, 
                                 query_string={'action': 'messages'},
                                 json=message_data, 
                                 headers=headers)
            
            # Check if we hit the rate limit
            if response.status_code == 429:  # Rate limit hit
                break
        else:
            # If we didn't break, the last response should be 429
            # This means we need to make more requests to hit the limit
            for i in range(60, 100):  # Make more requests
                message_data = {
                    'session_id': f'session_rate_test_{i+2}',
                    'message': f'Rate test message {i+2}'
                }
                
                response = client.post(endpoint, 
                                     query_string={'action': 'messages'},
                                     json=message_data, 
                                     headers=headers)
                
                if response.status_code == 429:  # Rate limit hit
                    break
        
        # Should eventually hit rate limit
        assert response.status_code == 429
        data = json.loads(response.get_data(as_text=True))
        assert 'Rate limit exceeded' in data['error']
    
    def test_error_handling_integration(self, client, test_db):
        """Test error handling in real API calls"""
        # 1. Test invalid session ID
        message_data = {
            'session_id': 'invalid_session_id',
            'message': 'Test message'
        }
        
        response = client.post('/api/v1/?action=messages',
                             json=message_data,
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is False
        assert 'Invalid session ID' in data['error']
        
        # 2. Test missing required fields
        message_data = {'session_id': 'session_test'}
        
        response = client.post('/api/v1/?action=messages',
                             json=message_data,
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is False
        assert 'Missing required fields' in data['error']
        
        # 3. Test unauthorized access
        response = client.get('/api/v1/?action=inbox')
        assert response.status_code == 401
        
        # 4. Test invalid action
        response = client.get('/api/v1/?action=invalid_action')
        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is False
        assert 'Invalid action' in data['error']
    
    def test_pagination_integration(self, client, test_db):
        """Test pagination functionality"""
        # 1. Create many messages for pagination testing
        for i in range(25):  # Create 25 messages
            message_data = {
                'session_id': f'session_pagination_{i//5}',  # 5 messages per session
                'message': f'Pagination test message {i+1}'
            }
            
            response = client.post('/api/v1/?action=messages',
                                 json=message_data,
                                 headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 200
        
        # 2. Test pagination with different limits
        for limit in [5, 10, 15]:
            response = client.get('/api/v1/',
                                query_string={'action': 'inbox', 'limit': limit, 'offset': 0},
                                headers={'Authorization': 'Bearer test_api_key_123'})
            
            assert response.status_code == 200
            data = json.loads(response.get_data(as_text=True))
            assert data['success'] is True
            assert len(data['data']['messages']) <= limit
            assert data['data']['pagination']['limit'] == limit
        
        # 3. Test offset functionality
        response = client.get('/api/v1/',
                            query_string={'action': 'inbox', 'limit': 10, 'offset': 10},
                            headers={'Authorization': 'Bearer test_api_key_123'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        assert data['data']['pagination']['offset'] == 10
    
    def test_concurrent_session_handling(self, client, test_db):
        """Test handling multiple concurrent sessions"""
        # 1. Create multiple sessions simultaneously
        session_data = []
        for i in range(10):
            session_data.append({
                'session_id': f'session_concurrent_{i}',
                'message': f'Concurrent message {i}'
            })
        
        # Submit all messages
        responses = []
        for i, data in enumerate(session_data):
            response = client.post('/api/v1/',
                                 query_string={'action': 'messages'},
                                 json=data,
                                 headers={'Content-Type': 'application/json'})
            responses.append(response)
            
            # Debug: print response details for failed requests
            if response.status_code != 200:
                print(f"Request {i} failed with status {response.status_code}")
                print(f"Response data: {response.get_data(as_text=True)}")
                print(f"Request data: {data}")
        
        # All should succeed
        for i, response in enumerate(responses):
            if response.status_code != 200:
                print(f"Response {i} failed: {response.status_code} - {response.get_data(as_text=True)}")
            assert response.status_code == 200
        
        # 2. Verify all sessions were created
        response = client.get('/api/v1/',
                            query_string={'action': 'sessions'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        
        # Should have at least our 10 sessions
        session_ids = [s['id'] for s in data['data']['sessions']]
        for i in range(10):
            expected_session = f'session_concurrent_{i}'
            assert expected_session in session_ids
    
    def test_data_consistency(self, client, test_db):
        """Test data consistency across API calls"""
        # 1. Create a message
        message_data = {
            'session_id': 'session_consistency_test',
            'message': 'Consistency test message'
        }
        
        response = client.post('/api/v1/',
                             query_string={'action': 'messages'},
                             json=message_data,
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        message_id = data['data']['message_id']
        uid = data['data']['uid']
        
        # 2. Verify message appears in inbox
        response = client.get('/api/v1/',
                            query_string={'action': 'inbox'},
                            headers={'Authorization': 'Bearer test_api_key_123'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        
        # Find our message
        found_message = None
        for msg in data['data']['messages']:
            if msg['id'] == message_id:
                found_message = msg
                break
        
        assert found_message is not None
        assert found_message['session_id'] == 'session_consistency_test'
        assert found_message['message'] == 'Consistency test message'
        assert found_message['uid'] == uid
        
        # 3. Submit a response
        response_data = {
            'session_id': 'session_consistency_test',
            'response': 'Consistency test response'
        }
        
        response = client.post('/api/v1/',
                             query_string={'action': 'outbox'},
                             json=response_data,
                             headers={'Content-Type': 'application/json', 'Authorization': 'Bearer test_api_key_123'})
        
        assert response.status_code == 200
        
        # 4. Verify response appears in responses
        response = client.get('/api/v1/',
                            query_string={'action': 'responses', 'session_id': 'session_consistency_test'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        assert len(data['data']['responses']) > 0
