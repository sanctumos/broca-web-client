"""
Comprehensive tests for database module to achieve 100% coverage

This file covers all missing lines identified in coverage reports:
- Database initialization error paths (lines 64-68, 74-80)
- Error handling in database operations (lines 258-259, 289-290, 403, 460)
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import sqlite3
from app.utils.database import DatabaseManager


class TestDatabaseInitializationComprehensive:
    """Test database initialization error paths for complete coverage"""
    
    def test_init_database_executescript_exception(self, app):
        """Test database init with executescript exception - covers line 64-68"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.executescript.side_effect = Exception("SQL execution error")
            mock_connect.return_value = mock_conn
            
            with patch('builtins.open', mock_open(read_data="CREATE TABLE test;")):
                db_manager = DatabaseManager()
                db_manager.init_database()
                
                # Should fall back to basic schema
                mock_cursor.executescript.assert_called_once()
                mock_conn.rollback.assert_called()
    
    def test_init_database_connection_exception(self, app):
        """Test database init with connection exception - covers line 74-80"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection error")
            
            db_manager = DatabaseManager()
            db_manager.init_database()
            
            # Should handle connection error gracefully
            mock_connect.assert_called_once()
    
    def test_init_database_rollback_exception(self, app):
        """Test database init with rollback exception - covers line 74-80"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.executescript.side_effect = Exception("SQL execution error")
            mock_conn.rollback.side_effect = Exception("Rollback error")
            mock_connect.return_value = mock_conn
            
            with patch('builtins.open', mock_open(read_data="CREATE TABLE test;")):
                db_manager = DatabaseManager()
                db_manager.init_database()
                
                # Should handle rollback error gracefully
                mock_conn.rollback.assert_called()
    
    def test_init_database_no_init_script(self, app):
        """Test database init without init script - covers line 74-80"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            with patch('os.path.exists', return_value=False):
                db_manager = DatabaseManager()
                db_manager.init_database()
                
                # Should create basic schema
                mock_cursor.execute.assert_called()


class TestDatabaseErrorHandlingComprehensive:
    """Test error handling paths in database operations"""
    
    def test_create_session_database_exception(self, app):
        """Test create_session with database exception - covers line 258-259"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Database error")
            mock_connect.return_value = mock_conn
            
            db_manager = DatabaseManager()
            
            with pytest.raises(Exception):
                db_manager.create_session('test_session', '127.0.0.1', 'test_agent')
    
    def test_create_message_database_exception(self, app):
        """Test create_message with database exception - covers line 289-290"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Database error")
            mock_connect.return_value = mock_conn
            
            db_manager = DatabaseManager()
            
            with pytest.raises(Exception):
                db_manager.create_message('test_session', 'test message')
    
    def test_create_response_database_exception(self, app):
        """Test create_response with database exception - covers line 403"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Database error")
            mock_connect.return_value = mock_conn
            
            db_manager = DatabaseManager()
            
            with pytest.raises(Exception):
                db_manager.create_response('test_session', 'test_response')
    
    def test_get_messages_database_exception(self, app):
        """Test get_messages with database exception - covers line 460"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.execute.side_effect = Exception("Database error")
            mock_connect.return_value = mock_conn
            
            db_manager = DatabaseManager()
            
            with pytest.raises(Exception):
                db_manager.get_messages('test_session')


class TestDatabaseEdgeCasesComprehensive:
    """Test edge cases and additional error paths"""
    
    def test_create_basic_schema_success(self, app):
        """Test create_basic_schema method execution"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            db_manager = DatabaseManager()
            db_manager.create_basic_schema(mock_conn)
            
            # Should execute multiple CREATE TABLE statements
            assert mock_cursor.execute.call_count >= 5
    
    def test_database_connection_close_always(self, app):
        """Test that database connections are always closed"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            db_manager = DatabaseManager()
            
            # Even if operations fail, connection should be closed
            with pytest.raises(Exception):
                db_manager.create_session('test_session', '127.0.0.1', 'test_agent')
            
            mock_conn.close.assert_called()
    
    def test_database_transaction_handling(self, app):
        """Test database transaction handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            db_manager = DatabaseManager()
            
            # Test that commits and rollbacks are handled properly
            with patch('builtins.open', mock_open(read_data="CREATE TABLE test;")):
                db_manager.init_database()
                
                # Should attempt to commit on success
                mock_conn.commit.assert_called()
    
    def test_database_schema_validation(self, app):
        """Test database schema validation methods"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            db_manager = DatabaseManager()
            
            # Test schema validation methods
            result = db_manager.validate_schema()
            assert isinstance(result, bool)
    
    def test_database_cleanup_operations(self, app):
        """Test database cleanup operations"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            db_manager = DatabaseManager()
            
            # Test cleanup operations
            db_manager.cleanup_old_sessions()
            db_manager.cleanup_old_messages()
            db_manager.cleanup_old_responses()
            
            # Should execute cleanup queries
            assert mock_cursor.execute.call_count >= 3


class TestDatabaseIntegrationComprehensive:
    """Test database integration scenarios"""
    
    def test_full_database_lifecycle(self, app):
        """Test complete database lifecycle with error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            db_manager = DatabaseManager()
            
            # Initialize database
            db_manager.init_database()
            
            # Create session
            db_manager.create_session('test_session', '127.0.0.1', 'test_agent')
            
            # Create message
            db_manager.create_message('test_session', 'test message')
            
            # Create response
            db_manager.create_response('test_session', 'test response')
            
            # Get messages
            messages = db_manager.get_messages('test_session')
            assert isinstance(messages, list)
            
            # Cleanup
            db_manager.cleanup_old_sessions()
            
            # Verify all operations were called
            assert mock_cursor.execute.call_count >= 10
            mock_conn.commit.assert_called()
            mock_conn.close.assert_called()
    
    def test_database_concurrent_access(self, app):
        """Test database concurrent access handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            db_manager = DatabaseManager()
            
            # Simulate concurrent access
            import threading
            
            def worker():
                try:
                    db_manager.create_session(f'session_{threading.current_thread().ident}', '127.0.0.1', 'test_agent')
                except:
                    pass
            
            threads = [threading.Thread(target=worker) for _ in range(3)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            
            # Should handle concurrent access gracefully
            assert mock_cursor.execute.call_count >= 3
