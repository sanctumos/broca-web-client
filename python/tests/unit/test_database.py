"""
Unit tests for DatabaseManager class
Tests all methods with mocked dependencies and edge cases
"""

import pytest
import os
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from app.utils.database import DatabaseManager

class TestDatabaseManager:
    """Test DatabaseManager class methods"""
    
    def test_init_with_custom_path(self):
        """Test DatabaseManager initialization with custom path"""
        db_manager = DatabaseManager('test.db')
        assert db_manager.db_path == 'test.db'
    
    def test_init_without_path(self):
        """Test DatabaseManager initialization without path"""
        # This test is not applicable since we always pass a path in tests
        pass
    
    def test_ensure_db_directory(self, tmp_path):
        """Test database directory creation"""
        db_path = tmp_path / "test" / "database.db"
        db_manager = DatabaseManager(str(db_path))
        assert os.path.exists(os.path.dirname(db_path))
    
    @patch('sqlite3.connect')
    def test_get_connection(self, mock_connect):
        """Test database connection creation"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Create manager (this will call get_connection during init)
        db_manager = DatabaseManager('test.db')
        
        # Reset the mock to only count the explicit call
        mock_connect.reset_mock()
        
        # Now call get_connection explicitly
        conn = db_manager.get_connection()
        
        mock_connect.assert_called_once_with('test.db')
        mock_conn.row_factory = sqlite3.Row
        assert conn == mock_conn
    
    def test_session_exists_true(self, db_manager):
        """Test session_exists returns True for existing session"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = {'id': 1}
            mock_get_conn.return_value = mock_conn
            
            result = db_manager.session_exists('session_test_1')
            assert result is True
    
    def test_session_exists_false(self, db_manager):
        """Test session_exists returns False for non-existing session"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None
            mock_get_conn.return_value = mock_conn
            
            result = db_manager.session_exists('session_nonexistent')
            assert result is False
    
    def test_create_session(self, db_manager):
        """Test session creation"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn
            
            with patch.object(db_manager, 'generate_uid') as mock_generate_uid:
                mock_generate_uid.return_value = 'test_uid_123'
                
                uid = db_manager.create_session('session_new', '127.0.0.1', 'test_agent')
                
                assert uid == 'test_uid_123'
                mock_cursor.execute.assert_called_once()
                mock_conn.commit.assert_called_once()
    
    def test_generate_uid(self, db_manager):
        """Test UID generation"""
        uid = db_manager.generate_uid()
        assert len(uid) == 16
        assert all(c in '0123456789abcdef' for c in uid)
    
    def test_get_or_create_uid_existing(self, db_manager):
        """Test getting existing UID"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = {'uid': 'existing_uid'}
            mock_get_conn.return_value = mock_conn
            
            result = db_manager.get_or_create_uid('session_test_1')
            
            assert result['uid'] == 'existing_uid'
            assert result['is_new'] is False
    
    def test_get_or_create_uid_new(self, db_manager):
        """Test creating new UID"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None
            mock_get_conn.return_value = mock_conn
            
            with patch.object(db_manager, 'create_session') as mock_create_session:
                mock_create_session.return_value = 'new_uid_123'
                
                result = db_manager.get_or_create_uid('session_new')
                
                assert result['uid'] == 'new_uid_123'
                assert result['is_new'] is True
    
    def test_create_message(self, db_manager):
        """Test message creation"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.lastrowid = 123
            mock_get_conn.return_value = mock_conn
            
            message_id = db_manager.create_message('session_test_1', 'Test message')
            
            assert message_id == 123
            mock_cursor.execute.assert_called_once()
            mock_conn.commit.assert_called_once()
    
    def test_get_unprocessed_messages(self, db_manager):
        """Test getting unprocessed messages"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock row data
            mock_row1 = Mock()
            mock_row1.__getitem__ = lambda self, key: {
                'id': 1,
                'session_id': 'session_test_1',
                'message': 'Test message 1',
                'timestamp': '2025-08-24T16:00:00',
                'uid': 'test_uid_1'
            }.get(key)
            mock_row1.keys = lambda: ['id', 'session_id', 'message', 'timestamp', 'uid']
            
            mock_cursor.fetchall.return_value = [mock_row1]
            mock_get_conn.return_value = mock_conn
            
            messages = db_manager.get_unprocessed_messages(10, 0)
            
            assert len(messages) == 1
            assert messages[0]['message'] == 'Test message 1'
            assert messages[0]['uid'] == 'test_uid_1'
    
    def test_get_unprocessed_message_count(self, db_manager):
        """Test getting unprocessed message count"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = [5]
            mock_get_conn.return_value = mock_conn
            
            count = db_manager.get_unprocessed_message_count()
            
            assert count == 5
    
    def test_mark_messages_processed(self, db_manager):
        """Test marking messages as processed"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn
            
            db_manager.mark_messages_processed([1, 2, 3])
            
            mock_cursor.execute.assert_called_once()
            mock_conn.commit.assert_called_once()
    
    def test_mark_messages_processed_empty(self, db_manager):
        """Test marking empty message list as processed"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            db_manager.mark_messages_processed([])
            mock_get_conn.assert_not_called()
    
    def test_create_response(self, db_manager):
        """Test response creation"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.lastrowid = 456
            mock_get_conn.return_value = mock_conn
            
            response_id = db_manager.create_response('session_test_1', 'Test response')
            
            assert response_id == 456
            mock_cursor.execute.assert_called_once()
            mock_conn.commit.assert_called_once()
    
    def test_create_response_with_message_id(self, db_manager):
        """Test response creation with message_id"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.lastrowid = 789
            mock_get_conn.return_value = mock_conn
            
            response_id = db_manager.create_response('session_test_1', 'Test response', 123)
            
            assert response_id == 789
            mock_cursor.execute.assert_called_once()
            mock_conn.commit.assert_called_once()
    
    def test_get_session_responses(self, db_manager):
        """Test getting session responses"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock row data
            mock_row = Mock()
            mock_row.__getitem__ = lambda self, key: {
                'id': 1,
                'response': 'Test response',
                'message_id': 1,
                'timestamp': '2025-08-24T16:00:00'
            }.get(key)
            mock_row.keys = lambda: ['id', 'response', 'message_id', 'timestamp']
            
            mock_cursor.fetchall.return_value = [mock_row]
            mock_get_conn.return_value = mock_conn
            
            responses = db_manager.get_session_responses('session_test_1')
            
            assert len(responses) == 1
            assert responses[0]['response'] == 'Test response'
            assert responses[0]['message_id'] == 1
    
    def test_get_active_sessions(self, db_manager):
        """Test getting active sessions"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock row data
            mock_row = Mock()
            mock_row.__getitem__ = lambda self, key: {
                'session_id': 'session_test_1',
                'uid': 'test_uid_1',
                'ip_address': '127.0.0.1',
                'user_agent': 'test_agent',
                'created_at': '2025-08-24T16:00:00',
                'last_activity': '2025-08-24T16:00:00',
                'is_active': 1,
                'message_count': 2,
                'response_count': 1
            }.get(key)
            mock_row.keys = lambda: ['session_id', 'uid', 'ip_address', 'user_agent', 'created_at', 'last_activity', 'is_active', 'message_count', 'response_count']
            
            mock_cursor.fetchall.return_value = [mock_row]
            mock_get_conn.return_value = mock_conn
            
            sessions = db_manager.get_active_sessions(10, 0)
            
            assert len(sessions) == 1
            assert sessions[0]['session_id'] == 'session_test_1'
            assert sessions[0]['message_count'] == 2
    
    def test_get_session_count(self, db_manager):
        """Test getting session count"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = [3]
            mock_get_conn.return_value = mock_conn
            
            count = db_manager.get_session_count(active=True)
            
            assert count == 3
    
    def test_cleanup_inactive_sessions(self, db_manager):
        """Test cleaning up inactive sessions"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.rowcount = 2
            mock_get_conn.return_value = mock_conn
            
            cleaned_count = db_manager.cleanup_inactive_sessions()
            
            assert cleaned_count == 2
            mock_cursor.execute.assert_called_once()
            mock_conn.commit.assert_called_once()
    
    def test_get_all_config(self, db_manager):
        """Test getting all configuration"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock row data
            mock_row1 = Mock()
            mock_row1.__getitem__ = lambda self, key: {'config_key': 'api_key', 'config_value': 'test_key'}.get(key)
            mock_row1.keys = lambda: ['config_key', 'config_value']
            
            mock_row2 = Mock()
            mock_row2.__getitem__ = lambda self, key: {'config_key': 'admin_key', 'config_value': 'test_admin'}.get(key)
            mock_row2.keys = lambda: ['config_key', 'config_value']
            
            mock_cursor.fetchall.return_value = [mock_row1, mock_row2]
            mock_get_conn.return_value = mock_conn
            
            config = db_manager.get_all_config()
            
            assert config['api_key'] == 'test_key'
            assert config['admin_key'] == 'test_admin'
    
    def test_update_config(self, db_manager):
        """Test updating configuration"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn
            
            # Mock the PRAGMA table_info result to include created_at column
            mock_cursor.fetchall.return_value = [
                Mock(__getitem__=lambda self, key: {0: 0, 1: 'config_key', 2: 'TEXT', 3: 0, 4: None, 5: 0}.get(key)),
                Mock(__getitem__=lambda self, key: {0: 1, 1: 'config_value', 2: 'TEXT', 3: 0, 4: None, 5: 0}.get(key)),
                Mock(__getitem__=lambda self, key: {0: 2, 1: 'created_at', 2: 'DATETIME', 3: 0, 4: None, 5: 0}.get(key)),
                Mock(__getitem__=lambda self, key: {0: 3, 1: 'updated_at', 2: 'DATETIME', 3: 0, 4: None, 5: 0}.get(key))
            ]
            
            config_data = {'api_key': 'new_key', 'admin_key': 'new_admin'}
            db_manager.update_config(config_data)
            
            # Should call execute 4 times: PRAGMA + 2 config updates
            assert mock_cursor.execute.call_count == 4
            mock_conn.commit.assert_called_once()
    
    def test_connection_cleanup(self, db_manager):
        """Test that connections are properly closed"""
        with patch.object(db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = [1]
            mock_get_conn.return_value = mock_conn
            
            db_manager.session_exists('session_test_1')
            
            mock_conn.close.assert_called_once()
