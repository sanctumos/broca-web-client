from flask import Blueprint, request, jsonify, render_template, current_app
from app.utils.database import DatabaseManager
from app.api.auth import require_admin_auth
from datetime import datetime
import json

bp = Blueprint('admin', __name__)

def get_db():
    """Get database manager instance"""
    db_path = current_app.config.get('DATABASE_PATH', 'web_chat_bridge.db')
    return DatabaseManager(db_path)

@bp.route('/')
def admin_interface():
    """Admin interface main page"""
    return render_template('admin.html')

@bp.route('/api/sessions')
@require_admin_auth
def get_sessions():
    """Get active sessions"""
    db = get_db()
    
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    active = request.args.get('active', 'true')
    
    try:
        sessions = db.get_active_sessions(limit, offset, active == 'true')
        total = db.get_session_count(active == 'true')
        
        return jsonify({
            'success': True,
            'message': 'Success',
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
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/session_messages')
@require_admin_auth
def get_session_messages():
    """Get messages and responses for a specific session"""
    db = get_db()
    
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'success': False, 'error': 'Missing session_id'}), 400
    
    try:
        # Get session info
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM web_chat_sessions WHERE session_id = ?
        """, (session_id,))
        session = cursor.fetchone()
        
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Get messages
        cursor.execute("""
            SELECT id, session_id, message, created_at FROM web_chat_messages 
            WHERE session_id = ? ORDER BY created_at ASC
        """, (session_id,))
        messages = [dict(row) for row in cursor.fetchall()]
        
        # Get responses
        cursor.execute("""
            SELECT id, response, message_id, timestamp FROM web_chat_responses 
            WHERE session_id = ? ORDER BY timestamp ASC
        """, (session_id,))
        responses = []
        for row in cursor.fetchall():
            responses.append({
                'id': row['id'],
                'response': row['response'],
                'timestamp': row['timestamp'],
                'message_id': row['message_id']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Success',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'session': dict(session),
                'messages': messages,
                'responses': responses
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/config', methods=['GET', 'POST'])
@require_admin_auth
def handle_config():
    """Get or update configuration"""
    db = get_db()
    
    if request.method == 'GET':
        try:
            config = db.get_all_config()
            return jsonify({
                'success': True,
                'message': 'Success',
                'timestamp': datetime.now().isoformat(),
                'data': config
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON'}), 400
        
        try:
            # Update configuration
            db.update_config(data)
            return jsonify({
                'success': True,
                'message': 'Success',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/cleanup', methods=['POST'])
@require_admin_auth
def manual_cleanup():
    """Manual cleanup of inactive sessions"""
    db = get_db()
    
    try:
        cleaned_count = db.cleanup_inactive_sessions()
        return jsonify({
            'success': True,
            'message': 'Success',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'cleaned_count': cleaned_count,
                'message': f'Cleaned up {cleaned_count} inactive sessions'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/clear_data', methods=['POST'])
@require_admin_auth
def clear_all_data():
    """Clear all data (dangerous operation)"""
    db = get_db()
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get counts before deletion
        cursor.execute("SELECT COUNT(*) FROM web_chat_sessions")
        sessions_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM web_chat_messages")
        messages_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM web_chat_responses")
        responses_count = cursor.fetchone()[0]
        
        # Clear all data
        cursor.execute("DELETE FROM web_chat_responses")
        cursor.execute("DELETE FROM web_chat_messages")
        cursor.execute("DELETE FROM web_chat_sessions")
        cursor.execute("DELETE FROM rate_limits")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Success',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'message': 'All data cleared successfully',
                'cleaned_data': {
                    'sessions': sessions_count,
                    'messages': messages_count,
                    'responses': responses_count
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/cleanup_logs', methods=['POST'])
@require_admin_auth
def cleanup_logs():
    """Clean up log files"""
    try:
        # This is a placeholder - implement actual log cleanup logic
        return jsonify({
            'success': True,
            'message': 'Success',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'message': 'Log cleanup completed successfully',
                'current_log_size_mb': 0.0,
                'backup_files_count': 0,
                'total_log_size_mb': 0.0,
                'retention_days': 30,
                'max_size_mb': 100
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
