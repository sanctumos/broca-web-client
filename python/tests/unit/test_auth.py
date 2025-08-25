import pytest
from unittest.mock import patch, MagicMock
from app.api.auth import require_auth, require_admin_auth
from flask import Flask, request, jsonify

class TestAuthDecorators:
    """Test authentication decorators"""
    
    def test_require_auth_success(self, app_context, request_context):
        """Test successful API key authentication"""
        def test_function():
            return "success"
        
        with patch('app.api.auth.request') as mock_request:
            mock_request.headers = {'Authorization': 'Bearer valid_api_key'}
            
            with patch('app.api.auth.DatabaseManager') as mock_db_class:
                mock_db = MagicMock()
                mock_db.get_all_config.return_value = {'api_key': 'valid_api_key'}
                mock_db_class.return_value = mock_db
                
                with patch('app.api.auth.current_app') as mock_app:
                    mock_app.config = {'DEFAULT_API_KEY': 'default_key'}
                    
                    decorated_func = require_auth(test_function)
                    result = decorated_func()
                    
                    assert result == "success"
    
    def test_require_auth_missing_header(self, app_context, request_context):
        """Test authentication with missing header"""
        def test_function():
            return "success"
        
        with patch('app.api.auth.request') as mock_request:
            mock_request.headers = {}
            
            decorated_func = require_auth(test_function)
            result = decorated_func()
            
            assert result[1] == 401
            data = result[0].get_json()
            assert data['success'] is False
            assert data['error'] == 'Authentication required'
            assert data['code'] == 401
    
    def test_require_auth_malformed_header(self, app_context, request_context):
        """Test authentication with malformed header"""
        def test_function():
            return "success"
        
        with patch('app.api.auth.request') as mock_request:
            mock_request.headers = {'Authorization': 'InvalidFormat valid_api_key'}
            
            decorated_func = require_auth(test_function)
            result = decorated_func()
            
            assert result[1] == 401
            data = result[0].get_json()
            assert data['success'] is False
            assert data['error'] == 'Authentication required'
            assert data['code'] == 401
    
    def test_require_auth_invalid_key(self, app_context, request_context):
        """Test authentication with invalid API key"""
        def test_function():
            return "success"
        
        with patch('app.api.auth.request') as mock_request:
            mock_request.headers = {'Authorization': 'Bearer invalid_key'}
            
            with patch('app.api.auth.DatabaseManager') as mock_db_class:
                mock_db = MagicMock()
                mock_db.get_all_config.return_value = {'api_key': 'valid_api_key'}
                mock_db_class.return_value = mock_db
                
                with patch('app.api.auth.current_app') as mock_app:
                    mock_app.config = {'DEFAULT_API_KEY': 'default_key'}
                    
                    decorated_func = require_auth(test_function)
                    result = decorated_func()
                    
                    assert result[1] == 401
                    data = result[0].get_json()
                    assert data['success'] is False
                    assert data['error'] == 'Invalid API key'
                    assert data['code'] == 401
    
    def test_require_auth_fallback_to_default(self, app_context, request_context):
        """Test authentication falls back to default API key"""
        def test_function():
            return "success"
        
        with patch('app.api.auth.request') as mock_request:
            mock_request.headers = {'Authorization': 'Bearer default_key'}
            
            with patch('app.api.auth.DatabaseManager') as mock_db_class:
                mock_db = MagicMock()
                mock_db.get_all_config.return_value = {}  # No config in DB
                mock_db_class.return_value = mock_db
                
                with patch('app.api.auth.current_app') as mock_app:
                    mock_app.config = {'DEFAULT_API_KEY': 'default_key'}
                    
                    decorated_func = require_auth(test_function)
                    result = decorated_func()
                    
                    assert result == "success"
    
    def test_require_auth_db_exception(self, app_context, request_context):
        """Test authentication when database throws exception - should fail"""
        def test_function():
            return "success"
        
        with patch('app.api.auth.request') as mock_request:
            mock_request.headers = {'Authorization': 'Bearer any_key'}
            
            with patch('app.api.auth.DatabaseManager') as mock_db_class:
                mock_db = MagicMock()
                mock_db.get_all_config.side_effect = Exception("DB Error")
                mock_db_class.return_value = mock_db
                
                with patch('app.api.auth.current_app') as mock_app:
                    mock_app.config = {'DEFAULT_API_KEY': 'default_key'}
                    
                    decorated_func = require_auth(test_function)
                    
                    # Should fail when database throws exception
                    with pytest.raises(Exception, match="DB Error"):
                        decorated_func()
    
    def test_require_admin_auth_success(self, app_context, request_context):
        """Test successful admin key authentication"""
        def test_function():
            return "success"
        
        with patch('app.api.auth.request') as mock_request:
            mock_request.headers = {'Authorization': 'Bearer valid_admin_key'}
            
            with patch('app.api.auth.DatabaseManager') as mock_db_class:
                mock_db = MagicMock()
                mock_db.get_all_config.return_value = {'admin_key': 'valid_admin_key'}
                mock_db_class.return_value = mock_db
                
                with patch('app.api.auth.current_app') as mock_app:
                    mock_app.config = {'DEFAULT_ADMIN_KEY': 'default_admin_key'}
                    
                    decorated_func = require_admin_auth(test_function)
                    result = decorated_func()
                    
                    assert result == "success"
    
    def test_require_admin_auth_missing_header(self, app_context, request_context):
        """Test admin authentication with missing header"""
        def test_function():
            return "success"
        
        with patch('app.api.auth.request') as mock_request:
            mock_request.headers = {}
            
            decorated_func = require_admin_auth(test_function)
            result = decorated_func()
            
            assert result[1] == 401
            data = result[0].get_json()
            assert data['success'] is False
            assert data['error'] == 'Authentication required'
            assert data['code'] == 401
    
    def test_require_admin_auth_malformed_header(self, app_context, request_context):
        """Test admin authentication with malformed header"""
        def test_function():
            return "success"
        
        with patch('app.api.auth.request') as mock_request:
            mock_request.headers = {'Authorization': 'InvalidFormat valid_admin_key'}
            
            decorated_func = require_admin_auth(test_function)
            result = decorated_func()
            
            assert result[1] == 401
            data = result[0].get_json()
            assert data['success'] is False
            assert data['error'] == 'Authentication required'
            assert data['code'] == 401
    
    def test_require_admin_auth_invalid_key(self, app_context, request_context):
        """Test admin authentication with invalid admin key"""
        def test_function():
            return "success"
        
        with patch('app.api.auth.request') as mock_request:
            mock_request.headers = {'Authorization': 'Bearer invalid_admin_key'}
            
            with patch('app.api.auth.DatabaseManager') as mock_db_class:
                mock_db = MagicMock()
                mock_db.get_all_config.return_value = {'admin_key': 'valid_admin_key'}
                mock_db_class.return_value = mock_db
                
                with patch('app.api.auth.current_app') as mock_app:
                    mock_app.config = {'DEFAULT_ADMIN_KEY': 'default_admin_key'}
                    
                    decorated_func = require_admin_auth(test_function)
                    result = decorated_func()
                    
                    assert result[1] == 401
                    data = result[0].get_json()
                    assert data['success'] is False
                    assert data['error'] == 'Invalid admin key'
                    assert data['code'] == 401
    
    def test_require_admin_auth_fallback_to_default(self, app_context, request_context):
        """Test admin authentication falls back to default admin key"""
        def test_function():
            return "success"
        
        with patch('app.api.auth.request') as mock_request:
            mock_request.headers = {'Authorization': 'Bearer default_admin_key'}
            
            with patch('app.api.auth.DatabaseManager') as mock_db_class:
                mock_db = MagicMock()
                mock_db.get_all_config.return_value = {}  # No config in DB
                mock_db_class.return_value = mock_db
                
                with patch('app.api.auth.current_app') as mock_app:
                    mock_app.config = {'DEFAULT_ADMIN_KEY': 'default_admin_key'}
                    
                    decorated_func = require_admin_auth(test_function)
                    result = decorated_func()
                    
                    assert result == "success"
    
    def test_require_admin_auth_db_exception(self, app_context, request_context):
        """Test admin authentication when database throws exception - should fail"""
        def test_function():
            return "success"
        
        with patch('app.api.auth.request') as mock_request:
            mock_request.headers = {'Authorization': 'Bearer any_key'}
            
            with patch('app.api.auth.DatabaseManager') as mock_db_class:
                mock_db = MagicMock()
                mock_db.get_all_config.side_effect = Exception("DB Error")
                mock_db_class.return_value = mock_db
                
                with patch('app.api.auth.current_app') as mock_app:
                    mock_app.config = {'DEFAULT_ADMIN_KEY': 'default_admin_key'}
                    
                    decorated_func = require_admin_auth(test_function)
                    
                    # Should fail when database throws exception
                    with pytest.raises(Exception, match="DB Error"):
                        decorated_func()
    
    def test_decorator_preserves_function_metadata(self, app_context, request_context):
        """Test that decorators preserve function metadata"""
        def test_function():
            """Test function docstring"""
            return "success"
        
        test_function.test_attr = "test_value"
        
        decorated_api = require_auth(test_function)
        decorated_admin = require_admin_auth(test_function)
        
        assert decorated_api.__name__ == "test_function"
        assert decorated_api.__doc__ == "Test function docstring"
        assert decorated_api.test_attr == "test_value"
        
        assert decorated_admin.__name__ == "test_function"
        assert decorated_admin.__doc__ == "Test function docstring"
        assert decorated_admin.test_attr == "test_value"
