import pytest
from unittest.mock import patch, MagicMock
from app import create_app


class TestAPIRoutesComprehensiveIntegration:
    """Comprehensive integration tests for API routes to achieve 100% coverage"""
    
    def test_api_rate_limiting_exception_integration(self, app):
        """Test API rate limiting with exception - covers lines 22, 66, 68"""
        with app.test_client() as client:
            # Mock rate limiting to raise exception
            with patch('app.api.routes.check_rate_limit') as mock_rate_limit:
                mock_rate_limit.side_effect = Exception("Rate limit check failed")
                
                response = client.post('/api/v1/?action=inbox',
                                     json={'message': 'test message'},
                                     headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Rate limit check failed' in data['error']
    
    def test_api_database_connection_exception_integration(self, app):
        """Test API database connection exception - covers lines 93, 99, 105"""
        with app.test_client() as client:
            # Mock database to raise exception
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.get_connection.side_effect = Exception("Database connection failed")
                mock_get_db.return_value = mock_db
                
                response = client.post('/api/v1/?action=inbox',
                                     json={'message': 'test message'},
                                     headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Database connection failed' in data['error']
    
    def test_api_session_creation_exception_integration(self, app):
        """Test API session creation exception - covers lines 111, 117, 123"""
        with app.test_client() as client:
            # Mock database to raise exception during session creation
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                mock_cursor.execute.side_effect = Exception("Session creation failed")
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.post('/api/v1/?action=inbox',
                                     json={'message': 'test message'},
                                     headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Session creation failed' in data['error']
    
    def test_api_message_storage_exception_integration(self, app):
        """Test API message storage exception - covers lines 128, 133, 138"""
        with app.test_client() as client:
            # Mock database to raise exception during message storage
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # First execute succeeds (session creation), second fails (message storage)
                mock_cursor.execute.side_effect = [None, Exception("Message storage failed")]
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.post('/api/v1/?action=inbox',
                                     json={'message': 'test message'},
                                     headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Message storage failed' in data['error']
    
    def test_api_response_storage_exception_integration(self, app):
        """Test API response storage exception - covers lines 146, 152"""
        with app.test_client() as client:
            # Mock database to raise exception during response storage
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # First two executes succeed, third fails (response storage)
                mock_cursor.execute.side_effect = [None, None, Exception("Response storage failed")]
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.post('/api/v1/?action=inbox',
                                     json={'message': 'test message'},
                                     headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Response storage failed' in data['error']
    
    def test_api_outbox_database_exception_integration(self, app):
        """Test API outbox database exception - covers lines 185-186, 191"""
        with app.test_client() as client:
            # Mock database to raise exception during outbox retrieval
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.get_connection.side_effect = Exception("Outbox retrieval failed")
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=outbox',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Outbox retrieval failed' in data['error']
    
    def test_api_outbox_session_retrieval_exception_integration(self, app):
        """Test API outbox session retrieval exception - covers lines 201"""
        with app.test_client() as client:
            # Mock database to raise exception during session retrieval
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                mock_cursor.execute.side_effect = Exception("Session retrieval failed")
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=outbox',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Session retrieval failed' in data['error']
    
    def test_api_outbox_message_retrieval_exception_integration(self, app):
        """Test API outbox message retrieval exception - covers lines 238-239, 244"""
        with app.test_client() as client:
            # Mock database to raise exception during message retrieval
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # First execute succeeds (sessions), second fails (messages)
                mock_cursor.execute.side_effect = [None, Exception("Message retrieval failed")]
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=outbox',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Message retrieval failed' in data['error']
    
    def test_api_outbox_response_retrieval_exception_integration(self, app):
        """Test API outbox response retrieval exception - covers lines 254, 259"""
        with app.test_client() as client:
            # Mock database to raise exception during response retrieval
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # First two executes succeed, third fails (responses)
                mock_cursor.execute.side_effect = [None, None, Exception("Response retrieval failed")]
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=outbox',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Response retrieval failed' in data['error']
    
    def test_api_outbox_connection_management_integration(self, app):
        """Test API outbox connection management - covers lines 281"""
        with app.test_client() as client:
            # Mock database to succeed and verify connection management
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock successful data retrieval
                mock_cursor.fetchall.side_effect = [[], [], []]
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=outbox',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 200
                # Verify connection was closed
                mock_conn.close.assert_called_once()
    
    def test_api_sessions_database_exception_integration(self, app):
        """Test API sessions database exception - covers lines 298-299, 304"""
        with app.test_client() as client:
            # Mock database to raise exception during sessions retrieval
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.get_connection.side_effect = Exception("Sessions retrieval failed")
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=sessions',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Sessions retrieval failed' in data['error']
    
    def test_api_sessions_connection_management_integration(self, app):
        """Test API sessions connection management - covers lines 309"""
        with app.test_client() as client:
            # Mock database to succeed and verify connection management
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock successful data retrieval
                mock_cursor.fetchall.return_value = []
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=sessions',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 200
                # Verify connection was closed
                mock_conn.close.assert_called_once()
    
    def test_api_session_messages_database_exception_integration(self, app):
        """Test API session messages database exception - covers lines 326"""
        with app.test_client() as client:
            # Mock database to raise exception during session messages retrieval
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.get_connection.side_effect = Exception("Session messages retrieval failed")
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=session_messages&session_id=test_session',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Session messages retrieval failed' in data['error']
    
    def test_api_session_messages_connection_management_integration(self, app):
        """Test API session messages connection management - covers lines 341-342, 347"""
        with app.test_client() as client:
            # Mock database to succeed and verify connection management
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock successful data retrieval
                mock_cursor.fetchall.side_effect = [[], []]
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=session_messages&session_id=test_session',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 200
                # Verify connection was closed
                mock_conn.close.assert_called_once()
    
    def test_api_config_database_exception_integration(self, app):
        """Test API config database exception - covers lines 352, 357"""
        with app.test_client() as client:
            # Mock database to raise exception during config retrieval
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.get_all_config.side_effect = Exception("Config retrieval failed")
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=config',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Config retrieval failed' in data['error']
    
    def test_api_cleanup_database_exception_integration(self, app):
        """Test API cleanup database exception - covers lines 384-385, 407-408"""
        with app.test_client() as client:
            # Mock database to raise exception during cleanup
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.cleanup_inactive_sessions.side_effect = Exception("Cleanup failed")
                mock_get_db.return_value = mock_db
                
                response = client.post('/api/v1/?action=cleanup',
                                     headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Cleanup failed' in data['error']
    
    def test_api_clear_data_database_exception_integration(self, app):
        """Test API clear data database exception - covers lines 413, 426-427, 432"""
        with app.test_client() as client:
            # Mock database to raise exception during clear data
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                mock_cursor.execute.side_effect = Exception("Clear data failed")
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.post('/api/v1/?action=clear_data',
                                     headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['success'] is False
                assert 'Clear data failed' in data['error']
    
    def test_api_clear_data_connection_management_integration(self, app):
        """Test API clear data connection management - covers lines 439-455, 459-507"""
        with app.test_client() as client:
            # Mock database to succeed and verify connection management
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock successful data retrieval and deletion
                mock_cursor.fetchone.side_effect = [[5], [10], [15]]
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.post('/api/v1/?action=clear_data',
                                     headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert data['data']['cleaned_data']['sessions'] == 5
                assert data['data']['cleaned_data']['messages'] == 10
                assert data['data']['cleaned_data']['responses'] == 15
                
                # Verify commit was called
                mock_conn.commit.assert_called_once()
                mock_conn.close.assert_called_once()
    
    def test_api_cleanup_logs_exception_integration(self, app):
        """Test API cleanup logs exception - covers lines 511-553, 570"""
        with app.test_client() as client:
            # Mock jsonify to raise exception
            with patch('app.api.routes.jsonify') as mock_jsonify:
                mock_jsonify.side_effect = Exception("JSON serialization failed")
                
                response = client.post('/api/v1/?action=cleanup_logs',
                                     headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 500
    
    def test_api_cleanup_logs_success_integration(self, app):
        """Test API cleanup logs success - covers lines 586"""
        with app.test_client() as client:
            response = client.post('/api/v1/?action=cleanup_logs',
                                 headers={'Authorization': 'Bearer test_api_key_123'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['message'] == 'Success'
            assert 'current_log_size_mb' in data['data']
            assert 'backup_files_count' in data['data']
            assert 'total_log_size_mb' in data['data']
            assert 'retention_days' in data['data']
            assert 'max_size_mb' in data['data']
    
    def test_api_rate_limiting_success_integration(self, app):
        """Test API rate limiting success - covers lines 22, 66, 68"""
        with app.test_client() as client:
            # Mock rate limiting to succeed
            with patch('app.api.routes.check_rate_limit') as mock_rate_limit:
                mock_rate_limit.return_value = True
                
                # Mock database to succeed
                with patch('app.api.routes.get_db') as mock_get_db:
                    mock_db = MagicMock()
                    mock_conn = MagicMock()
                    mock_cursor = MagicMock()
                    
                    # Mock successful data operations
                    mock_cursor.fetchone.side_effect = [None, 1]
                    mock_conn.cursor.return_value = mock_cursor
                    mock_db.get_connection.return_value = mock_conn
                    mock_get_db.return_value = mock_db
                    
                    response = client.post('/api/v1/?action=inbox',
                                         json={'message': 'test message'},
                                         headers={'Authorization': 'Bearer test_api_key_123'})
                    
                    assert response.status_code == 200
                    data = response.get_json()
                    assert data['success'] is True
                    assert data['message'] == 'Success'
                    
                    # Verify connection was closed
                    mock_conn.close.assert_called_once()
    
    def test_api_outbox_success_integration(self, app):
        """Test API outbox success - covers lines 185-186, 191, 201, 238-239, 244, 254, 259, 281"""
        with app.test_client() as client:
            # Mock database to succeed
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock successful data retrieval
                mock_cursor.fetchall.side_effect = [[], [], []]
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=outbox',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert data['message'] == 'Success'
                assert 'sessions' in data['data']
                assert 'messages' in data['data']
                assert 'responses' in data['data']
                
                # Verify connection was closed
                mock_conn.close.assert_called_once()
    
    def test_api_sessions_success_integration(self, app):
        """Test API sessions success - covers lines 298-299, 304, 309"""
        with app.test_client() as client:
            # Mock database to succeed
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock successful data retrieval
                mock_cursor.fetchall.return_value = []
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=sessions',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert data['message'] == 'Success'
                assert 'sessions' in data['data']
                
                # Verify connection was closed
                mock_conn.close.assert_called_once()
    
    def test_api_session_messages_success_integration(self, app):
        """Test API session messages success - covers lines 326, 341-342, 347"""
        with app.test_client() as client:
            # Mock database to succeed
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock successful data retrieval
                mock_cursor.fetchall.side_effect = [[], []]
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=session_messages&session_id=test_session',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert data['message'] == 'Success'
                assert 'messages' in data['data']
                assert 'responses' in data['data']
                
                # Verify connection was closed
                mock_conn.close.assert_called_once()
    
    def test_api_config_success_integration(self, app):
        """Test API config success - covers lines 352, 357"""
        with app.test_client() as client:
            # Mock database to succeed
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.get_all_config.return_value = {'api_key': 'test_key'}
                mock_get_db.return_value = mock_db
                
                response = client.get('/api/v1/?action=config',
                                    headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert data['message'] == 'Success'
                assert 'api_key' in data['data']
    
    def test_api_cleanup_success_integration(self, app):
        """Test API cleanup success - covers lines 384-385, 407-408"""
        with app.test_client() as client:
            # Mock database to succeed
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_db.cleanup_inactive_sessions.return_value = 3
                mock_get_db.return_value = mock_db
                
                response = client.post('/api/v1/?action=cleanup',
                                     headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert data['data']['cleaned_count'] == 3
    
    def test_api_clear_data_success_integration(self, app):
        """Test API clear data success - covers lines 413, 426-427, 432, 439-455, 459-507"""
        with app.test_client() as client:
            # Mock database to succeed
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_db = MagicMock()
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                
                # Mock successful data retrieval and deletion
                mock_cursor.fetchone.side_effect = [[2], [5], [8]]
                mock_conn.cursor.return_value = mock_cursor
                mock_db.get_connection.return_value = mock_conn
                mock_get_db.return_value = mock_db
                
                response = client.post('/api/v1/?action=clear_data',
                                     headers={'Authorization': 'Bearer test_api_key_123'})
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] is True
                assert data['data']['cleaned_data']['sessions'] == 2
                assert data['data']['cleaned_data']['messages'] == 5
                assert data['data']['cleaned_data']['responses'] == 8
                
                # Verify commit was called
                mock_conn.commit.assert_called_once()
                mock_conn.close.assert_called_once()
    
    def test_api_cleanup_logs_success_integration(self, app):
        """Test API cleanup logs success - covers lines 511-553, 570, 586"""
        with app.test_client() as client:
            response = client.post('/api/v1/?action=cleanup_logs',
                                 headers={'Authorization': 'Bearer test_api_key_123'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['message'] == 'Success'
            assert 'current_log_size_mb' in data['data']
            assert 'backup_files_count' in data['data']
            assert 'total_log_size_mb' in data['data']
            assert 'retention_days' in data['data']
            assert 'max_size_mb' in data['data']
