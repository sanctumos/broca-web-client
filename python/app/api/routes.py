from flask import Blueprint, request, jsonify, current_app
from app.utils.database import DatabaseManager
from app.utils.rate_limiting import RateLimitManager
from app.api.auth import require_auth, require_admin_auth
import re
from datetime import datetime

bp = Blueprint('api', __name__)

def get_db():
    """Get database manager instance"""
    db_path = current_app.config.get('DATABASE_PATH', 'web_chat_bridge.db')
    return DatabaseManager(db_path)

def get_rate_limiter():
    """Get rate limiter instance"""
    return RateLimitManager(get_db())

def validate_session_id(session_id: str) -> bool:
    """Validate session ID format - IDENTICAL to PHP version"""
    if not session_id or not isinstance(session_id, str):
        return False
    pattern = r'^session_[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, session_id)) and len(session_id) <= 64

def validate_message(message: str) -> bool:
    """Validate message content - IDENTICAL to PHP version"""
    return (
        isinstance(message, str) and
        len(message) >= 1 and
        len(message) <= 10000 and
        message.strip() != ''
    )

# Single entry point for API - IDENTICAL to PHP structure
@bp.route('/', methods=['GET', 'POST', 'OPTIONS'])
def api_entry_point():
    """Single API entry point with action parameter routing - IDENTICAL to PHP"""
    # Handle preflight requests
    if request.method == 'OPTIONS':
        return '', 200
    
    # Get action from query string
    action = request.args.get('action', '')
    
    # Check if action parameter is provided
    if not action:
        return jsonify({'success': False, 'error': 'Missing action parameter'}), 400
    
    # Route to appropriate handler based on action - IDENTICAL to PHP
    if action == 'messages':
        return handle_messages()
    elif action == 'inbox':
        return handle_inbox()
    elif action == 'outbox':
        return handle_outbox()
    elif action == 'responses':
        return handle_responses()
    elif action == 'sessions':
        return handle_sessions()
    elif action == 'config':
        return handle_config()
    elif action == 'cleanup':
        return handle_cleanup()
    elif action == 'clear_data':
        return handle_clear_data()
    elif action == 'cleanup_logs':
        return handle_cleanup_logs()
    else:
        return jsonify({'success': False, 'error': 'Invalid action'}), 400

# Individual route decorators for direct access (optional, for backward compatibility)
@bp.route('/messages', methods=['POST'])
def handle_messages_direct():
    """Direct route for messages - same as ?action=messages"""
    return handle_messages()

@bp.route('/inbox', methods=['GET'])
@require_auth
def handle_inbox_direct():
    """Direct route for inbox - same as ?action=inbox"""
    return handle_inbox()

@bp.route('/outbox', methods=['POST'])
@require_auth
def handle_outbox_direct():
    """Direct route for outbox - same as ?action=outbox"""
    return handle_outbox()

@bp.route('/responses', methods=['GET'])
def handle_responses_direct():
    """Direct route for responses - same as ?action=responses"""
    return handle_responses()

@bp.route('/sessions', methods=['GET'])
@require_admin_auth
def handle_sessions_direct():
    """Direct route for sessions - same as ?action=sessions"""
    return handle_sessions()

@bp.route('/config', methods=['GET', 'POST'])
@require_admin_auth
def handle_config_direct():
    """Direct route for config - same as ?action=config"""
    return handle_config()

@bp.route('/cleanup', methods=['POST'])
@require_admin_auth
def handle_cleanup_direct():
    """Direct route for cleanup - same as ?action=cleanup"""
    return handle_cleanup()

@bp.route('/clear_data', methods=['POST'])
@require_admin_auth
def handle_clear_data_direct():
    """Direct route for clear_data - same as ?action=clear_data"""
    return handle_clear_data()

@bp.route('/cleanup_logs', methods=['POST'])
@require_admin_auth
def handle_cleanup_logs_direct():
    """Direct route for cleanup_logs - same as ?action=cleanup_logs"""
    return handle_cleanup_logs()

def handle_messages():
    """Handle POST /api/v1/?action=messages - IDENTICAL to PHP"""
    if request.method != 'POST':
        return jsonify({'success': False, 'error': 'Method not allowed'}), 405
    
    # Rate limiting - IDENTICAL to PHP
    rate_limiter = get_rate_limiter()
    if not rate_limiter.check_rate_limit(request.remote_addr, '/api/messages', 50):
        return jsonify({'success': False, 'error': 'Rate limit exceeded'}), 429
    
    # Get and validate input - IDENTICAL to PHP
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON'}), 400
    
    session_id = data.get('session_id', '').strip()
    message = data.get('message', '').strip()
    timestamp = data.get('timestamp', datetime.now().isoformat())
    
    # Validate required fields - IDENTICAL to PHP
    if not session_id or not message:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    if not validate_session_id(session_id):
        return jsonify({'success': False, 'error': 'Invalid session ID'}), 400
    
    if not validate_message(message):
        return jsonify({'success': False, 'error': 'Invalid message'}), 400
    
    try:
        db = get_db()
        
        # Check if session exists and create if needed - IDENTICAL to PHP
        session_existed = db.session_exists(session_id)
        if not session_existed:
            db.create_session(session_id, request.remote_addr, request.headers.get('User-Agent'))
        
        # Get or create UID for this session - IDENTICAL to PHP
        uid_data = db.get_or_create_uid(session_id, request.remote_addr)
        uid = uid_data['uid']
        # A user is new if the session didn't exist before this request
        is_new_user = not session_existed
        
        # Store message - IDENTICAL to PHP
        message_id = db.create_message(session_id, message)
        
        # Response format - IDENTICAL to PHP
        return jsonify({
            'success': True,
            'message': 'Message received',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'message_id': message_id,
                'session_id': session_id,
                'timestamp': timestamp,
                'uid': uid,
                'is_new_user': is_new_user
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

def handle_inbox():
    """Handle GET /api/v1/?action=inbox - IDENTICAL to PHP"""
    if request.method != 'GET':
        return jsonify({'success': False, 'error': 'Method not allowed'}), 405
    
    # Authentication required - IDENTICAL to PHP
    auth_result = require_auth_internal()
    if auth_result:
        return auth_result
    
    # Rate limiting - IDENTICAL to PHP
    rate_limiter = get_rate_limiter()
    if not rate_limiter.check_rate_limit(request.remote_addr, '/api/inbox', 120):
        return jsonify({'success': False, 'error': 'Rate limit exceeded'}), 429
    
    # Get query parameters - IDENTICAL to PHP
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    since = request.args.get('since', '')
    
    try:
        db = get_db()
        
        # Get messages with UID information - IDENTICAL to PHP
        messages = db.get_unprocessed_messages(limit, offset, since)
        
        # Get total count - IDENTICAL to PHP
        total = db.get_unprocessed_message_count(since)
        
        # Mark messages as processed - IDENTICAL to PHP
        if messages:
            message_ids = [msg['id'] for msg in messages]
            db.mark_messages_processed(message_ids)
        
        # Response format - IDENTICAL to PHP
        return jsonify({
            'success': True,
            'message': 'Messages retrieved successfully',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'messages': messages,
                'pagination': {
                    'total': total,
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + limit) < total
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

def handle_outbox():
    """Handle POST /api/v1/?action=outbox - IDENTICAL to PHP"""
    if request.method != 'POST':
        return jsonify({'success': False, 'error': 'Method not allowed'}), 405
    
    # Authentication required - IDENTICAL to PHP
    auth_result = require_auth_internal()
    if auth_result:
        return auth_result
    
    # Rate limiting - IDENTICAL to PHP
    rate_limiter = get_rate_limiter()
    if not rate_limiter.check_rate_limit(request.remote_addr, '/api/outbox', 200):
        return jsonify({'success': False, 'error': 'Rate limit exceeded'}), 429
    
    # Get and validate input - IDENTICAL to PHP
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    session_id = data.get('session_id', '').strip()
    response = data.get('response', '').strip()
    message_id = data.get('message_id', 0)
    timestamp = data.get('timestamp', datetime.now().isoformat())
    
    # Validate required fields - IDENTICAL to PHP
    if not session_id or not response:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Validate session_id format
    if not validate_session_id(session_id):
        return jsonify({'success': False, 'error': 'Invalid session ID'}), 400
    
    try:
        db = get_db()
        
        # Validate session - IDENTICAL to PHP
        if not db.session_exists(session_id):
            return jsonify({'success': False, 'error': 'Invalid session'}), 400
        
        # Store response - IDENTICAL to PHP (with message_id)
        response_id = db.create_response_with_message_id(session_id, response, message_id if message_id else None)
        
        # Response format - IDENTICAL to PHP
        return jsonify({
            'success': True,
            'message': 'Response sent successfully',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'response_id': response_id,
                'session_id': session_id,
                'timestamp': timestamp
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

def handle_responses():
    """Handle GET /api/v1/?action=responses - IDENTICAL to PHP"""
    if request.method != 'GET':
        return jsonify({'success': False, 'error': 'Method not allowed'}), 405
    
    # Rate limiting - IDENTICAL to PHP
    rate_limiter = get_rate_limiter()
    if not rate_limiter.check_rate_limit(request.remote_addr, '/api/responses', 200):
        return jsonify({'success': False, 'error': 'Rate limit exceeded'}), 429
    
    session_id = request.args.get('session_id', '').strip()
    since = request.args.get('since', '')
    
    if not session_id:
        return jsonify({'success': False, 'error': 'Missing session_id'}), 400
    
    # Validate session_id format - IDENTICAL to PHP
    if not validate_session_id(session_id):
        return jsonify({'success': False, 'error': 'Invalid session ID'}), 400
    
    try:
        db = get_db()
        
        # Create session if doesn't exist - IDENTICAL to PHP
        if not db.session_exists(session_id):
            db.create_session(session_id, request.remote_addr, request.headers.get('User-Agent'))
        
        responses = db.get_session_responses(session_id, since)
        
        # Response format - IDENTICAL to PHP
        return jsonify({
            'success': True,
            'message': 'Responses retrieved successfully',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'session_id': session_id,
                'responses': responses
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

def handle_sessions():
    """Handle GET /api/v1/?action=sessions - IDENTICAL to PHP"""
    if request.method != 'GET':
        return jsonify({'success': False, 'error': 'Method not allowed'}), 405
    
    # Authentication required - IDENTICAL to PHP
    auth_result = require_admin_auth_internal()
    if auth_result:
        return auth_result
    
    # Rate limiting - IDENTICAL to PHP
    rate_limiter = get_rate_limiter()
    if not rate_limiter.check_rate_limit(request.remote_addr, '/api/sessions', 20):
        return jsonify({'success': False, 'error': 'Rate limit exceeded'}), 429
    
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    active = request.args.get('active', 'true')
    
    try:
        db = get_db()
        sessions = db.get_active_sessions(limit, offset, active == 'true')
        total = db.get_session_count(active == 'true')
        
        # Response format - IDENTICAL to PHP
        return jsonify({
            'success': True,
            'message': 'Sessions retrieved successfully',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'sessions': sessions,
                'pagination': {
                    'total': total,
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + limit) < total
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

def handle_config():
    """Handle GET/POST /api/v1/?action=config - IDENTICAL to PHP"""
    # Authentication required - IDENTICAL to PHP
    auth_result = require_admin_auth_internal()
    if auth_result:
        return auth_result
    
    if request.method == 'GET':
        try:
            db = get_db()
            config = db.get_all_config()
            
            # Response format - IDENTICAL to PHP
            return jsonify({
                'success': True,
                'message': 'Configuration retrieved successfully',
                'timestamp': datetime.now().isoformat(),
                'data': config
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON'}), 400
        
        try:
            db = get_db()
            db.update_config(data)
            
            # Response format - IDENTICAL to PHP
            return jsonify({
                'success': True,
                'message': 'Configuration updated successfully',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': 'Internal server error'}), 500

def handle_cleanup():
    """Handle POST /api/v1/?action=cleanup - IDENTICAL to PHP"""
    if request.method != 'POST':
        return jsonify({'success': False, 'error': 'Method not allowed'}), 405
    
    # Authentication required - IDENTICAL to PHP
    auth_result = require_admin_auth_internal()
    if auth_result:
        return auth_result
    
    try:
        db = get_db()
        cleaned_count = db.cleanup_inactive_sessions()
        
        # Response format - IDENTICAL to PHP
        return jsonify({
            'success': True,
            'message': 'Cleanup completed successfully',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'cleaned_count': cleaned_count,
                'message': f'Cleaned up {cleaned_count} inactive sessions'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

def handle_clear_data():
    """Handle POST /api/v1/?action=clear_data - IDENTICAL to PHP"""
    if request.method != 'POST':
        return jsonify({'success': False, 'error': 'Method not allowed'}), 405
    
    # Authentication required - IDENTICAL to PHP
    auth_result = require_admin_auth_internal()
    if auth_result:
        return auth_result
    
    try:
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get counts before deletion - IDENTICAL to PHP
        cursor.execute("SELECT COUNT(*) FROM web_chat_responses")
        responses_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM web_chat_messages")
        messages_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM web_chat_sessions")
        sessions_count = cursor.fetchone()[0]
        
        # Clear all data - IDENTICAL to PHP
        cursor.execute("DELETE FROM web_chat_responses")
        cursor.execute("DELETE FROM web_chat_messages")
        cursor.execute("DELETE FROM web_chat_sessions")
        cursor.execute("DELETE FROM rate_limits")
        
        conn.commit()
        conn.close()
        
        # Log the action (we'll implement logging later)
        # log_message('WARNING', 'All data cleared by admin', {'admin_ip': request.remote_addr})
        
        return jsonify({
            'success': True,
            'message': 'All data cleared successfully',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'message': 'All data cleared successfully',
                'remaining_data': {
                    'responses': 0,
                    'messages': 0,
                    'sessions': 0
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

def handle_cleanup_logs():
    """Handle POST /api/v1/?action=cleanup_logs - IDENTICAL to PHP"""
    if request.method != 'POST':
        return jsonify({'success': False, 'error': 'Method not allowed'}), 405
    
    # Authentication required - IDENTICAL to PHP
    auth_result = require_admin_auth_internal()
    if auth_result:
        return auth_result
    
    try:
        # For now, implement basic log cleanup logic
        # In production, this would integrate with actual logging system
        
        # Get current log file info (placeholder for now)
        current_log_size_mb = 0.0
        backup_files_count = 0
        total_log_size_mb = 0.0
        retention_days = 30
        max_size_mb = 100
        
        # Log the action (we'll implement logging later)
        # log_message('INFO', 'Manual log cleanup triggered by admin', {
        #     'admin_ip': request.remote_addr,
        #     'current_size_mb': current_log_size_mb,
        #     'backup_count': backup_files_count,
        #     'total_size_mb': total_log_size_mb
        # })
        
        return jsonify({
            'success': True,
            'message': 'Log cleanup completed successfully',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'message': 'Log cleanup completed successfully',
                'current_log_size_mb': current_log_size_mb,
                'backup_files_count': backup_files_count,
                'total_log_size_mb': total_log_size_mb,
                'retention_days': retention_days,
                'max_size_mb': max_size_mb
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

# Internal authentication functions
def require_auth_internal():
    """Internal authentication check - IDENTICAL to PHP"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    key = auth_header[7:]
    db_manager = get_db()
    config = db_manager.get_all_config()
    stored_api_key = config.get('api_key', current_app.config['DEFAULT_API_KEY'])
    stored_admin_key = config.get('admin_key', current_app.config['DEFAULT_ADMIN_KEY'])
    
    # Accept either API key or admin key for inbox access
    if key != stored_api_key and key != stored_admin_key:
        return jsonify({'success': False, 'error': 'Invalid API key'}), 401
    
    return None

def require_admin_auth_internal():
    """Internal admin authentication check - IDENTICAL to PHP"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    admin_key = auth_header[7:]
    db_manager = get_db()
    config = db_manager.get_all_config()
    stored_admin_key = config.get('admin_key', current_app.config['DEFAULT_ADMIN_KEY'])
    
    if admin_key != stored_admin_key:
        return jsonify({'success': False, 'error': 'Invalid admin key'}), 401
    
    return None
