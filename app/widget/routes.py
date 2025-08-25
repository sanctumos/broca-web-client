"""
Widget-specific routes for the embeddable chat widget
"""

from flask import (
    render_template, jsonify, request, current_app,
    send_from_directory, abort
)
from . import bp
import os
import json
from datetime import datetime


@bp.route('/')
def widget_home():
    """Widget home page - shows embed instructions and demo"""
    return render_template('widget.html')


@bp.route('/demo')
def widget_demo():
    """Widget demo page - interactive testing environment"""
    return render_template('widget_demo.html')


@bp.route('/init')
def widget_init():
    """Widget initialization endpoint - returns configuration and assets"""
    config = {
        'apiKey': request.args.get('apiKey'),
        'position': request.args.get('position', 'bottom-right'),
        'theme': request.args.get('theme', 'light'),
        'title': request.args.get('title', 'Chat with us'),
        'primaryColor': request.args.get('primaryColor', '#007bff'),
        'language': request.args.get('language', 'en'),
        'autoOpen': request.args.get('autoOpen', 'false').lower() == 'true',
        'notifications': request.args.get('notifications', 'true').lower() == 'true',
        'sound': request.args.get('sound', 'true').lower() == 'true'
    }
    
    if not config['apiKey']:
        return jsonify({
            'success': False,
            'error': 'API key is required'
        }), 400
    
    return jsonify({
        'success': True,
        'message': 'Success',
        'timestamp': datetime.now().isoformat(),
        'data': {
            'config': config,
            'assets': {
                'css': '/widget/static/css/widget.css',
                'js': '/widget/static/js/chat-widget.js',
                'icons': '/widget/static/assets/icons/'
            },
            'api': {
                'baseUrl': request.host_url.rstrip('/'),
                'endpoint': '/api/v1/'
            }
        }
    })


@bp.route('/config')
def widget_config():
    """Widget configuration endpoint - returns available options"""
    return jsonify({
        'success': True,
        'message': 'Success',
        'timestamp': datetime.now().isoformat(),
        'data': {
            'positions': ['bottom-right', 'bottom-left', 'top-right', 'top-left'],
            'themes': ['light', 'dark', 'auto'],
            'languages': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'],
            'defaults': {
                'position': 'bottom-right',
                'theme': 'light',
                'title': 'Chat with us',
                'primaryColor': '#007bff',
                'language': 'en',
                'autoOpen': False,
                'notifications': True,
                'sound': True
            }
        }
    })


@bp.route('/health')
def widget_health():
    """Widget health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Success',
        'timestamp': datetime.now().isoformat(),
        'data': {
            'status': 'healthy',
            'version': '1.0.0',
            'api_status': 'connected'
        }
    })


@bp.route('/static/<path:filename>')
def widget_static(filename):
    """Serve widget static files"""
    return send_from_directory(bp.static_folder, filename)


@bp.errorhandler(404)
def widget_not_found(error):
    """Handle 404 errors for widget routes"""
    return jsonify({
        'success': False,
        'error': 'Widget endpoint not found'
    }), 404


@bp.errorhandler(500)
def widget_error(error):
    """Handle 500 errors for widget routes"""
    return jsonify({
        'success': False,
        'error': 'Internal widget error'
    }), 500
