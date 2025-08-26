"""
Test file to cover missing lines in admin routes
Target: 100% coverage for app/admin/routes.py
"""

import pytest
from unittest.mock import patch, MagicMock
from app.admin.routes import get_db, get_sessions, get_session_messages, handle_config, manual_cleanup, clear_all_data, cleanup_logs


class TestAdminRoutesMissingCoverage:
    """Test class to cover missing lines in admin routes"""
    
    def test_get_db_function(self):
        """Test get_db function - covers lines 11-12"""
        with patch('app.admin.routes.current_app') as mock_app:
            mock_app.config.get.return_value = 'test.db'
            with patch('app.admin.routes.DatabaseManager') as mock_db_manager:
                mock_db_manager.return_value = 'db_instance'
                
                result = get_db()
                
                mock_app.config.get.assert_called_once_with('DATABASE_PATH', 'web_chat_bridge.db')
                mock_db_manager.assert_called_once_with('test.db')
                assert result == 'db_instance'
    
    def test_get_sessions_exception_handling(self):
        """Test get_sessions exception handling - covers lines 31-33"""
        with patch('app.admin.routes.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_db.get_active_sessions.side_effect = Exception("Database error")
            mock_get_db.return_value = mock_db
            
            with patch('app.admin.routes.request') as mock_request:
                mock_request.args.get.side_effect = lambda key, default: default
                
                with patch('app.admin.routes.jsonify') as mock_jsonify:
                    mock_jsonify.return_value = ('error_response', 500)
                    
                    result = get_sessions()
                    
                    assert result == ('error_response', 500)
                    mock_jsonify.assert_called_once_with({'success': False, 'error': 'Database error'})
    
    def test_get_session_messages_missing_session_id(self):
        """Test get_session_messages with missing session_id - covers line 59"""
        with patch('app.admin.routes.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            
            with patch('app.admin.routes.request') as mock_request:
                mock_request.args.get.return_value = None
                
                with patch('app.admin.routes.jsonify') as mock_jsonify:
                    mock_jsonify.return_value = ('error_response', 400)
                    
                    result = get_session_messages()
                    
                    assert result == ('error_response', 400)
                    mock_jsonify.assert_called_once_with({'success': False, 'error': 'Missing session_id'})
    
    def test_get_session_messages_session_not_found(self):
        """Test get_session_messages with session not found - covers line 74"""
        with patch('app.admin.routes.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.get_connection.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None  # Session not found
            mock_get_db.return_value = mock_db
            
            with patch('app.admin.routes.request') as mock_request:
                mock_request.args.get.return_value = 'test_session'
                
                with patch('app.admin.routes.jsonify') as mock_jsonify:
                    mock_jsonify.return_value = ('error_response', 404)
                    
                    result = get_session_messages()
                    
                    assert result == ('error_response', 404)
                    mock_jsonify.assert_called_once_with({'success': False, 'error': 'Session not found'})
    
    def test_get_session_messages_database_operations(self):
        """Test get_session_messages database operations - covers lines 75-96"""
        with patch('app.admin.routes.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.get_connection.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock session data
            mock_session = {'id': 'test_session', 'last_active': '2023-01-01'}
            mock_cursor.fetchone.return_value = mock_session
            
            # Mock messages data
            mock_messages = [{'id': 1, 'session_id': 'test_session', 'message': 'test', 'timestamp': '2023-01-01'}]
            mock_cursor.fetchall.return_value = mock_messages
            
            # Mock responses data
            mock_responses = [{'id': 1, 'response': 'test', 'message_id': 1, 'timestamp': '2023-01-01'}]
            mock_cursor.fetchall.return_value = mock_responses
            
            mock_get_db.return_value = mock_db
            
            with patch('app.admin.routes.request') as mock_request:
                mock_request.args.get.return_value = 'test_session'
                
                with patch('app.admin.routes.jsonify') as mock_jsonify:
                    mock_jsonify.return_value = 'success_response'
                    
                    result = get_session_messages()
                    
                    assert result == 'success_response'
                    mock_conn.close.assert_called_once()
    
    def test_handle_config_get_exception(self):
        """Test handle_config GET exception handling - covers line 119"""
        with patch('app.admin.routes.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_db.get_all_config.side_effect = Exception("Config error")
            mock_get_db.return_value = mock_db
            
            with patch('app.admin.routes.request') as mock_request:
                mock_request.method = 'GET'
                
                with patch('app.admin.routes.jsonify') as mock_jsonify:
                    mock_jsonify.return_value = ('error_response', 500)
                    
                    result = handle_config()
                    
                    assert result == ('error_response', 500)
                    mock_jsonify.assert_called_once_with({'success': False, 'error': 'Config error'})
    
    def test_handle_config_post_invalid_json(self):
        """Test handle_config POST with invalid JSON - covers line 131"""
        with patch('app.admin.routes.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            
            with patch('app.admin.routes.request') as mock_request:
                mock_request.method = 'POST'
                mock_request.get_json.return_value = None
                
                with patch('app.admin.routes.jsonify') as mock_jsonify:
                    mock_jsonify.return_value = ('error_response', 400)
                    
                    result = handle_config()
                    
                    assert result == ('error_response', 400)
                    mock_jsonify.assert_called_once_with({'success': False, 'error': 'Invalid JSON'})
    
    def test_handle_config_post_exception(self):
        """Test handle_config POST exception handling - covers line 136"""
        with patch('app.admin.routes.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_db.update_config.side_effect = Exception("Update error")
            mock_get_db.return_value = mock_db
            
            with patch('app.admin.routes.request') as mock_request:
                mock_request.method = 'POST'
                mock_request.get_json.return_value = {'key': 'value'}
                
                with patch('app.admin.routes.jsonify') as mock_jsonify:
                    mock_jsonify.return_value = ('error_response', 500)
                    
                    result = handle_config()
                    
                    assert result == ('error_response', 500)
                    mock_jsonify.assert_called_once_with({'success': False, 'error': 'Update error'})
    
    def test_manual_cleanup_exception(self):
        """Test manual_cleanup exception handling - covers line 153"""
        with patch('app.admin.routes.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_db.cleanup_inactive_sessions.side_effect = Exception("Cleanup error")
            mock_get_db.return_value = mock_db
            
            with patch('app.admin.routes.jsonify') as mock_jsonify:
                mock_jsonify.return_value = ('error_response', 500)
                
                result = manual_cleanup()
                
                assert result == ('error_response', 500)
                mock_jsonify.assert_called_once_with({'success': False, 'error': 'Cleanup error'})
    
    def test_clear_all_data_database_operations(self):
        """Test clear_all_data database operations - covers lines 178-193"""
        with patch('app.admin.routes.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.get_connection.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock count results
            mock_cursor.fetchone.side_effect = [('5',), ('10',), ('15',)]
            
            mock_get_db.return_value = mock_db
            
            with patch('app.admin.routes.jsonify') as mock_jsonify:
                mock_jsonify.return_value = 'success_response'
                
                result = clear_all_data()
                
                assert result == 'success_response'
                mock_conn.commit.assert_called_once()
                mock_conn.close.assert_called_once()
    
    def test_clear_all_data_exception(self):
        """Test clear_all_data exception handling - covers line 214"""
        with patch('app.admin.routes.get_db') as mock_get_db:
            mock_db = MagicMock()
            mock_db.get_connection.side_effect = Exception("Connection error")
            mock_get_db.return_value = mock_db
            
            with patch('app.admin.routes.jsonify') as mock_jsonify:
                mock_jsonify.return_value = ('error_response', 500)
                
                result = clear_all_data()
                
                assert result == ('error_response', 500)
                mock_jsonify.assert_called_once_with({'success': False, 'error': 'Connection error'})
    
    def test_cleanup_logs_exception(self):
        """Test cleanup_logs exception handling - covers lines 230-231"""
        with patch('app.admin.routes.jsonify') as mock_jsonify:
            mock_jsonify.side_effect = Exception("JSON error")
            
            with pytest.raises(Exception):
                cleanup_logs()
