import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            from flask import current_app
            db_path = current_app.config['DATABASE_PATH']
        
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()
    
    def ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:  # Only create directory if there is one
            os.makedirs(db_dir, exist_ok=True)
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with schema"""
        conn = self.get_connection()
        try:
            # Check if tables already exist to avoid re-initialization
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='web_chat_sessions'")
            if cursor.fetchone():
                # Tables already exist, skip initialization
                return
            
            # Try to find the initialization script
            # First, try relative to the database path
            init_script_path = os.path.join(os.path.dirname(self.db_path), 'init_database.sql')
            
            # If not found, try relative to the project root (for tests)
            if not os.path.exists(init_script_path):
                # Try to find the project root by looking for the db/ directory
                current_dir = os.path.dirname(os.path.abspath(self.db_path))
                while current_dir != os.path.dirname(current_dir):  # Stop at root
                    potential_path = os.path.join(current_dir, 'db', 'init_database.sql')
                    if os.path.exists(potential_path):
                        init_script_path = potential_path
                        break
                    current_dir = os.path.dirname(current_dir)
            
            if os.path.exists(init_script_path):
                with open(init_script_path, 'r') as f:
                    init_script = f.read()
                
                # Execute the entire script as one statement
                # This ensures proper order and transaction handling
                try:
                    cursor.executescript(init_script)
                    conn.commit()
                except Exception as e:
                    print(f"Error executing init script: {e}")
                    # Fallback to basic schema
                    self.create_basic_schema(conn)
                    conn.commit()
            else:
                # If no init script, create basic tables
                self.create_basic_schema(conn)
                conn.commit()
                
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Rollback on error
            try:
                conn.rollback()
            except:
                pass
        finally:
            conn.close()
    
    def create_basic_schema(self, conn):
        """Create basic database schema if no init script exists"""
        cursor = conn.cursor()
        
        # Create web_chat_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                uid TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        # Create web_chat_messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message TEXT NOT NULL,
                message_type TEXT DEFAULT 'user',
                processed BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (session_id) REFERENCES web_chat_sessions (session_id)
            )
        """)
        
        # Create web_chat_responses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_chat_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                response_id TEXT UNIQUE NOT NULL,
                response_data TEXT NOT NULL,
                status TEXT DEFAULT 'sent',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (session_id) REFERENCES web_chat_sessions (session_id)
            )
        """)
        
        # Create system_config table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create rate_limits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                request_count INTEGER DEFAULT 1,
                window_start DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ip_address, endpoint, window_start)
            )
        """)
        
        # Create active_sessions_view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS active_sessions_view AS
            SELECT 
                s.session_id,
                s.uid,
                s.ip_address,
                s.user_agent,
                s.created_at,
                s.last_activity,
                s.is_active,
                COUNT(DISTINCT m.id) as message_count,
                COUNT(DISTINCT r.id) as response_count
            FROM web_chat_sessions s
            LEFT JOIN web_chat_messages m ON s.session_id = m.session_id
            LEFT JOIN web_chat_responses r ON s.session_id = r.session_id
            WHERE s.is_active = 1
            GROUP BY s.session_id
        """)
        
        # Insert default configuration
        cursor.execute("""
            INSERT OR IGNORE INTO system_config (config_key, config_value) VALUES 
            ('api_key', 'ObeyG1ant'),
            ('admin_key', 'FreeUkra1ne'),
            ('session_timeout', '1800'),
            ('max_message_length', '10000'),
            ('rate_limit_window', '3600')
        """)
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM web_chat_sessions WHERE session_id = ?", (session_id,))
            return cursor.fetchone() is not None
        finally:
            conn.close()
    
    def create_session(self, session_id: str, ip_address: str = None, user_agent: str = None):
        """Create new session"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # Generate UID if not exists
            uid = self.generate_uid()
            
            cursor.execute("""
                INSERT INTO web_chat_sessions (session_id, uid, ip_address, user_agent, created_at, last_activity, is_active, metadata)
                VALUES (?, ?, ?, ?, datetime('now'), datetime('now'), 1, ?)
            """, (session_id, uid, ip_address, user_agent, json.dumps({})))
            conn.commit()
            return uid
        finally:
            conn.close()
    
    def generate_uid(self) -> str:
        """Generate a unique 16-character hexadecimal UID"""
        import secrets
        return secrets.token_hex(8)
    
    def get_or_create_uid(self, session_id: str, ip_address: str = None) -> Dict[str, Any]:
        """Get existing UID or create new one"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT uid FROM web_chat_sessions WHERE session_id = ?", (session_id,))
            result = cursor.fetchone()
            
            if result:
                return {'uid': result['uid'], 'is_new': False}
            else:
                # Create new session and return new UID
                uid = self.create_session(session_id, ip_address)
                return {'uid': uid, 'is_new': True}
        finally:
            conn.close()
    
    def create_message(self, session_id: str, message: str, message_type: str = 'user') -> int:
        """Create new message"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO web_chat_messages (session_id, message, message_type, created_at, metadata)
                VALUES (?, ?, ?, datetime('now'), ?)
            """, (session_id, message, message_type, json.dumps({})))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_unprocessed_messages(self, limit: int, offset: int, since: str = None) -> List[Dict]:
        """Get unprocessed messages - IDENTICAL to PHP version"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            where_conditions = ["m.processed = 0"]
            params = []
            
            if since:
                where_conditions.append("m.created_at > ?")
                params.append(since)
            
            where_clause = " AND ".join(where_conditions)
            
            # Query IDENTICAL to PHP version
            sql = f"""
                SELECT m.id, m.session_id, m.message, m.created_at as timestamp, s.uid
                FROM web_chat_messages m
                LEFT JOIN web_chat_sessions s ON m.session_id = s.session_id
                WHERE {where_clause}
                ORDER BY m.created_at ASC
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_unprocessed_message_count(self, since: str = None) -> int:
        """Get total count of unprocessed messages - IDENTICAL to PHP"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            where_conditions = ["processed = 0"]
            params = []
            
            if since:
                where_conditions.append("created_at > ?")
                params.append(since)
            
            where_clause = " AND ".join(where_conditions)
            
            sql = f"SELECT COUNT(*) as total FROM web_chat_messages WHERE {where_clause}"
            cursor.execute(sql, params)
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def mark_messages_processed(self, message_ids: List[int]):
        """Mark messages as processed"""
        if not message_ids:
            return
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            placeholders = ','.join(['?' for _ in message_ids])
            sql = f"UPDATE web_chat_messages SET processed = 1 WHERE id IN ({placeholders})"
            cursor.execute(sql, message_ids)
            conn.commit()
        finally:
            conn.close()
    
    def create_response(self, session_id: str, response: str, message_id: int = None) -> int:
        """Create new response - IDENTICAL to PHP"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO web_chat_responses (session_id, response, message_id, timestamp)
                VALUES (?, ?, ?, datetime('now'))
            """, (session_id, response, message_id))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def create_response_with_message_id(self, session_id: str, response: str, message_id: int = None) -> int:
        """Create new response with message_id - IDENTICAL to PHP"""
        return self.create_response(session_id, response, message_id)
    

    
    def get_session_responses(self, session_id: str, since: str = None) -> List[Dict]:
        """Get responses for a session - IDENTICAL to PHP"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            where_conditions = ["session_id = ?"]
            params = [session_id]
            
            if since:
                where_conditions.append("timestamp > ?")
                params.append(since)
            
            where_clause = " AND ".join(where_conditions)
            
            sql = f"""
                SELECT id, response, timestamp, message_id
                FROM web_chat_responses
                WHERE {where_clause}
                ORDER BY timestamp ASC
            """
            
            cursor.execute(sql, params)
            responses = []
            for row in cursor.fetchall():
                responses.append({
                    'id': row['id'],
                    'response': row['response'],
                    'timestamp': row['timestamp'],
                    'message_id': row['message_id']
                })
            return responses
        finally:
            conn.close()
    
    def get_active_sessions(self, limit: int, offset: int, active: bool = True) -> List[Dict]:
        """Get active sessions with message/response counts"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Use the view for better performance
            sql = """
                SELECT * FROM active_sessions_view
                ORDER BY last_activity DESC
                LIMIT ? OFFSET ?
            """
            
            cursor.execute(sql, [limit, offset])
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_session_count(self, active: bool = True) -> int:
        """Get total session count"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if active:
                cursor.execute("SELECT COUNT(*) FROM web_chat_sessions WHERE is_active = 1")
            else:
                cursor.execute("SELECT COUNT(*) FROM web_chat_sessions")
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def cleanup_inactive_sessions(self) -> int:
        """Clean up inactive sessions"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM web_chat_sessions 
                WHERE last_activity < datetime('now', '-1800 seconds')
            """)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def get_all_config(self) -> Dict[str, str]:
        """Get all configuration values from system_config table"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT config_key, config_value FROM system_config")
            return {row['config_key']: row['config_value'] for row in cursor.fetchall()}
        finally:
            conn.close()
    
    def get_config(self, config_key: str) -> Optional[str]:
        """Get a specific configuration value"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT config_value FROM system_config WHERE config_key = ?", (config_key,))
            result = cursor.fetchone()
            return result['config_value'] if result else None
        finally:
            conn.close()
    
    def update_config(self, config_data: Dict[str, str]):
        """Update configuration values"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            for key, value in config_data.items():
                # Check if created_at column exists
                cursor.execute("PRAGMA table_info(system_config)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'created_at' in columns:
                    cursor.execute("""
                        INSERT OR REPLACE INTO system_config (config_key, config_value, created_at, updated_at)
                        VALUES (?, ?, COALESCE((SELECT created_at FROM system_config WHERE config_key = ?), datetime('now')), datetime('now'))
                    """, (key, value, key))
                else:
                    # Fallback for older schema without created_at
                    cursor.execute("""
                        INSERT OR REPLACE INTO system_config (config_key, config_value, updated_at)
                        VALUES (?, ?, datetime('now'))
                    """, (key, value))
            conn.commit()
        finally:
            conn.close()
    
    def update_session_activity(self, session_id: str):
        """Update the last_activity timestamp for a session"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE web_chat_sessions 
                SET last_activity = datetime('now')
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()
        finally:
            conn.close()
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (alias for cleanup_inactive_sessions)"""
        return self.cleanup_inactive_sessions()
