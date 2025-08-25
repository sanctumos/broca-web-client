from flask import Blueprint, request, jsonify, render_template, current_app
from app.utils.database import DatabaseManager
from datetime import datetime
import json

bp = Blueprint('chat', __name__)

def get_db():
    """Get database manager instance"""
    return DatabaseManager()

@bp.route('/')
def chat_interface():
    """Main chat interface page"""
    return render_template('chat.html')

@bp.route('/widget.js')
def chat_widget_js():
    """JavaScript widget for embedding in other sites"""
    from flask import send_file
    import os
    template_path = os.path.join(current_app.root_path, 'templates', 'widget.js')
    return send_file(template_path, mimetype='application/javascript')

@bp.route('/api/send_message', methods=['POST'])
def send_message():
    """Send a message from the chat interface"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON'}), 400
    
    session_id = data.get('session_id')
    message = data.get('message')
    
    if not session_id or not message:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        db = get_db()
        
        # Create/update session if doesn't exist
        if not db.session_exists(session_id):
            db.create_session(session_id, request.remote_addr, request.headers.get('User-Agent'))
        
        # Store message
        message_id = db.create_message(session_id, message)
        
        # Get or create UID
        uid_data = db.get_or_create_uid(session_id, request.remote_addr)
        
        return jsonify({
            'success': True,
            'message': 'Success',
            'data': {
                'message_id': message_id,
                'session_id': session_id,
                'uid': uid_data['uid']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@bp.route('/api/get_responses', methods=['GET'])
def get_responses():
    """Get responses for a session"""
    session_id = request.args.get('session_id')
    since = request.args.get('since')
    
    if not session_id:
        return jsonify({'success': False, 'error': 'Missing session_id'}), 400
    
    try:
        db = get_db()
        
        # Create session if doesn't exist
        if not db.session_exists(session_id):
            db.create_session(session_id, request.remote_addr, request.headers.get('User-Agent'))
        
        responses = db.get_session_responses(session_id, since)
        
        return jsonify({
            'success': True,
            'message': 'Success',
            'data': {
                'session_id': session_id,
                'responses': responses
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
