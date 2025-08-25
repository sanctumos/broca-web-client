import sqlite3
import os

def init_database():
    """Initialize the database with schema"""
    db_path = 'db/web_chat_bridge.db'
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to database (this will create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(64) UNIQUE NOT NULL,
                uid VARCHAR(16) UNIQUE NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at DATETIME NOT NULL,
                last_activity DATETIME NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(64) NOT NULL,
                message TEXT NOT NULL,
                message_type VARCHAR(20) DEFAULT 'user',
                processed BOOLEAN DEFAULT 0,
                created_at DATETIME NOT NULL,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (session_id) REFERENCES web_chat_sessions(session_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_chat_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(64) NOT NULL,
                response_id VARCHAR(32) UNIQUE NOT NULL,
                response_data TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (session_id) REFERENCES web_chat_sessions(session_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address VARCHAR(45) NOT NULL,
                endpoint VARCHAR(100) NOT NULL,
                request_count INTEGER DEFAULT 1,
                window_start DATETIME NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                UNIQUE(ip_address, endpoint, window_start)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key VARCHAR(100) UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                description TEXT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)
        
        # Create view for active sessions
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS active_sessions_view AS
            SELECT 
                s.*,
                COUNT(m.id) as message_count,
                COUNT(r.id) as response_count
            FROM web_chat_sessions s
            LEFT JOIN web_chat_messages m ON s.session_id = m.session_id
            LEFT JOIN web_chat_responses r ON s.session_id = r.session_id
            WHERE s.is_active = 1
            GROUP BY s.id
        """)
        
        # Insert default configuration
        cursor.execute("""
            INSERT OR IGNORE INTO system_config (config_key, config_value, description, created_at, updated_at) VALUES
            ('api_key', 'ObeyG1ant', 'API key for external integrations', datetime('now'), datetime('now')),
            ('admin_key', 'FreeUkra1ne', 'Admin authentication key', datetime('now'), datetime('now')),
            ('rate_limit_window', '3600', 'Rate limiting window in seconds', datetime('now'), datetime('now')),
            ('rate_limit_max_requests', '1000', 'Maximum requests per window per IP', datetime('now'), datetime('now'))
        """)
        
        conn.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
