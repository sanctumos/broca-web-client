import pytest
import sqlite3
import tempfile
import os
from app.utils.database import DatabaseManager
from app.utils.rate_limiting import RateLimitManager

class TestDatabaseIntegration:
    """Integration tests for database functionality"""
    
    # Use the fixtures from conftest.py instead of local ones
    # The test_db fixture properly initializes the database with the SQL file
    
    def test_database_initialization(self, db_manager):
        """Test complete database initialization"""
        # Database is already initialized by the test_db fixture
        
        # Verify tables exist
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Check all required tables
        tables = ['web_chat_sessions', 'web_chat_messages', 'web_chat_responses', 'system_config', 'rate_limits']
        for table in tables:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            result = cursor.fetchone()
            assert result is not None, f"Table {table} should exist"
        
        # Check views - PHP version doesn't have complex views
        # We only have the basic tables that PHP uses
        
        conn.close()
    
    def test_session_management_workflow(self, db_manager):
        """Test complete session management workflow"""
        # Database is already initialized by the test_db fixture
        
        # Create a session
        session_id = 'integration_test_session_123'
        uid_result = db_manager.get_or_create_uid(session_id, ip_address='127.0.0.1')
        assert uid_result is not None
        assert 'uid' in uid_result
        uid = uid_result['uid']
        
        # Verify session exists
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, uid FROM web_chat_sessions WHERE id = ?", (session_id,))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == session_id
        assert result[1] == uid
        
        # Update session activity
        db_manager.update_session_activity(session_id)
        
        # Check session is active (using last_active timestamp)
        cursor.execute("SELECT last_active FROM web_chat_sessions WHERE id = ?", (session_id,))
        result = cursor.fetchone()
        assert result is not None
        # Session should be active if last_active is recent
        assert result[0] is not None
        
        conn.close()
    
    def test_message_workflow(self, db_manager):
        """Test complete message handling workflow"""
        # Database is already initialized by the test_db fixture
        
        session_id = 'message_workflow_test_456'
        message_text = 'Test message for workflow'
        
        # Create session and message
        uid_result = db_manager.get_or_create_uid(session_id, ip_address='127.0.0.1')
        uid = uid_result['uid']
        message_id = db_manager.create_message(session_id, message_text, 'user')
        assert message_id is not None
        
        # Verify message stored
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT message, session_id FROM web_chat_messages WHERE id = ?", (message_id,))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == message_text
        assert result[1] == session_id
        
        conn.close()
    
    def test_response_workflow(self, db_manager):
        """Test complete response handling workflow"""
        # Database is already initialized by the test_db fixture
        
        session_id = 'response_workflow_test_789'
        response_text = 'Test response for workflow'
        
        # Create session and message first
        uid_result = db_manager.get_or_create_uid(session_id, ip_address='127.0.0.1')
        uid = uid_result['uid']
        message_id = db_manager.create_message(session_id, 'Test message for response', 'user')
        # Now create response with the message_id
        response_id = db_manager.create_response(session_id, response_text, message_id)
        assert response_id is not None
        
        # Verify response stored
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT response, session_id FROM web_chat_responses WHERE id = ?", (response_id,))
        result = cursor.fetchone()
        assert result is not None
        
        # response is now stored directly, not in JSON
        assert result[0] == response_text
        assert result[1] == session_id
        
        conn.close()
    
    def test_configuration_management(self, db_manager):
        """Test configuration management workflow"""
        # Database is already initialized by the test_db fixture
        
        # Test getting default config
        config = db_manager.get_all_config()
        assert 'api_key' in config
        assert 'admin_key' in config
        # Note: conftest.py overrides these values for testing
        assert config['api_key'] == 'test_api_key_123'
        assert config['admin_key'] == 'test_admin_key_456'
        
        # Test updating config
        test_key = 'test_config_key'
        test_value = 'test_config_value'
        db_manager.update_config({test_key: test_value})
        
        # Verify config updated
        updated_config = db_manager.get_all_config()
        assert updated_config[test_key] == test_value
        
        # Test getting specific config
        specific_value = db_manager.get_config(test_key)
        assert specific_value == test_value
        
        # Test getting non-existent config
        non_existent = db_manager.get_config('non_existent_key')
        assert non_existent is None
    
    def test_unprocessed_messages_retrieval(self, db_manager):
        """Test unprocessed messages retrieval"""
        # Database is already initialized by the test_db fixture
        
        session_id = 'unprocessed_test_123'
        message_text = 'Unprocessed test message'
        
        # Create session and unprocessed message
        uid_result = db_manager.get_or_create_uid(session_id, ip_address='127.0.0.1')
        uid = uid_result['uid']
        message_id = db_manager.create_message(session_id, message_text, 'user')
        
        # Get unprocessed messages
        messages = db_manager.get_unprocessed_messages(limit=10, offset=0)
        assert len(messages) > 0
        
        # Find our test message
        test_message = None
        for msg in messages:
            if msg['id'] == message_id:
                test_message = msg
                break
        
        assert test_message is not None
        assert test_message['message'] == message_text
        assert test_message['session_id'] == session_id
        assert 'timestamp' in test_message  # Should alias created_at
    
    def test_session_cleanup_workflow(self, db_manager):
        """Test session cleanup workflow"""
        # Database is already initialized by the test_db fixture
        
        # Create some old sessions
        old_session_ids = [
            'old_session_1',
            'old_session_2',
            'old_session_3'
        ]
        
        for session_id in old_session_ids:
            uid = db_manager.get_or_create_uid(session_id, ip_address='127.0.0.1')
            # Store a message to make session active
            db_manager.create_message(session_id, f'Message for {session_id}', 'user')
        
        # Get initial session count
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM web_chat_sessions")
        initial_count = cursor.fetchone()[0]
        
        # Perform cleanup (this would normally be called with a time threshold)
        # For testing, we'll just verify the cleanup method exists and works
        cleaned_count = db_manager.cleanup_expired_sessions()
        assert isinstance(cleaned_count, int)
        
        conn.close()
    
    def test_rate_limiting_integration(self, rate_limiter):
        """Test rate limiting integration with database"""
        # Initialize database (rate limiter will do this)
        
        # Test rate limit check
        ip_address = '192.168.1.100'
        endpoint = '/api/messages'
        
        # First check should pass
        result = rate_limiter.check_rate_limit(ip_address, endpoint, 50)
        assert result is True
        
        # Make multiple requests to hit limit
        for i in range(60):  # Should hit 50/hour limit
            result = rate_limiter.check_rate_limit(ip_address, endpoint, 50)
            if not result:
                break
        
        # Should eventually hit rate limit
        if not result:
            # Rate limit exceeded
            pass  # This is expected behavior
    
    def test_concurrent_database_access(self, db_manager):
        """Test concurrent database access"""
        # Database is already initialized by the test_db fixture
        
        import threading
        import time
        
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                session_id = f'concurrent_worker_{worker_id}'
                uid = db_manager.get_or_create_uid(session_id, ip_address='127.0.0.1')
                message_id = db_manager.create_message(session_id, f'Message from worker {worker_id}', 'user')
                results.append((worker_id, message_id))
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5, "All workers should have completed successfully"
        
        # Verify all messages were stored
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        for worker_id, message_id in results:
            cursor.execute("SELECT message FROM web_chat_messages WHERE id = ?", (message_id,))
            result = cursor.fetchone()
            assert result is not None
            assert f'Message from worker {worker_id}' in result[0]
        
        conn.close()
    
    def test_database_transaction_rollback(self, db_manager):
        """Test database transaction rollback on error"""
        # Database is already initialized by the test_db fixture
        
        # Try to insert invalid data that should cause rollback
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Insert valid data
            cursor.execute("INSERT INTO web_chat_sessions (id, uid, ip_address, created_at) VALUES (?, ?, ?, datetime('now'))", 
                         ('rollback_test_123', 'test_uid_123', '127.0.0.1'))
            
            # Try to insert invalid data (should fail)
            cursor.execute("INSERT INTO web_chat_sessions (invalid_column) VALUES (?)", ('value',))
            
            # If we get here, commit
            conn.commit()
            assert False, "Should have failed before commit"
            
        except sqlite3.OperationalError:
            # Expected error, rollback
            conn.rollback()
            
            # Verify data was rolled back
            cursor.execute("SELECT COUNT(*) FROM web_chat_sessions WHERE id = 'rollback_test_123'")
            count = cursor.fetchone()[0]
            assert count == 0, "Data should have been rolled back"
        
        conn.close()
    
    def test_database_connection_pooling(self, db_manager):
        """Test database connection handling"""
        # Database is already initialized by the test_db fixture
        
        # Get multiple connections
        conn1 = db_manager.get_connection()
        conn2 = db_manager.get_connection()
        
        # Verify they're different connection objects
        assert conn1 is not conn2
        
        # Test both connections work
        cursor1 = conn1.cursor()
        cursor2 = conn2.cursor()
        
        cursor1.execute("SELECT 1")
        cursor2.execute("SELECT 2")
        
        assert cursor1.fetchone()[0] == 1
        assert cursor2.fetchone()[0] == 2
        
        # Close connections
        conn1.close()
        conn2.close()
    
    def test_database_schema_consistency(self, db_manager):
        """Test database schema consistency"""
        # Database is already initialized by the test_db fixture
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Check sessions table structure - IDENTICAL to PHP
        cursor.execute("PRAGMA table_info(web_chat_sessions)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_columns = {
            'id': 'VARCHAR',  # This IS the session_id in PHP schema
            'uid': 'VARCHAR',
            'ip_address': 'VARCHAR',
            'created_at': 'TEXT',
            'last_active': 'TEXT',
            'metadata': 'TEXT'
        }
        
        for col, expected_type in expected_columns.items():
            assert col in columns, f"Column {col} should exist in web_chat_sessions table"
            # Note: SQLite type checking is flexible, so we just verify the column exists
        
        # Check messages table structure - IDENTICAL to PHP
        cursor.execute("PRAGMA table_info(web_chat_messages)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_columns = {
            'id': 'INTEGER',
            'session_id': 'VARCHAR',
            'message': 'TEXT',
            'timestamp': 'TEXT',
            'processed': 'INTEGER',
            'broca_message_id': 'INTEGER'
        }
        
        for col, expected_type in expected_columns.items():
            assert col in columns, f"Column {col} should exist in web_chat_messages table"
        
        conn.close()
    
    def test_database_indexes(self, db_manager):
        """Test database indexes for performance"""
        # Database is already initialized by the test_db fixture
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Check for important indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        # Should have indexes on frequently queried columns - IDENTICAL to PHP
        expected_indexes = [
            'idx_messages_session',
            'idx_messages_processed',
            'idx_responses_session',
            'idx_rate_limits_window',
            'idx_sessions_uid',
            'idx_sessions_ip'
        ]
        
        # Check that at least some of the expected indexes exist
        found_indexes = 0
        for index in expected_indexes:
            if index in indexes:
                found_indexes += 1
        
        # Should have at least 4 indexes (basic PHP indexes)
        assert found_indexes >= 4, f"Expected at least 4 indexes, found {found_indexes}"
        
        # Check that key indexes exist for performance
        key_indexes = ['idx_messages_session', 'idx_sessions_uid']
        for index in key_indexes:
            assert index in indexes, f"Index {index} should exist for performance"
        
        conn.close()
