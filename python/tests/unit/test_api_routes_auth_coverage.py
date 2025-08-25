import pytest
from unittest.mock import patch, MagicMock
from app import create_app

class TestAPIAuthenticationCoverage:
    """Test authentication functions for 100% coverage"""
    
    def test_require_auth_internal_missing_header(self):
        """Test missing authorization header"""
        from app.api.routes import require_auth_internal
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST'):
            # No Authorization header
            result = require_auth_internal()
            
            assert result[1] == 401  # Unauthorized
            assert 'Authentication required' in result[0].json['error']
    
    def test_require_auth_internal_invalid_header_format(self):
        """Test invalid authorization header format"""
        from app.api.routes import require_auth_internal
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'InvalidFormat'}):
            # Invalid header format (no 'Bearer ' prefix)
            result = require_auth_internal()
            
            assert result[1] == 401  # Unauthorized
            assert 'Authentication required' in result[0].json['error']
    
    @patch('app.api.routes.get_db')
    def test_require_auth_internal_invalid_key(self, mock_get_db):
        """Test invalid API key"""
        from app.api.routes import require_auth_internal
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'Bearer invalid_key'}):
            # Mock database to return config with different keys
            mock_db = MagicMock()
            mock_db.get_all_config.return_value = {
                'api_key': 'valid_api_key',
                'admin_key': 'valid_admin_key'
            }
            mock_get_db.return_value = mock_db
            
            result = require_auth_internal()
            
            assert result[1] == 401  # Unauthorized
            assert 'Invalid API key' in result[0].json['error']
    
    @patch('app.api.routes.get_db')
    def test_require_auth_internal_valid_api_key(self, mock_get_db):
        """Test valid API key"""
        from app.api.routes import require_auth_internal
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'Bearer valid_api_key'}):
            # Mock database to return config with matching key
            mock_db = MagicMock()
            mock_db.get_all_config.return_value = {
                'api_key': 'valid_api_key',
                'admin_key': 'valid_admin_key'
            }
            mock_get_db.return_value = mock_db
            
            result = require_auth_internal()
            
            assert result is None  # Authentication successful
    
    @patch('app.api.routes.get_db')
    def test_require_auth_internal_valid_admin_key(self, mock_get_db):
        """Test valid admin key (should also work for require_auth_internal)"""
        from app.api.routes import require_auth_internal
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'Bearer valid_admin_key'}):
            # Mock database to return config with matching admin key
            mock_db = MagicMock()
            mock_db.get_all_config.return_value = {
                'api_key': 'valid_api_key',
                'admin_key': 'valid_admin_key'
            }
            mock_get_db.return_value = mock_db
            
            result = require_auth_internal()
            
            assert result is None  # Authentication successful
    
    def test_require_admin_auth_internal_missing_header(self):
        """Test missing authorization header for admin"""
        from app.api.routes import require_admin_auth_internal
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST'):
            # No Authorization header
            result = require_admin_auth_internal()
            
            assert result[1] == 401  # Unauthorized
            assert 'Authentication required' in result[0].json['error']
    
    def test_require_admin_auth_internal_invalid_header_format(self):
        """Test invalid authorization header format for admin"""
        from app.api.routes import require_admin_auth_internal
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'InvalidFormat'}):
            # Invalid header format (no 'Bearer ' prefix)
            result = require_admin_auth_internal()
            
            assert result[1] == 401  # Unauthorized
            assert 'Authentication required' in result[0].json['error']
    
    @patch('app.api.routes.get_db')
    def test_require_admin_auth_internal_invalid_key(self, mock_get_db):
        """Test invalid admin key"""
        from app.api.routes import require_admin_auth_internal
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'Bearer invalid_admin_key'}):
            # Mock database to return config with different admin key
            mock_db = MagicMock()
            mock_db.get_all_config.return_value = {
                'admin_key': 'valid_admin_key'
            }
            mock_get_db.return_value = mock_db
            
            result = require_admin_auth_internal()
            
            assert result[1] == 401  # Unauthorized
            assert 'Invalid admin key' in result[0].json['error']
    
    @patch('app.api.routes.get_db')
    def test_require_admin_auth_internal_valid_key(self, mock_get_db):
        """Test valid admin key"""
        from app.api.routes import require_admin_auth_internal
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'Bearer valid_admin_key'}):
            # Mock database to return config with matching admin key
            mock_db = MagicMock()
            mock_db.get_all_config.return_value = {
                'admin_key': 'valid_admin_key'
            }
            mock_get_db.return_value = mock_db
            
            result = require_admin_auth_internal()
            
            assert result is None  # Authentication successful
    
    @patch('app.api.routes.get_db')
    def test_require_auth_internal_database_error(self, mock_get_db):
        """Test database error during authentication"""
        from app.api.routes import require_auth_internal
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'Bearer test_key'}):
            # Mock database to raise exception
            mock_db = MagicMock()
            mock_db.get_all_config.side_effect = Exception("Database error")
            mock_get_db.return_value = mock_db
            
            # Database errors should cause the function to fail
            with pytest.raises(Exception) as exc_info:
                require_auth_internal()
            
            assert "Database error" in str(exc_info.value)
    
    @patch('app.api.routes.get_db')
    def test_require_admin_auth_internal_database_error(self, mock_get_db):
        """Test database error during admin authentication"""
        from app.api.routes import require_admin_auth_internal
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'Bearer test_key'}):
            # Mock database to raise exception
            mock_db = MagicMock()
            mock_db.get_all_config.side_effect = Exception("Database error")
            mock_get_db.return_value = mock_db
            
            # Database errors should cause the function to fail
            with pytest.raises(Exception) as exc_info:
                require_admin_auth_internal()
            
            assert "Database error" in str(exc_info.value)
