"""
End-to-End tests for Web Chat Bridge Flask API
Tests complete user workflows from start to finish
"""

import pytest
import json
import time
from app import create_app

class TestE2EUserWorkflows:
    """Test complete end-to-end user workflows"""
    
    def test_complete_chat_workflow(self, client, test_db):
        """Test complete chat workflow from user message to admin response"""
        # 1. User submits initial message
        user_message = {
            'session_id': 'session_e2e_chat',
            'message': 'Hello, I need help with my account'
        }
        
        response = client.post('/api/v1/',
                             query_string={'action': 'messages'},
                             json=user_message,
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        assert data['data']['is_new_user'] is True
        
        message_id = data['data']['message_id']
        uid = data['data']['uid']
        
        # 2. Admin checks inbox for new messages
        response = client.get('/api/v1/',
                            query_string={'action': 'inbox'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        
        # Find our message in the inbox
        found_message = None
        for msg in data['data']['messages']:
            if msg['id'] == message_id:
                found_message = msg
                break
        
        assert found_message is not None
        assert found_message['message'] == 'Hello, I need help with my account'
        assert found_message['session_id'] == 'session_e2e_chat'
        assert found_message['uid'] == uid
        
        # 3. Admin responds via outbox
        admin_response = {
            'session_id': 'session_e2e_chat',
            'response': 'Hello! I can help you with your account. What specific issue are you experiencing?'
        }
        
        response = client.post('/api/v1/',
                             query_string={'action': 'outbox'},
                             json=admin_response,
                             headers={'Content-Type': 'application/json', 'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        response_id = data['data']['response_id']
        
        # 4. User checks for responses
        response = client.get('/api/v1/',
                            query_string={'action': 'responses', 'session_id': 'session_e2e_chat'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        assert len(data['data']['responses']) == 1
        assert data['data']['responses'][0]['response'] == 'Hello! I can help you with your account. What specific issue are you experiencing?'
        
        # 5. User sends follow-up message
        follow_up_message = {
            'session_id': 'session_e2e_chat',
            'message': 'I cannot log in to my account'
        }
        
        response = client.post('/api/v1/',
                             query_string={'action': 'messages'},
                             json=follow_up_message,
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['data']['is_new_user'] is False  # Should be existing user now
        
        # 6. Admin sees follow-up in inbox
        response = client.get('/api/v1/',
                            query_string={'action': 'inbox'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        
        # Should have the follow-up message
        follow_up_found = False
        for msg in data['data']['messages']:
            if msg['message'] == 'I cannot log in to my account':
                follow_up_found = True
                break
        
        assert follow_up_found is True
        
        # 7. Admin provides final response
        final_response = {
            'session_id': 'session_e2e_chat',
            'response': 'I understand the issue. Let me reset your password. Please check your email for a reset link.'
        }
        
        response = client.post('/api/v1/',
                             query_string={'action': 'outbox'},
                             json=final_response,
                             headers={'Content-Type': 'application/json', 'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        
        # 8. Verify complete conversation
        response = client.get('/api/v1/',
                            query_string={'action': 'responses', 'session_id': 'session_e2e_chat'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert len(data['data']['responses']) == 2  # Should have 2 responses now
        
        # Check response order
        responses = data['data']['responses']
        assert responses[0]['response'] == 'Hello! I can help you with your account. What specific issue are you experiencing?'
        assert responses[1]['response'] == 'I understand the issue. Let me reset your password. Please check your email for a reset link.'
    
    def test_multiple_concurrent_users(self, client, test_db):
        """Test handling multiple concurrent users with different sessions"""
        # 1. Create multiple user sessions
        users = [
            {'session_id': 'session_user_1', 'message': 'User 1 needs help'},
            {'session_id': 'session_user_2', 'message': 'User 2 has a question'},
            {'session_id': 'session_user_3', 'message': 'User 3 needs support'}
        ]
        
        # Submit all messages
        for user in users:
            response = client.post('/api/v1/',
                                 query_string={'action': 'messages'},
                                 json=user,
                                 headers={'Content-Type': 'application/json'})
            assert response.status_code == 200
        
        # 2. Admin processes all messages
        response = client.get('/api/v1/',
                            query_string={'action': 'inbox'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert len(data['data']['messages']) >= 3
        
        # 3. Admin responds to each user
        responses = [
            {'session_id': 'session_user_1', 'response': 'Hello User 1, how can I help?'},
            {'session_id': 'session_user_2', 'response': 'Hello User 2, what is your question?'},
            {'session_id': 'session_user_3', 'response': 'Hello User 3, I am here to support you'}
        ]
        
        for resp in responses:
            response = client.post('/api/v1/',
                                 query_string={'action': 'outbox'},
                                 json=resp,
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 200
        
        # 4. Verify each user can see their responses
        for user in users:
            response = client.get('/api/v1/',
                                query_string={'action': 'responses', 'session_id': user['session_id']})
            
            assert response.status_code == 200
            data = json.loads(response.get_data(as_text=True))
            assert len(data['data']['responses']) == 1
            
            # Find the matching response
            expected_response = None
            for resp in responses:
                if resp['session_id'] == user['session_id']:
                    expected_response = resp['response']
                    break
            
            assert data['data']['responses'][0]['response'] == expected_response
    
    def test_admin_session_monitoring(self, client, test_db):
        """Test admin monitoring of active sessions"""
        # 1. Create several active sessions
        sessions = []
        for i in range(5):
            session_data = {
                'session_id': f'session_admin_monitor_{i}',
                'message': f'Message for session {i}'
            }
            
            response = client.post('/api/v1/',
                                 query_string={'action': 'messages'},
                                 json=session_data,
                                 headers={'Content-Type': 'application/json'})
            assert response.status_code == 200
            sessions.append(session_data)
        
        # 2. Admin checks active sessions
        response = client.get('/api/v1/',
                            query_string={'action': 'sessions'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        assert len(data['data']['sessions']) >= 5
        
        # 3. Verify session details
        session_ids = [s['id'] for s in data['data']['sessions']]
        for session in sessions:
            assert session['session_id'] in session_ids
        
        # 4. Check pagination
        response = client.get('/api/v1/',
                            query_string={'action': 'sessions', 'limit': '3', 'offset': '0'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert len(data['data']['sessions']) <= 3
        assert data['data']['pagination']['has_more'] is True
        
        # 5. Check second page
        response = client.get('/api/v1/',
                            query_string={'action': 'sessions', 'limit': '3', 'offset': '3'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert len(data['data']['sessions']) <= 3
    
    def test_configuration_management_workflow(self, client, test_db):
        """Test complete configuration management workflow"""
        # 1. Admin gets current configuration
        response = client.get('/api/v1/',
                            query_string={'action': 'config'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        original_config = data['data'].copy()
        
        # 2. Admin updates multiple configuration values
        config_updates = {
            'max_message_length': '15000',
            'session_timeout': '3600',
            'custom_setting': 'custom_value',
            'feature_flag': 'enabled'
        }
        
        response = client.post('/api/v1/',
                             query_string={'action': 'config'},
                             json=config_updates,
                             headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        
        # 3. Verify all updates were applied
        response = client.get('/api/v1/',
                            query_string={'action': 'config'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        updated_config = data['data']
        
        # Check new values
        assert updated_config['max_message_length'] == '15000'
        assert updated_config['session_timeout'] == '3600'
        assert updated_config['custom_setting'] == 'custom_value'
        assert updated_config['feature_flag'] == 'enabled'
        
        # Check original values are preserved
        for key, value in original_config.items():
            if key not in config_updates:
                assert key in updated_config
                assert updated_config[key] == value
        
        # 4. Test configuration validation (if implemented)
        # This would test that invalid configuration values are rejected
        
        # 5. Test configuration rollback
        rollback_config = {
            'max_message_length': '10000',
            'session_timeout': '1800'
        }
        
        response = client.post('/api/v1/',
                             query_string={'action': 'config'},
                             json=rollback_config,
                             headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        
        # Verify rollback
        response = client.get('/api/v1/',
                            query_string={'action': 'config'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        final_config = data['data']
        
        assert final_config['max_message_length'] == '10000'
        assert final_config['session_timeout'] == '1800'
    
    def test_error_recovery_workflow(self, client, test_db):
        """Test system recovery from various error conditions"""
        # 1. Test invalid session ID recovery
        invalid_message = {
            'session_id': 'invalid_session_id',
            'message': 'This should fail'
        }
        
        response = client.post('/api/v1/',
                             query_string={'action': 'messages'},
                             json=invalid_message,
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 400
        
        # 2. Test valid message after error (should work)
        valid_message = {
            'session_id': 'session_error_recovery',
            'message': 'This should work after the error'
        }
        
        response = client.post('/api/v1/',
                             query_string={'action': 'messages'},
                             json=valid_message,
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200
        
        # 3. Test authentication error recovery
        response = client.get('/api/v1/',
                            query_string={'action': 'inbox'})
        assert response.status_code == 401
        
        # 4. Test with valid authentication (should work)
        response = client.get('/api/v1/',
                            query_string={'action': 'inbox'},
                            headers={'Authorization': 'Bearer test_api_key_123'})
        
        assert response.status_code == 200
        
        # 5. Test invalid action recovery
        response = client.get('/api/v1/',
                            query_string={'action': 'nonexistent_action'})
        assert response.status_code == 400
        
        # 6. Test valid action after error (should work)
        response = client.get('/api/v1/',
                            query_string={'action': 'inbox'},
                            headers={'Authorization': 'Bearer test_api_key_123'})
        
        assert response.status_code == 200
    
    def test_performance_under_load(self, client, test_db):
        """Test system performance under load"""
        # 1. Create many sessions quickly
        start_time = time.time()
        
        for i in range(50):
            message_data = {
                'session_id': f'session_load_test_{i}',
                'message': f'Load test message {i}'
            }
            
            response = client.post('/api/v1/',
                                 query_string={'action': 'messages'},
                                 json=message_data,
                                 headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 50 requests in reasonable time (less than 10 seconds)
        assert total_time < 10.0
        
        # 2. Test inbox retrieval under load
        start_time = time.time()
        
        response = client.get('/api/v1/',
                            query_string={'action': 'inbox'},
                            headers={'Authorization': 'Bearer test_api_key_123'})
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # Should respond quickly (less than 2 seconds)
        assert response_time < 2.0
        
        # 3. Test session monitoring under load
        start_time = time.time()
        
        response = client.get('/api/v1/',
                            query_string={'action': 'sessions'},
                            headers={'Authorization': 'Bearer test_admin_key_456'})
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # Should respond quickly even with many sessions
        assert response_time < 2.0
        
        # 4. Verify data integrity under load
        data = json.loads(response.get_data(as_text=True))
        assert data['success'] is True
        assert len(data['data']['sessions']) >= 50  # Should have all our sessions
        
        # Check that all session IDs are present
        session_ids = [s['id'] for s in data['data']['sessions']]
        for i in range(50):
            expected_session = f'session_load_test_{i}'
            assert expected_session in session_ids
    
    def test_data_persistence_across_restarts(self, client, test_db):
        """Test that data persists correctly across application restarts"""
        # 1. Create persistent data
        persistent_message = {
            'session_id': 'session_persistent',
            'message': 'This message should persist'
        }
        
        response = client.post('/api/v1/',
                             query_string={'action': 'messages'},
                             json=persistent_message,
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 200
        message_id = response.json['data']['message_id']
        
        # 2. Add a response
        persistent_response = {
            'session_id': 'session_persistent',
            'response': 'This response should also persist'
        }
        
        response = client.post('/api/v1/',
                             query_string={'action': 'outbox'},
                             json=persistent_response,
                             headers={'Content-Type': 'application/json', 'Authorization': 'Bearer test_api_key_123'})
        
        assert response.status_code == 200
        
        # 3. Verify data exists
        response = client.get('/api/v1/',
                            query_string={'action': 'responses', 'session_id': 'session_persistent'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert len(data['data']['responses']) == 1
        
        # 4. Simulate application restart by recreating client
        # (In real scenario, this would be a full app restart)
        new_client = client.application.test_client()
        
        # 5. Verify data still exists after "restart"
        response = new_client.get('/api/v1/',
                                 query_string={'action': 'responses', 'session_id': 'session_persistent'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert len(data['data']['responses']) == 1
        assert data['data']['responses'][0]['response'] == 'This response should also persist'
        
        # 6. Verify session still exists
        response = new_client.get('/api/v1/',
                                 query_string={'action': 'sessions'},
                                 headers={'Authorization': 'Bearer test_admin_key_456'})
        
        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        
        session_found = False
        for session in data['data']['sessions']:
            if session['id'] == 'session_persistent':
                session_found = True
                break
        
        assert session_found is True
