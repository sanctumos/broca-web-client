"""Simple widget tests to achieve 100% coverage"""

import pytest
from unittest.mock import patch, MagicMock
from app.widget.routes import (
    widget_home, widget_demo, widget_init, widget_config,
    widget_health, widget_static, widget_not_found, widget_error
)


def test_widget_home():
    """Test widget home route - covers line 18"""
    with patch('app.widget.routes.render_template') as mock_render:
        mock_render.return_value = '<html>Widget Home</html>'
        result = widget_home()
        mock_render.assert_called_once_with('widget.html')
        assert result == '<html>Widget Home</html>'


def test_widget_demo():
    """Test widget demo route - covers line 24"""
    with patch('app.widget.routes.render_template') as mock_render:
        mock_render.return_value = '<html>Widget Demo</html>'
        result = widget_demo()
        mock_render.assert_called_once_with('widget_demo.html')
        assert result == '<html>Widget Demo</html>'


def test_widget_init_success():
    """Test widget init route with valid API key - covers lines 30-48"""
    with patch('app.widget.routes.request') as mock_request, \
         patch('app.widget.routes.jsonify') as mock_jsonify, \
         patch('app.widget.routes.datetime') as mock_datetime:
        
        # Mock request arguments
        mock_request.args.get.side_effect = lambda key, default=None: {
            'apiKey': 'test-api-key',
            'position': 'bottom-left',
            'theme': 'dark',
            'title': 'Custom Chat',
            'primaryColor': '#ff0000',
            'language': 'es',
            'autoOpen': 'true',
            'notifications': 'false',
            'sound': 'false'
        }.get(key, default)
        
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


def test_widget_init_missing_api_key():
    """Test widget init route without API key - covers error path"""
    with patch('app.widget.routes.request') as mock_request, \
         patch('app.widget.routes.jsonify') as mock_jsonify:
        
        # Mock request arguments - no API key
        mock_request.args.get.side_effect = lambda key, default=None: {
            'position': 'bottom-right',
            'theme': 'light'
        }.get(key, default)
        
        # Mock jsonify
        mock_response = MagicMock()
        mock_jsonify.return_value = mock_response
        
        result = widget_init()
        
        # Verify error response
        mock_jsonify.assert_called_once()
        call_args = mock_jsonify.call_args[0][0]
        
        assert call_args['success'] is False
        assert call_args['error'] == 'API key is required'
        
        assert result == mock_response


def test_widget_config():
    """Test widget config route - covers line 70"""
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


def test_widget_health():
    """Test widget health route - covers line 95"""
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


def test_widget_static():
    """Test widget static file serving - covers line 110"""
    with patch('app.widget.routes.send_from_directory') as mock_send, \
         patch('app.widget.routes.bp') as mock_bp:
        
        mock_bp.static_folder = '/path/to/static'
        mock_response = MagicMock()
        mock_send.return_value = mock_response
        
        result = widget_static('test.css')
        
        mock_send.assert_called_once_with('/path/to/static', 'test.css')
        assert result == mock_response


def test_widget_not_found():
    """Test widget 404 error handler - covers line 116"""
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
        
        assert result == mock_response


def test_widget_error():
    """Test widget 500 error handler - covers line 125"""
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
        
        assert result == mock_response
