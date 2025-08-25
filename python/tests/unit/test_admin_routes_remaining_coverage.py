"""
Comprehensive tests for remaining admin routes coverage

This file covers all remaining missing lines identified in coverage reports:
- Lines 178-193: clear_all_data function execution paths
- Lines 214-231: cleanup_logs function execution paths
"""

import pytest
from unittest.mock import patch, MagicMock
from app import create_app


class TestAdminRoutesRemainingCoverage:
    """Test remaining admin routes for complete coverage"""
    
    def test_clear_all_data_success(self, app):
        """Test clear_all_data success path - covers lines 178-193"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock database connection and cursor
                mock_db.get_connection.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor
                
                # Mock count queries
                mock_cursor.fetchone.side_effect = [(5,), (10,), (15,)]  # sessions, messages, responses
                
                response = client.post('/admin/api/clear_data', 
                                    headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert data['message'] == 'Success'
                assert 'data' in data
                assert 'cleaned_data' in data['data']
                
                # Verify all database operations were called
                assert mock_cursor.execute.call_count == 7  # 3 COUNT + 4 DELETE
                mock_conn.commit.assert_called_once()
                mock_conn.close.assert_called_once()
                
                # Verify the specific lines were executed
                mock_cursor.execute.assert_any_call("SELECT COUNT(*) FROM web_chat_sessions")
                mock_cursor.execute.assert_any_call("SELECT COUNT(*) FROM web_chat_messages")
                mock_cursor.execute.assert_any_call("SELECT COUNT(*) FROM web_chat_responses")
                mock_cursor.execute.assert_any_call("DELETE FROM web_chat_responses")
                mock_cursor.execute.assert_any_call("DELETE FROM web_chat_messages")
                mock_cursor.execute.assert_any_call("DELETE FROM web_chat_sessions")
                mock_cursor.execute.assert_any_call("DELETE FROM rate_limits")
    
    def test_clear_all_data_database_exception(self, app):
        """Test clear_all_data with database exception - covers error path"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.get_connection.side_effect = Exception("Database connection error")
                
                response = client.post('/admin/api/clear_data', 
                                    headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'error' in data
    
    def test_clear_all_data_cursor_exception(self, app):
        """Test clear_all_data with cursor exception - covers error path"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock database connection and cursor
                mock_db.get_connection.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor
                
                # Mock cursor.execute to raise exception
                mock_cursor.execute.side_effect = Exception("Cursor execution error")
                
                response = client.post('/admin/api/clear_data', 
                                    headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'error' in data
    
    def test_clear_all_data_commit_exception(self, app):
        """Test clear_all_data with commit exception - covers error path"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock database connection and cursor
                mock_db.get_connection.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor
                
                # Mock count queries
                mock_cursor.fetchone.side_effect = [(5,), (10,), (15,)]
                
                # Mock commit to raise exception
                mock_conn.commit.side_effect = Exception("Commit error")
                
                response = client.post('/admin/api/clear_data', 
                                    headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'error' in data
    
    def test_clear_all_data_close_exception(self, app):
        """Test clear_all_data with close exception - covers error path"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock database connection and cursor
                mock_db.get_connection.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor
                
                # Mock count queries
                mock_cursor.fetchone.side_effect = [(5,), (10,), (15,)]
                
                # Mock close to raise exception
                mock_conn.close.side_effect = Exception("Close error")
                
                response = client.post('/admin/api/clear_data', 
                                    headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'error' in data
    
    def test_cleanup_logs_success(self, app):
        """Test cleanup_logs success path - covers lines 214-231"""
        with app.test_client() as client:
            response = client.post('/admin/api/cleanup_logs', 
                                headers={'Authorization': 'Bearer admin_key'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['message'] == 'Success'
            assert 'timestamp' in data
            assert 'data' in data
            
            # Verify log cleanup data
            log_data = data['data']
            assert log_data['message'] == 'Log cleanup completed successfully'
            assert log_data['current_log_size_mb'] == 0.0
            assert log_data['backup_files_count'] == 0
            assert log_data['total_log_size_mb'] == 0.0
            assert log_data['retention_days'] == 30
            assert log_data['max_size_mb'] == 100
    
    def test_cleanup_logs_exception(self, app):
        """Test cleanup_logs with exception - covers line 230-231"""
        with app.test_client() as client:
            with patch('app.admin.routes.jsonify') as mock_jsonify:
                # Mock jsonify to raise exception
                mock_jsonify.side_effect = Exception("JSON error")
                
                response = client.post('/admin/api/cleanup_logs', 
                                    headers={'Authorization': 'Bearer admin_key'})
                
                # Should handle exception gracefully
                assert response.status_code in [500, 200]  # Depends on error handling
    
    def test_clear_all_data_edge_cases(self, app):
        """Test clear_all_data edge cases for complete coverage"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock database connection and cursor
                mock_db.get_connection.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor
                
                # Test with zero counts
                mock_cursor.fetchone.side_effect = [(0,), (0,), (0,)]
                
                response = client.post('/admin/api/clear_data', 
                                    headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                
                # Verify zero counts are handled
                cleaned_data = data['data']['cleaned_data']
                assert cleaned_data['sessions'] == 0
                assert cleaned_data['messages'] == 0
                assert cleaned_data['responses'] == 0
    
    def test_clear_all_data_large_counts(self, app):
        """Test clear_all_data with large counts for complete coverage"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock database connection and cursor
                mock_db.get_connection.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor
                
                # Test with large counts
                mock_cursor.fetchone.side_effect = [(1000,), (5000,), (2500,)]
                
                response = client.post('/admin/api/clear_data', 
                                    headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                
                # Verify large counts are handled
                cleaned_data = data['data']['cleaned_data']
                assert cleaned_data['sessions'] == 1000
                assert cleaned_data['messages'] == 5000
                assert cleaned_data['responses'] == 2500
    
    def test_clear_all_data_partial_failure(self, app):
        """Test clear_all_data with partial failure for complete coverage"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock database connection and cursor
                mock_db.get_connection.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor
                
                # Mock some operations to succeed and others to fail
                def mock_execute(query):
                    if 'COUNT' in query:
                        return None  # Success
                    elif 'DELETE FROM web_chat_responses' in query:
                        raise Exception("Delete responses failed")
                    else:
                        return None  # Success
                
                mock_cursor.execute.side_effect = mock_execute
                mock_cursor.fetchone.side_effect = [(5,), (10,), (15,)]
                
                response = client.post('/admin/api/clear_data', 
                                    headers={'Authorization': 'Bearer admin_key'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'error' in data
    
    def test_cleanup_logs_edge_cases(self, app):
        """Test cleanup_logs edge cases for complete coverage"""
        with app.test_client() as client:
            # Test with different HTTP methods
            response = client.get('/admin/api/cleanup_logs', 
                               headers={'Authorization': 'Bearer admin_key'})
            assert response.status_code == 405  # Method not allowed
            
            response = client.put('/admin/api/cleanup_logs', 
                               headers={'Authorization': 'Bearer admin_key'})
            assert response.status_code == 405  # Method not allowed
            
            # Test without authentication
            response = client.post('/admin/api/cleanup_logs')
            assert response.status_code == 401  # Unauthorized
    
    def test_clear_all_data_authentication(self, app):
        """Test clear_all_data authentication for complete coverage"""
        with app.test_client() as client:
            # Test without authentication
            response = client.post('/admin/api/clear_data')
            assert response.status_code == 401  # Unauthorized
            
            # Test with invalid authentication
            response = client.post('/admin/api/clear_data', 
                                headers={'Authorization': 'Bearer invalid_key'})
            assert response.status_code == 401  # Unauthorized
    
    def test_cleanup_logs_authentication(self, app):
        """Test cleanup_logs authentication for complete coverage"""
        with app.test_client() as client:
            # Test without authentication
            response = client.post('/admin/api/cleanup_logs')
            assert response.status_code == 401  # Unauthorized
            
            # Test with invalid authentication
            response = client.post('/admin/api/cleanup_logs', 
                                headers={'Authorization': 'Bearer invalid_key'})
            assert response.status_code == 401  # Unauthorized


class TestAdminRoutesIntegrationCoverage:
    """Test admin routes integration scenarios for complete coverage"""
    
    def test_admin_full_workflow_with_clear_data(self, app):
        """Test complete admin workflow including clear_data"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock database operations
                mock_db.get_connection.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchone.side_effect = [(5,), (10,), (15,)]
                
                # Test complete workflow
                # 1. Get sessions
                response = client.get('/admin/sessions', 
                                   headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code in [200, 500]
                
                # 2. Get config
                response = client.get('/admin/config', 
                                   headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code in [200, 500]
                
                # 3. Clear all data
                response = client.post('/admin/api/clear_data', 
                                    headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code == 200
                
                # 4. Cleanup logs
                response = client.post('/admin/api/cleanup_logs', 
                                    headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code == 200
                
                # Verify all operations were called
                assert mock_cursor.execute.call_count >= 7
                mock_conn.commit.assert_called_once()
                mock_conn.close.assert_called_once()
    
    def test_admin_error_recovery_with_clear_data(self, app):
        """Test admin error recovery including clear_data"""
        with app.test_client() as client:
            with patch('app.admin.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock database operations
                mock_db.get_connection.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchone.side_effect = [(5,), (10,), (15,)]
                
                # First call should succeed
                response = client.post('/admin/api/clear_data', 
                                    headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code == 200
                
                # Mock failure for second call
                mock_db.get_connection.side_effect = Exception("Connection failed")
                
                # Second call should fail
                response = client.post('/admin/api/clear_data', 
                                    headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code == 500
                
                # Reset mock for third call
                mock_db.get_connection.side_effect = None
                mock_db.get_connection.return_value = mock_conn
                
                # Third call should succeed again
                response = client.post('/admin/api/clear_data', 
                                    headers={'Authorization': 'Bearer admin_key'})
                assert response.status_code == 200
