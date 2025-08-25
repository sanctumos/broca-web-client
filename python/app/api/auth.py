from functools import wraps
from flask import request, jsonify, current_app
from app.utils.database import DatabaseManager

def require_auth(f):
    """Require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False, 
                'error': 'Authentication required',
                'code': 401
            }), 401
        
        api_key = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Get API key from database
        db_manager = DatabaseManager()
        config = db_manager.get_all_config()
        stored_api_key = config.get('api_key', current_app.config['DEFAULT_API_KEY'])
        
        if api_key != stored_api_key:
            return jsonify({
                'success': False, 
                'error': 'Invalid API key',
                'code': 401
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_admin_auth(f):
    """Require admin password authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False, 
                'error': 'Authentication required',
                'code': 401
            }), 401
        
        admin_key = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Get admin key from database
        db_manager = DatabaseManager()
        config = db_manager.get_all_config()
        stored_admin_key = config.get('admin_key', current_app.config['DEFAULT_ADMIN_KEY'])
        
        if admin_key != stored_admin_key:
            return jsonify({
                'success': False, 
                'error': 'Invalid admin key',
                'code': 401
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function
