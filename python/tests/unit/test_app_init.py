import pytest
from app import create_app


class TestAppInit:
    """Test app initialization and error handlers"""
    
    def test_create_app(self):
        """Test app creation"""
        app = create_app()
        assert app is not None
        assert app.name == 'app'
    
    def test_error_handler_405_api_path(self, app):
        """Test 405 Method Not Allowed for API paths"""
        with app.test_client() as client:
            # Test with API path
            response = client.get('/api/v1/')
            assert response.status_code == 400  # Missing action parameter
            
            # Test 405 for API path
            response = client.put('/api/v1/')  # PUT method not allowed
            assert response.status_code == 405
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Method not allowed'
    
    def test_error_handler_404_api_path(self, app):
        """Test 404 Not Found for API paths"""
        with app.test_client() as client:
            response = client.get('/api/nonexistent/')
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
            assert data['error'] == 'Endpoint not found'
    
    def test_error_handler_non_api_paths(self, app):
        """Test that non-API paths get default Flask error handling"""
        with app.test_client() as client:
            # Test 405 for non-API path
            response = client.put('/chat/')  # PUT method not allowed
            assert response.status_code == 405
            
            # Test 404 for non-API path
            response = client.get('/nonexistent/')
            assert response.status_code == 404
    
    def test_cors_enabled(self, app):
        """Test that CORS is properly enabled"""
        with app.test_client() as client:
            response = client.options('/api/v1/')
            assert response.status_code == 200
            # CORS headers should be present
            assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_blueprints_registered(self, app):
        """Test that all blueprints are registered"""
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert 'api' in blueprint_names
        assert 'admin' in blueprint_names
        assert 'chat' in blueprint_names
