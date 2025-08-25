import pytest
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from app.utils.database import DatabaseManager


class TestDatabaseEdgeCases:
    """Test database manager edge cases and error handling"""
    
    def test_create_response_connection_error(self):
        """Test create_response with connection error"""
        # Create a database manager that will fail when trying to connect
        with pytest.raises(sqlite3.OperationalError):
            db_manager = DatabaseManager('/nonexistent/path/db.sqlite')
            db_manager.create_response('session_test', 'test response')
    
    def test_get_session_responses_connection_error(self):
        """Test get_session_responses with connection error"""
        # Create a database manager that will fail when trying to connect
        with pytest.raises(sqlite3.OperationalError):
            db_manager = DatabaseManager('/nonexistent/path/db.sqlite')
            db_manager.get_session_responses('session_test')
