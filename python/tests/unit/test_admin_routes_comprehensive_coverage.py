"""
Comprehensive tests for admin routes to achieve 100% coverage

This file covers all missing lines identified in coverage reports:
- Error handling paths (lines 87, 119, 131, 136, 153, 230-231)
"""

import pytest
from unittest.mock import patch, MagicMock
from app import create_app


class TestAdminRoutesErrorHandlingComprehensive:
    """Test error handling paths in admin routes for complete coverage"""
    
    def test_admin_sessions_database_exception(self, app):
        """Test admin sessions with database exception - covers line 87"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.get_sessions.side_effect = Exception("Database error")
                mock_get_db.return_value = mock_db
                
                response = client.get('/admin/sessions', 
                                   headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Internal server error'
    
    def test_admin_config_get_database_exception(self, app):
        """Test admin config get with database exception - covers line 119"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.get_config.side_effect = Exception("Database error")
                mock_get_db.return_value = mock_db
                
                response = client.get('/admin/config', 
                                   headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Internal server error'
    
    def test_admin_config_update_database_exception(self, app):
        """Test admin config update with database exception - covers line 131"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.update_config.side_effect = Exception("Database error")
                mock_get_db.return_value = mock_db
                
                response = client.post('/admin/config', 
                                    json={'key': 'test_key', 'value': 'test_value'},
                                    headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Internal server error'
    
    def test_admin_config_update_invalid_json(self, app):
        """Test admin config update with invalid JSON - covers line 136"""
        with app.test_client() as client:
            response = client.post('/admin/config', 
                                data='invalid json',
                                content_type='application/json',
                                headers={'Authorization': 'Bearer admin_key'})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Invalid JSON'
    
    def test_admin_cleanup_database_exception(self, app):
        """Test admin cleanup with database exception - covers line 153"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.cleanup_old_data.side_effect = Exception("Database error")
                mock_get_db.return_value = mock_db
                
                response = client.post('/admin/cleanup', 
                                    headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Internal server error'
    
    def test_admin_session_messages_database_exception(self, app):
        """Test admin session messages with database exception - covers line 230-231"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.get_session_messages.side_effect = Exception("Database error")
                mock_get_db.return_value = mock_db
                
                response = client.get('/admin/session_messages?session_id=test_session', 
                                   headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert data['error'] == 'Internal server error'


class TestAdminRoutesEdgeCasesComprehensive:
    """Test edge cases and additional error paths"""
    
    def test_admin_sessions_pagination_edge_cases(self, app):
        """Test admin sessions pagination edge cases"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.get_sessions.return_value = []
                mock_get_db.return_value = mock_db
                
                # Test with invalid pagination parameters
                response = client.get('/admin/sessions?limit=invalid&offset=invalid', 
                                   headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
    
    def test_admin_config_missing_required_fields(self, app):
        """Test admin config update with missing required fields"""
        with app.test_client() as client:
            response = client.post('/admin/config', 
                                json={'key': 'test_key'},  # Missing value
                                headers={'Authorization': 'Bearer admin_key'})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Missing required fields'
    
    def test_admin_config_empty_values(self, app):
        """Test admin config update with empty values"""
        with app.test_client() as client:
            response = client.post('/admin/config', 
                                json={'key': '', 'value': ''},  # Empty values
                                headers={'Authorization': 'Bearer admin_key'})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Invalid configuration values'
    
    def test_admin_cleanup_with_parameters(self, app):
        """Test admin cleanup with optional parameters"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.cleanup_old_data.return_value = {'deleted_sessions': 5, 'deleted_messages': 10}
                mock_get_db.return_value = mock_db
                
                response = client.post('/admin/cleanup', 
                                    json={'days': 30, 'force': True},
                                    headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert 'deleted_sessions' in data['data']
    
    def test_admin_session_messages_invalid_session_id(self, app):
        """Test admin session messages with invalid session ID"""
        with app.test_client() as client:
            response = client.get('/admin/session_messages?session_id=invalid_session_id', 
                               headers={'Authorization': 'Bearer admin_key'})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Invalid session ID'


class TestAdminRoutesIntegrationComprehensive:
    """Test admin routes integration scenarios"""
    
    def test_admin_full_workflow(self, app):
        """Test complete admin workflow with error handling"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.get_sessions.return_value = []
                mock_db.get_config.return_value = {'api_key': 'test_key'}
                mock_db.update_config.return_value = True
                mock_db.cleanup_old_data.return_value = {'deleted_sessions': 0}
                mock_db.get_session_messages.return_value = []
                mock_get_db.return_value = mock_db
                
                # Get sessions
                response = client.get('/admin/sessions', 
                                   headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code == 200
                
                # Get config
                response = client.get('/admin/config', 
                                   headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code == 200
                
                # Update config
                response = client.post('/admin/config', 
                                    json={'key': 'new_key', 'value': 'new_value'},
                                    headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code == 200
                
                # Cleanup
                response = client.post('/admin/cleanup', 
                                    headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code == 200
                
                # Get session messages
                response = client.get('/admin/session_messages?session_id=test_session', 
                                   headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code == 200
    
    def test_admin_error_recovery(self, app):
        """Test admin error recovery scenarios"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_get_db.return_value = mock_db
                
                # First call fails, second succeeds
                mock_db.get_sessions.side_effect = [Exception("First error"), []]
                
                # First call should fail
                response = client.get('/admin/sessions', 
                                   headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code == 500
                
                # Second call should succeed
                response = client.get('/admin/sessions', 
                                   headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code == 200
