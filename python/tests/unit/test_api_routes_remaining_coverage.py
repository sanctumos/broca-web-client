"""
Comprehensive tests for remaining API routes coverage

This file covers all remaining missing lines identified in coverage reports:
- Lines 66, 68, 99, 105, 111, 117, 123, 152, 185-186, 259, 304, 357, 384-385, 407-408, 413, 426-427, 432, 454-455, 465, 487-492, 552-553
"""

import pytest
from unittest.mock import patch, MagicMock
from app import create_app


class TestAPIRoutesRemainingCoverage:
    """Test remaining API routes for complete coverage"""
    
    def test_handle_messages_rate_limit_exceeded(self, app):
        """Test messages rate limiting - covers lines 185-186"""
        with app.test_client() as client:
            with patch('app.api.routes.get_rate_limiter') as mock_rate_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = False
                mock_rate_limiter.return_value = mock_limiter
                
                response = client.post('/api/v1/?action=messages',
                                    json={'session_id': 'test_session', 'message': 'test message'})
                
                assert response.status_code == 429
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Rate limit exceeded'
    
    def test_handle_messages_invalid_session_id(self, app):
        """Test messages invalid session ID validation - covers line 259"""
        with app.test_client() as client:
            response = client.post('/api/v1/?action=messages',
                                json={'session_id': 'invalid', 'message': 'test'})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Invalid session ID'
    
    def test_handle_messages_invalid_message(self, app):
        """Test messages invalid message validation - covers line 304"""
        with app.test_client() as client:
            response = client.post('/api/v1/?action=messages',
                                json={'session_id': 'session_test', 'message': ''})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Invalid message'
    
    def test_handle_inbox_auth_failure(self, app):
        """Test inbox authentication failure - covers line 357"""
        with app.test_client() as client:
            with patch('app.api.routes.require_auth_internal') as mock_auth:
                mock_auth.return_value = {'success': False, 'error': 'Auth failed'}
                
                response = client.get('/api/v1/?action=inbox')
                
                assert response.status_code == 401
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Auth failed'
    
    def test_handle_outbox_method_not_allowed(self, app):
        """Test outbox method validation - covers lines 384-385"""
        with app.test_client() as client:
            response = client.get('/api/v1/?action=outbox')
            assert response.status_code == 405
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Method not allowed'
    
    def test_handle_outbox_auth_failure(self, app):
        """Test outbox authentication failure - covers lines 407-408"""
        with app.test_client() as client:
            with patch('app.api.routes.require_auth_internal') as mock_auth:
                mock_auth.return_value = {'success': False, 'error': 'Auth failed'}
                
                response = client.post('/api/v1/?action=outbox',
                                    json={'session_id': 'test', 'response': 'test'})
                
                assert response.status_code == 401
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Auth failed'
    
    def test_handle_outbox_invalid_json(self, app):
        """Test outbox invalid JSON handling - covers line 413"""
        with app.test_client() as client:
            response = client.post('/api/v1/?action=outbox',
                                data='invalid json',
                                content_type='application/json',
                                headers={'Authorization': 'Bearer test_key'})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Invalid JSON'
    
    def test_handle_outbox_missing_fields(self, app):
        """Test outbox missing fields validation - covers lines 426-427"""
        with app.test_client() as client:
            response = client.post('/api/v1/?action=outbox',
                                json={'session_id': ''},
                                headers={'Authorization': 'Bearer test_key'})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Missing required fields'
    
    def test_handle_outbox_invalid_session_id(self, app):
        """Test outbox invalid session ID validation - covers line 432"""
        with app.test_client() as client:
            response = client.post('/api/v1/?action=outbox',
                                json={'session_id': 'invalid', 'response': 'test'},
                                headers={'Authorization': 'Bearer test_key'})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Invalid session ID'
    
    def test_handle_outbox_database_exception(self, app):
        """Test outbox database exception handling - covers lines 454-455"""
        with app.test_client() as client:
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.create_response.side_effect = Exception("Database error")
                mock_get_db.return_value = mock_db
                
                response = client.post('/api/v1/?action=outbox',
                                    json={'session_id': 'session_test', 'response': 'test response'},
                                    headers={'Authorization': 'Bearer test_key'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Internal server error'
    
    def test_handle_responses_invalid_session_id(self, app):
        """Test responses invalid session ID validation - covers line 465"""
        with app.test_client() as client:
            response = client.get('/api/v1/?action=responses?session_id=invalid')
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Invalid session ID'
    
    def test_handle_sessions_method_not_allowed(self, app):
        """Test sessions method validation - covers lines 487-492"""
        with app.test_client() as client:
            response = client.post('/api/v1/?action=sessions')
            assert response.status_code == 405
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Method not allowed'
    
    def test_handle_config_method_not_allowed(self, app):
        """Test config method validation - covers lines 552-553"""
        with app.test_client() as client:
            response = client.put('/api/v1/?action=config')
            assert response.status_code == 405
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Method not allowed'
    
    def test_handle_messages_method_not_allowed(self, app):
        """Test messages method validation - covers line 152"""
        with app.test_client() as client:
            response = client.get('/api/v1/?action=messages')
            assert response.status_code == 405
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Method not allowed'


class TestAPIDirectRoutesRemainingCoverage:
    """Test direct route handlers for remaining coverage"""
    
    def test_handle_messages_direct_success(self, app):
        """Test direct messages route - covers line 66"""
        with app.test_client() as client:
            with patch('app.api.routes.handle_messages') as mock_handle:
                mock_handle.return_value = {'success': True, 'message': 'Success'}
                
                response = client.post('/api/v1/messages', 
                                    json={'session_id': 'test_session', 'message': 'test message'})
                
                assert response.status_code == 200
                mock_handle.assert_called_once()
    
    def test_handle_inbox_direct_success(self, app):
        """Test direct inbox route - covers line 68"""
        with app.test_client() as client:
            with patch('app.api.routes.handle_inbox') as mock_handle:
                mock_handle.return_value = {'success': True, 'message': 'Success'}
                
                response = client.get('/api/v1/inbox', 
                                   headers={'Authorization': 'Bearer test_key'})
                
                assert response.status_code == 200
                mock_handle.assert_called_once()
    
    def test_handle_outbox_direct_success(self, app):
        """Test direct outbox route - covers line 99"""
        with app.test_client() as client:
            with patch('app.api.routes.handle_outbox') as mock_handle:
                mock_handle.return_value = {'success': True, 'message': 'Success'}
                
                response = client.post('/api/v1/outbox', 
                                    json={'session_id': 'test_session', 'response': 'test response'},
                                    headers={'Authorization': 'Bearer test_key'})
                
                assert response.status_code == 200
                mock_handle.assert_called_once()
    
    def test_handle_responses_direct_success(self, app):
        """Test direct responses route - covers line 105"""
        with app.test_client() as client:
            with patch('app.api.routes.handle_responses') as mock_handle:
                mock_handle.return_value = {'success': True, 'message': 'Success'}
                
                response = client.get('/api/v1/responses?session_id=test_session')
                
                assert response.status_code == 200
                mock_handle.assert_called_once()
    
    def test_handle_sessions_direct_success(self, app):
        """Test direct sessions route - covers line 111"""
        with app.test_client() as client:
            with patch('app.api.routes.handle_sessions') as mock_handle:
                mock_handle.return_value = {'success': True, 'message': 'Success'}
                
                response = client.get('/api/v1/sessions', 
                                   headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 200
                mock_handle.assert_called_once()
    
    def test_handle_config_direct_success(self, app):
        """Test direct config route - covers line 117"""
        with app.test_client() as client:
            with patch('app.api.routes.handle_config') as mock_handle:
                mock_handle.return_value = {'success': True, 'message': 'Success'}
                
                response = client.get('/api/v1/config', 
                                   headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 200
                mock_handle.assert_called_once()
    
    def test_handle_cleanup_direct_success(self, app):
        """Test direct cleanup route - covers line 123"""
        with app.test_client() as client:
            with patch('app.api.routes.handle_cleanup') as mock_handle:
                mock_handle.return_value = {'success': True, 'message': 'Success'}
                
                response = client.post('/api/v1/cleanup', 
                                    headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 200
                mock_handle.assert_called_once()


class TestAPIEdgeCasesRemainingCoverage:
    """Test edge cases and additional error paths"""
    
    def test_main_route_invalid_action(self, app):
        """Test main route with invalid action parameter"""
        with app.test_client() as client:
            response = client.get('/api/v1/?action=invalid_action')
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Invalid action'
    
    def test_main_route_missing_action(self, app):
        """Test main route without action parameter"""
        with app.test_client() as client:
            response = client.get('/api/v1/')
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Action parameter required'
    
    def test_handle_messages_database_exception(self, app):
        """Test messages database exception handling - covers line 347"""
        with app.test_client() as client:
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.session_exists.side_effect = Exception("Database error")
                mock_get_db.return_value = mock_db
                
                response = client.post('/api/v1/?action=messages',
                                    json={'session_id': 'session_test', 'message': 'test message'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Internal server error'
    
    def test_handle_messages_invalid_json(self, app):
        """Test messages invalid JSON handling - covers line 191"""
        with app.test_client() as client:
            response = client.post('/api/v1/?action=messages',
                                data='invalid json',
                                content_type='application/json')
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Invalid JSON'
    
    def test_handle_messages_missing_fields(self, app):
        """Test messages missing fields validation - covers line 244"""
        with app.test_client() as client:
            response = client.post('/api/v1/?action=messages',
                                json={'session_id': ''})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Missing required fields'
    
    def test_handle_outbox_rate_limit_exceeded(self, app):
        """Test outbox rate limiting"""
        with app.test_client() as client:
            with patch('app.api.routes.get_rate_limiter') as mock_rate_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = False
                mock_rate_limiter.return_value = mock_limiter
                
                response = client.post('/api/v1/?action=outbox',
                                    json={'session_id': 'test_session', 'response': 'test response'},
                                    headers={'Authorization': 'Bearer test_key'})
                
                assert response.status_code == 429
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Rate limit exceeded'
    
    def test_handle_responses_rate_limit_exceeded(self, app):
        """Test responses rate limiting"""
        with app.test_client() as client:
            with patch('app.api.routes.get_rate_limiter') as mock_rate_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = False
                mock_rate_limiter.return_value = mock_limiter
                
                response = client.get('/api/v1/?action=responses?session_id=test_session')
                
                assert response.status_code == 429
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Rate limit exceeded'
    
    def test_handle_sessions_rate_limit_exceeded(self, app):
        """Test sessions rate limiting"""
        with app.test_client() as client:
            with patch('app.api.routes.get_rate_limiter') as mock_rate_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = False
                mock_rate_limiter.return_value = mock_limiter
                
                response = client.get('/api/v1/?action=sessions',
                                   headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 429
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Rate limit exceeded'
    
    def test_handle_config_rate_limit_exceeded(self, app):
        """Test config rate limiting"""
        with app.test_client() as client:
            with patch('app.api.routes.get_rate_limiter') as mock_rate_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = False
                mock_rate_limiter.return_value = mock_limiter
                
                response = client.get('/api/v1/?action=config',
                                   headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 429
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Rate limit exceeded'
    
    def test_handle_cleanup_rate_limit_exceeded(self, app):
        """Test cleanup rate limiting"""
        with app.test_client() as client:
            with patch('app.api.routes.get_rate_limiter') as mock_rate_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = False
                mock_rate_limiter.return_value = mock_limiter
                
                response = client.post('/api/v1/?action=cleanup',
                                    headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 429
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Rate limit exceeded'
