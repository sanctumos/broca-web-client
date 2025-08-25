import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from app.widget.routes import (
    widget_home, widget_demo, widget_init, widget_config,
    widget_health, widget_static, widget_not_found, widget_error
)


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
        assert 'widget' in blueprint_names  # Test widget blueprint registration


class TestWidgetRoutes:
    """Test widget route functions for complete coverage"""
    
    def test_widget_home(self, app):
        """Test widget home route - covers line 18"""
        with app.test_request_context():
            with patch('app.widget.routes.render_template') as mock_render:
                mock_render.return_value = '<html>Widget Home</html>'
                result = widget_home()
                
                mock_render.assert_called_once_with('widget.html')
                assert result == '<html>Widget Home</html>'

    def test_widget_demo(self, app):
        """Test widget demo route - covers line 24"""
        with app.test_request_context():
            with patch('app.widget.routes.render_template') as mock_render:
                mock_render.return_value = '<html>Widget Demo</html>'
                result = widget_demo()
                
                mock_render.assert_called_once_with('widget_demo.html')
                assert result == '<html>Widget Demo</html>'

    def test_widget_init_success(self, app):
        """Test widget init route with valid API key - covers lines 30-48"""
        with app.test_request_context():
            with patch('app.widget.routes.request') as mock_request, \
                 patch('app.widget.routes.jsonify') as mock_jsonify, \
                 patch('app.widget.routes.datetime') as mock_datetime:
                
                # Mock request arguments
                def mock_args_get(key, default=None):
                    args = {
                        'apiKey': 'test-api-key',
                        'position': 'bottom-left',
                        'theme': 'dark',
                        'title': 'Custom Chat',
                        'primaryColor': '#ff0000',
                        'language': 'es',
                        'autoOpen': 'true',
                        'notifications': 'false',
                        'sound': 'false'
                    }
                    return args.get(key, default)
                
                mock_request.args.get = mock_args_get
                
                mock_request.host_url = 'http://localhost:8000/'
                
                # Mock datetime
                mock_datetime.now.return_value.isoformat.return_value = '2025-08-25T13:00:00'
                
                # Mock jsonify
                mock_response = MagicMock()
                mock_jsonify.return_value = mock_response
                
                result = widget_init()
                
                # Verify jsonify was called with correct data
                mock_jsonify.assert_called_once()
                call_args = mock_jsonify.call_args[0][0]
                
                assert call_args['success'] is True
                assert call_args['message'] == 'Success'
                assert call_args['data']['config']['apiKey'] == 'test-api-key'
                assert call_args['data']['config']['position'] == 'bottom-left'
                assert call_args['data']['config']['theme'] == 'dark'
                assert call_args['data']['config']['title'] == 'Custom Chat'
                assert call_args['data']['config']['primaryColor'] == '#ff0000'
                assert call_args['data']['config']['language'] == 'es'
                assert call_args['data']['config']['autoOpen'] is True
                assert call_args['data']['config']['notifications'] is False
                assert call_args['data']['config']['sound'] is False
                
                assert result == mock_response

    def test_widget_init_missing_api_key(self, app):
        """Test widget init route without API key - covers error path"""
        with app.test_request_context():
            with patch('app.widget.routes.request') as mock_request, \
                 patch('app.widget.routes.jsonify') as mock_jsonify:
                
                # Mock request arguments - no API key
                def mock_args_get(key, default=None):
                    args = {
                        'position': 'bottom-right',
                        'theme': 'light'
                    }
                    return args.get(key, default)
                
                mock_request.args.get = mock_args_get
                
                # Mock jsonify
                mock_response = MagicMock()
                mock_jsonify.return_value = mock_response
                
                result = widget_init()
                
                # Verify error response
                mock_jsonify.assert_called_once()
                call_args = mock_jsonify.call_args[0][0]
                
                assert call_args['success'] is False
                assert call_args['error'] == 'API key is required'
                
                # Error response returns (response, status_code) tuple
                assert result[0] == mock_response
                assert result[1] == 400

    def test_widget_config(self, app):
        """Test widget config route - covers line 70"""
        with app.test_request_context():
            with patch('app.widget.routes.jsonify') as mock_jsonify, \
                 patch('app.widget.routes.datetime') as mock_datetime:
                
                # Mock datetime
                mock_datetime.now.return_value.isoformat.return_value = '2025-08-25T13:00:00'
                
                # Mock jsonify
                mock_response = MagicMock()
                mock_jsonify.return_value = mock_response
                
                result = widget_config()
                
                # Verify jsonify was called with correct data
                mock_jsonify.assert_called_once()
                call_args = mock_jsonify.call_args[0][0]
                
                assert call_args['success'] is True
                assert call_args['message'] == 'Success'
                assert 'positions' in call_args['data']
                assert 'themes' in call_args['data']
                assert 'languages' in call_args['data']
                assert 'defaults' in call_args['data']
                
                assert result == mock_response

    def test_widget_health(self, app):
        """Test widget health route - covers line 95"""
        with app.test_request_context():
            with patch('app.widget.routes.jsonify') as mock_jsonify, \
                 patch('app.widget.routes.datetime') as mock_datetime:
                
                # Mock datetime
                mock_datetime.now.return_value.isoformat.return_value = '2025-08-25T13:00:00'
                
                # Mock jsonify
                mock_response = MagicMock()
                mock_jsonify.return_value = mock_response
                
                result = widget_health()
                
                # Verify jsonify was called with correct data
                mock_jsonify.assert_called_once()
                call_args = mock_jsonify.call_args[0][0]
                
                assert call_args['success'] is True
                assert call_args['message'] == 'Success'
                assert call_args['data']['status'] == 'healthy'
                assert call_args['data']['version'] == '1.0.0'
                assert call_args['data']['api_status'] == 'connected'
                
                assert result == mock_response

    def test_widget_static(self, app):
        """Test widget static file serving - covers line 110"""
        with app.test_request_context():
            with patch('app.widget.routes.send_from_directory') as mock_send, \
                 patch('app.widget.routes.bp') as mock_bp:
                
                mock_bp.static_folder = '/path/to/static'
                mock_response = MagicMock()
                mock_send.return_value = mock_response
                
                result = widget_static('test.css')
                
                mock_send.assert_called_once_with('/path/to/static', 'test.css')
                assert result == mock_response

    def test_widget_not_found(self, app):
        """Test widget 404 error handler - covers line 116"""
        with app.test_request_context():
            with patch('app.widget.routes.jsonify') as mock_jsonify:
                
                # Mock jsonify
                mock_response = MagicMock()
                mock_jsonify.return_value = mock_response
                
                error = MagicMock()
                result = widget_not_found(error)
                
                # Verify jsonify was called with correct data
                mock_jsonify.assert_called_once()
                call_args = mock_jsonify.call_args[0][0]
                
                assert call_args['success'] is False
                assert call_args['error'] == 'Widget endpoint not found'
                
                # Error handlers return (response, status_code) tuples
                assert result[0] == mock_response
                assert result[1] == 404

    def test_widget_error(self, app):
        """Test widget 500 error handler - covers line 125"""
        with app.test_request_context():
            with patch('app.widget.routes.jsonify') as mock_jsonify:
                
                # Mock jsonify
                mock_response = MagicMock()
                mock_jsonify.return_value = mock_response
                
                error = MagicMock()
                result = widget_error(error)
                
                # Verify jsonify was called with correct data
                mock_jsonify.assert_called_once()
                call_args = mock_jsonify.call_args[0][0]
                
                assert call_args['success'] is False
                assert call_args['error'] == 'Internal widget error'
                
                # Error handlers return (response, status_code) tuples
                assert result[0] == mock_response
                assert result[1] == 500
