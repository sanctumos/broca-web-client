# Database Schema and Migration Guide - Flask Port

## Overview

This document provides the complete database schema, initialization scripts, and migration procedures for the Flask port of the Web Chat Bridge system. The database must maintain 100% compatibility with the existing PHP system.

## Database Technology

- **Database Engine:** SQLite 3
- **File Format:** `.db` file
- **Location:** `db/web_chat_bridge.db` (relative to project root)
- **Permissions:** Read/write for application user
- **Backup Strategy:** File-based backup with versioning

## Complete Database Schema

### 1. Core Tables

#### `web_chat_sessions`
```sql
CREATE TABLE web_chat_sessions (
    id VARCHAR(64) PRIMARY KEY,
    uid VARCHAR(16),
    created_at TEXT,
    last_active TEXT,
    ip_address VARCHAR(45),
    metadata TEXT
);
```

**Field Descriptions:**
- `id`: Unique session identifier, format: `session_{timestamp}_{random_string}`
- `uid`: 16-character hexadecimal user identifier, persistent across sessions
- `created_at`: Session creation timestamp in SQLite datetime format
- `last_active`: Last activity timestamp in SQLite datetime format
- `ip_address`: Client IP address (supports IPv4 and IPv6)
- `metadata`: JSON string for additional session data

**Indexes:**
```sql
CREATE INDEX idx_sessions_last_active ON web_chat_sessions(last_active);
CREATE INDEX idx_sessions_uid ON web_chat_sessions(uid);
CREATE INDEX idx_sessions_ip ON web_chat_sessions(ip_address);
```

#### `web_chat_messages`
```sql
CREATE TABLE web_chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(64),
    message TEXT,
    timestamp TEXT,
    processed INTEGER DEFAULT 0,
    broca_message_id INTEGER
);
```

**Field Descriptions:**
- `id`: Auto-incrementing primary key
- `session_id`: Foreign key to web_chat_sessions.id
- `message`: User message content (max 10KB)
- `timestamp`: Message timestamp in ISO format
- `processed`: Processing status (0=unprocessed, 1=processed)
- `broca_message_id`: Optional link to Broca2 message ID

**Indexes:**
```sql
CREATE INDEX idx_messages_session_id ON web_chat_messages(session_id);
CREATE INDEX idx_messages_processed ON web_chat_messages(processed);
CREATE INDEX idx_messages_timestamp ON web_chat_messages(timestamp);
CREATE INDEX idx_messages_broca_id ON web_chat_messages(broca_message_id);
```

#### `web_chat_responses`
```sql
CREATE TABLE web_chat_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(64),
    response TEXT,
    timestamp TEXT,
    message_id INTEGER
);
```

**Field Descriptions:**
- `id`: Auto-incrementing primary key
- `session_id`: Foreign key to web_chat_sessions.id
- `response`: Agent response content (max 10KB)
- `timestamp`: Response timestamp in ISO format
- `message_id`: Optional link to specific message being responded to

**Indexes:**
```sql
CREATE INDEX idx_responses_session_id ON web_chat_responses(session_id);
CREATE INDEX idx_responses_timestamp ON web_chat_responses(timestamp);
CREATE INDEX idx_responses_message_id ON web_chat_responses(message_id);
```

#### `rate_limits`
```sql
CREATE TABLE rate_limits (
    ip_address VARCHAR(45),
    endpoint VARCHAR(50),
    count INTEGER,
    window_start TEXT
);
```

**Field Descriptions:**
- `ip_address`: Client IP address
- `endpoint`: API endpoint being rate limited
- `count`: Request count in current window
- `window_start`: Window start timestamp

**Indexes:**
```sql
CREATE INDEX idx_rate_limits_ip_endpoint ON rate_limits(ip_address, endpoint);
CREATE INDEX idx_rate_limits_window ON rate_limits(window_start);
```

### 2. Foreign Key Constraints

```sql
-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Add foreign key constraints
ALTER TABLE web_chat_messages 
ADD CONSTRAINT fk_messages_session 
FOREIGN KEY (session_id) REFERENCES web_chat_sessions(id) ON DELETE CASCADE;

ALTER TABLE web_chat_responses 
ADD CONSTRAINT fk_responses_session 
FOREIGN KEY (session_id) REFERENCES web_chat_sessions(id) ON DELETE CASCADE;

ALTER TABLE web_chat_responses 
ADD CONSTRAINT fk_responses_message 
FOREIGN KEY (message_id) REFERENCES web_chat_messages(id) ON DELETE SET NULL;
```

## Database Initialization Script

### Complete SQL Script (`init_database.sql`)

```sql
-- Web Chat Bridge Database Initialization Script
-- Flask Port - Must maintain 100% compatibility with PHP version

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Create web_chat_sessions table
CREATE TABLE IF NOT EXISTS web_chat_sessions (
    id VARCHAR(64) PRIMARY KEY,
    uid VARCHAR(16),
    created_at TEXT,
    last_active TEXT,
    ip_address VARCHAR(45),
    metadata TEXT
);

-- Create web_chat_messages table
CREATE TABLE IF NOT EXISTS web_chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(64),
    message TEXT,
    timestamp TEXT,
    processed INTEGER DEFAULT 0,
    broca_message_id INTEGER
);

-- Create web_chat_responses table
CREATE TABLE IF NOT EXISTS web_chat_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(64),
    response TEXT,
    timestamp TEXT,
    message_id INTEGER
);

-- Create rate_limits table
CREATE TABLE IF NOT EXISTS rate_limits (
    ip_address VARCHAR(45),
    endpoint VARCHAR(50),
    count INTEGER,
    window_start TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_last_active ON web_chat_sessions(last_active);
CREATE INDEX IF NOT EXISTS idx_sessions_uid ON web_chat_sessions(uid);
CREATE INDEX IF NOT EXISTS idx_sessions_ip ON web_chat_sessions(ip_address);

CREATE INDEX IF NOT EXISTS idx_messages_session_id ON web_chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_processed ON web_chat_messages(processed);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON web_chat_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_broca_id ON web_chat_messages(broca_message_id);

CREATE INDEX IF NOT EXISTS idx_responses_session_id ON web_chat_responses(session_id);
CREATE INDEX IF NOT EXISTS idx_responses_timestamp ON web_chat_responses(timestamp);
CREATE INDEX IF NOT EXISTS idx_responses_message_id ON web_chat_responses(message_id);

CREATE INDEX IF NOT EXISTS idx_rate_limits_ip_endpoint ON rate_limits(ip_address, endpoint);
CREATE INDEX IF NOT EXISTS idx_rate_limits_window ON rate_limits(window_start);

-- Insert sample data for testing (optional)
INSERT OR IGNORE INTO web_chat_sessions (id, uid, created_at, last_active, ip_address, metadata) 
VALUES (
    'session_test_123',
    'a1b2c3d4e5f6g7h8',
    datetime('now', '-1 hour'),
    datetime('now'),
    '127.0.0.1',
    '{"test": true}'
);

-- Verify table creation
SELECT name FROM sqlite_master WHERE type='table';
```

## Python Database Connection

### Database Connection Class (`database.py`)

```python
import sqlite3
import os
from typing import Optional, Dict, List, Any
from contextlib import contextmanager
import logging

class DatabaseManager:
    def __init__(self, db_path: str = "db/web_chat_bridge.db"):
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()
    
    def ensure_db_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a new database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database operations"""
        conn = self.get_connection()
        try:
            yield conn.cursor()
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with required tables"""
        init_script = os.path.join(os.path.dirname(__file__), 'init_database.sql')
        
        if os.path.exists(init_script):
            with open(init_script, 'r') as f:
                sql_script = f.read()
            
            with self.get_cursor() as cursor:
                cursor.executescript(sql_script)
        else:
            # Fallback: create tables programmatically
            self.create_tables()
    
    def create_tables(self):
        """Create database tables programmatically"""
        with self.get_cursor() as cursor:
            # Create web_chat_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS web_chat_sessions (
                    id VARCHAR(64) PRIMARY KEY,
                    uid VARCHAR(16),
                    created_at TEXT,
                    last_active TEXT,
                    ip_address VARCHAR(45),
                    metadata TEXT
                )
            """)
            
            # Create web_chat_messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS web_chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id VARCHAR(64),
                    message TEXT,
                    timestamp TEXT,
                    processed INTEGER DEFAULT 0,
                    broca_message_id INTEGER
                )
            """)
            
            # Create web_chat_responses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS web_chat_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id VARCHAR(64),
                    response TEXT,
                    timestamp TEXT,
                    message_id INTEGER
                )
            """)
            
            # Create rate_limits table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    ip_address VARCHAR(45),
                    endpoint VARCHAR(50),
                    count INTEGER,
                    window_start TEXT
                )
            """)
            
            # Create indexes
            self.create_indexes(cursor)
    
    def create_indexes(self, cursor):
        """Create database indexes for performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_sessions_last_active ON web_chat_sessions(last_active)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_uid ON web_chat_sessions(uid)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_ip ON web_chat_sessions(ip_address)",
            "CREATE INDEX IF NOT EXISTS idx_messages_session_id ON web_chat_messages(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_processed ON web_chat_messages(processed)",
            "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON web_chat_messages(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_messages_broca_id ON web_chat_messages(broca_message_id)",
            "CREATE INDEX IF NOT EXISTS idx_responses_session_id ON web_chat_responses(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_responses_timestamp ON web_chat_responses(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_responses_message_id ON web_chat_responses(message_id)",
            "CREATE INDEX IF NOT EXISTS idx_rate_limits_ip_endpoint ON rate_limits(ip_address, endpoint)",
            "CREATE INDEX IF NOT EXISTS idx_rate_limits_window ON rate_limits(window_start)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def execute_query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_single(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a query and return single result as dictionary"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def execute_insert(self, sql: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the last insert ID"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.lastrowid
    
    def execute_update(self, sql: str, params: tuple = ()) -> int:
        """Execute an UPDATE query and return the number of affected rows"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount
    
    def execute_delete(self, sql: str, params: tuple = ()) -> int:
        """Execute a DELETE query and return the number of affected rows"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount
```

## Database Operations

### Session Management

```python
class SessionManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_session(self, session_id: str, ip_address: str = None, metadata: dict = None) -> bool:
        """Create a new session"""
        try:
            sql = """
                INSERT INTO web_chat_sessions (id, created_at, last_active, ip_address, metadata)
                VALUES (?, datetime('now'), datetime('now'), ?, ?)
            """
            metadata_json = json.dumps(metadata) if metadata else None
            self.db.execute_insert(sql, (session_id, ip_address, metadata_json))
            return True
        except Exception as e:
            logging.error(f"Failed to create session {session_id}: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        sql = "SELECT * FROM web_chat_sessions WHERE id = ?"
        return self.db.execute_single(sql, (session_id,))
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update session last_active timestamp"""
        try:
            sql = "UPDATE web_chat_sessions SET last_active = datetime('now') WHERE id = ?"
            self.db.execute_update(sql, (session_id,))
            return True
        except Exception as e:
            logging.error(f"Failed to update session activity {session_id}: {e}")
            return False
    
    def get_active_sessions(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get active sessions with message/response counts"""
        sql = """
            SELECT 
                s.id,
                s.uid,
                s.created_at,
                s.last_active,
                s.ip_address,
                s.metadata,
                COUNT(DISTINCT m.id) as message_count,
                COUNT(DISTINCT r.id) as response_count
            FROM web_chat_sessions s
            LEFT JOIN web_chat_messages m ON s.id = m.session_id
            LEFT JOIN web_chat_responses r ON s.id = r.session_id
            WHERE s.last_active > datetime('now', '-1800 seconds')
            GROUP BY s.id
            ORDER BY s.last_active DESC
            LIMIT ? OFFSET ?
        """
        return self.db.execute_query(sql, (limit, offset))
    
    def cleanup_inactive_sessions(self) -> int:
        """Remove sessions inactive for more than 30 minutes"""
        try:
            sql = """
                DELETE FROM web_chat_sessions 
                WHERE last_active < datetime('now', '-1800 seconds')
            """
            return self.db.execute_delete(sql)
        except Exception as e:
            logging.error(f"Failed to cleanup inactive sessions: {e}")
            return 0
```

### Message Management

```python
class MessageManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_message(self, session_id: str, message: str, timestamp: str = None) -> int:
        """Create a new message"""
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        
        sql = """
            INSERT INTO web_chat_messages (session_id, message, timestamp)
            VALUES (?, ?, ?)
        """
        return self.db.execute_insert(sql, (session_id, message, timestamp))
    
    def get_unprocessed_messages(self, limit: int = 50, offset: int = 0, since: str = None) -> List[Dict[str, Any]]:
        """Get unprocessed messages for plugin processing"""
        where_conditions = ["processed = 0"]
        params = []
        
        if since:
            where_conditions.append("timestamp > ?")
            params.append(since)
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
            SELECT m.id, m.session_id, m.message, m.timestamp, s.uid
            FROM web_chat_messages m
            LEFT JOIN web_chat_sessions s ON m.session_id = s.id
            WHERE {where_clause}
            ORDER BY m.timestamp ASC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        return self.db.execute_query(sql, tuple(params))
    
    def mark_messages_processed(self, message_ids: List[int]) -> bool:
        """Mark messages as processed"""
        if not message_ids:
            return True
        
        try:
            placeholders = ','.join(['?' for _ in message_ids])
            sql = f"UPDATE web_chat_messages SET processed = 1 WHERE id IN ({placeholders})"
            self.db.execute_update(sql, tuple(message_ids))
            return True
        except Exception as e:
            logging.error(f"Failed to mark messages as processed: {e}")
            return False
    
    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a session"""
        sql = """
            SELECT id, session_id, message, timestamp
            FROM web_chat_messages 
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """
        return self.db.execute_query(sql, (session_id,))
```

### Response Management

```python
class ResponseManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_response(self, session_id: str, response: str, message_id: int = None, timestamp: str = None) -> int:
        """Create a new response"""
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        
        sql = """
            INSERT INTO web_chat_responses (session_id, response, message_id, timestamp)
            VALUES (?, ?, ?, ?)
        """
        return self.db.execute_insert(sql, (session_id, response, message_id, timestamp))
    
    def get_session_responses(self, session_id: str, since: str = None) -> List[Dict[str, Any]]:
        """Get responses for a session"""
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
        
        return self.db.execute_query(sql, tuple(params))
```

### Rate Limiting

```python
class RateLimitManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def check_rate_limit(self, ip_address: str, endpoint: str, limit: int) -> bool:
        """Check if request is within rate limit"""
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(hours=1)
        
        # Clean up old entries
        self.cleanup_old_rate_limits(window_start)
        
        # Check current count
        sql = """
            SELECT COUNT(*) as count
            FROM rate_limits
            WHERE ip_address = ? AND endpoint = ? AND window_start >= ?
        """
        result = self.db.execute_single(sql, (ip_address, endpoint, window_start.isoformat()))
        current_count = result['count'] if result else 0
        
        if current_count >= limit:
            return False
        
        # Add current request
        sql = """
            INSERT OR REPLACE INTO rate_limits (ip_address, endpoint, count, window_start)
            VALUES (?, ?, ?, ?)
        """
        self.db.execute_insert(sql, (ip_address, endpoint, current_count + 1, current_time.isoformat()))
        
        return True
    
    def cleanup_old_rate_limits(self, cutoff_time: datetime):
        """Remove old rate limit entries"""
        sql = "DELETE FROM rate_limits WHERE window_start < ?"
        self.db.execute_delete(sql, (cutoff_time.isoformat(),))
```

## Data Migration

### From PHP to Flask

#### 1. Export PHP Data
```bash
# Create SQLite dump from PHP system (now located in php/ folder)
sqlite3 php/db/web_chat.db ".dump" > php_export.sql

# Or export specific tables
sqlite3 php/db/web_chat.db "SELECT * FROM web_chat_sessions;" > sessions.csv
sqlite3 php/db/web_chat.db "SELECT * FROM web_chat_messages;" > messages.csv
sqlite3 php/db/web_chat.db "SELECT * FROM web_chat_responses;" > responses.csv
```

#### 2. Import to Flask System
```python
def migrate_from_php(php_db_path: str, flask_db_path: str):
    """Migrate data from PHP SQLite to Flask SQLite"""
    
    # Connect to PHP database
    php_conn = sqlite3.connect(php_db_path)
    php_cursor = php_conn.cursor()
    
    # Connect to Flask database
    flask_db = DatabaseManager(flask_db_path)
    
    try:
        # Migrate sessions
        php_cursor.execute("SELECT * FROM web_chat_sessions")
        sessions = php_cursor.fetchall()
        
        for session in sessions:
            flask_db.execute_insert("""
                INSERT INTO web_chat_sessions (id, uid, created_at, last_active, ip_address, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, session)
        
        # Migrate messages
        php_cursor.execute("SELECT * FROM web_chat_messages")
        messages = php_cursor.fetchall()
        
        for message in messages:
            flask_db.execute_insert("""
                INSERT INTO web_chat_messages (id, session_id, message, timestamp, processed, broca_message_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, message)
        
        # Migrate responses
        php_cursor.execute("SELECT * FROM web_chat_responses")
        responses = php_cursor.fetchall()
        
        for response in responses:
            flask_db.execute_insert("""
                INSERT INTO web_chat_responses (id, session_id, response, timestamp, message_id)
                VALUES (?, ?, ?, ?, ?)
            """, response)
        
        print(f"Migration completed: {len(sessions)} sessions, {len(messages)} messages, {len(responses)} responses")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        raise
    finally:
        php_conn.close()
```

### Data Validation

```python
def validate_migration(php_db_path: str, flask_db_path: str) -> bool:
    """Validate that migration was successful"""
    
    php_conn = sqlite3.connect(php_db_path)
    flask_conn = sqlite3.connect(flask_db_path)
    
    try:
        # Check session count
        php_count = php_conn.execute("SELECT COUNT(*) FROM web_chat_sessions").fetchone()[0]
        flask_count = flask_conn.execute("SELECT COUNT(*) FROM web_chat_sessions").fetchone()[0]
        
        if php_count != flask_count:
            print(f"Session count mismatch: PHP={php_count}, Flask={flask_count}")
            return False
        
        # Check message count
        php_count = php_conn.execute("SELECT COUNT(*) FROM web_chat_messages").fetchone()[0]
        flask_count = flask_conn.execute("SELECT COUNT(*) FROM web_chat_messages").fetchone()[0]
        
        if php_count != flask_count:
            print(f"Message count mismatch: PHP={php_count}, Flask={flask_count}")
            return False
        
        # Check response count
        php_count = php_conn.execute("SELECT COUNT(*) FROM web_chat_responses").fetchone()[0]
        flask_count = flask_conn.execute("SELECT COUNT(*) FROM web_chat_responses").fetchone()[0]
        
        if php_count != flask_count:
            print(f"Response count mismatch: PHP={php_count}, Flask={flask_count}")
            return False
        
        print("Migration validation successful")
        return True
        
    finally:
        php_conn.close()
        flask_conn.close()
```

## Database Maintenance

### Backup Procedures

```python
import shutil
import datetime

def backup_database(db_path: str, backup_dir: str = "backups"):
    """Create a timestamped backup of the database"""
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"web_chat_bridge_{timestamp}.db")
    
    shutil.copy2(db_path, backup_path)
    print(f"Database backed up to: {backup_path}")
    
    # Clean up old backups (keep last 7)
    cleanup_old_backups(backup_dir, 7)

def cleanup_old_backups(backup_dir: str, keep_count: int):
    """Remove old backup files, keeping only the most recent ones"""
    backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
    backup_files.sort(reverse=True)
    
    for old_backup in backup_files[keep_count:]:
        os.remove(os.path.join(backup_dir, old_backup))
        print(f"Removed old backup: {old_backup}")
```

### Database Optimization

```python
def optimize_database(db_path: str):
    """Optimize SQLite database performance"""
    conn = sqlite3.connect(db_path)
    
    try:
        # Analyze tables for better query planning
        conn.execute("ANALYZE")
        
        # Rebuild indexes
        conn.execute("REINDEX")
        
        # Vacuum to reclaim space
        conn.execute("VACUUM")
        
        print("Database optimization completed")
        
    finally:
        conn.close()
```

## Testing Database Operations

### Unit Tests

```python
import unittest
import tempfile
import os

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        """Set up test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = DatabaseManager(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_session(self):
        """Test session creation"""
        session_id = "test_session_123"
        result = self.db.execute_insert(
            "INSERT INTO web_chat_sessions (id, created_at, last_active) VALUES (?, datetime('now'), datetime('now'))",
            (session_id,)
        )
        self.assertIsNotNone(result)
        
        # Verify session exists
        session = self.db.execute_single("SELECT * FROM web_chat_sessions WHERE id = ?", (session_id,))
        self.assertIsNotNone(session)
        self.assertEqual(session['id'], session_id)
    
    def test_message_operations(self):
        """Test message creation and retrieval"""
        # Create session first
        session_id = "test_session_456"
        self.db.execute_insert(
            "INSERT INTO web_chat_sessions (id, created_at, last_active) VALUES (?, datetime('now'), datetime('now'))",
            (session_id,)
        )
        
        # Create message
        message_text = "Test message"
        message_id = self.db.execute_insert(
            "INSERT INTO web_chat_messages (session_id, message, timestamp) VALUES (?, ?, datetime('now'))",
            (session_id, message_text)
        )
        
        # Retrieve message
        message = self.db.execute_single(
            "SELECT * FROM web_chat_messages WHERE id = ?", (message_id,)
        )
        self.assertEqual(message['message'], message_text)
        self.assertEqual(message['session_id'], session_id)

if __name__ == '__main__':
    unittest.main()
```

## Performance Considerations

### Query Optimization

1. **Use prepared statements** for all database operations
2. **Implement connection pooling** for high-traffic scenarios
3. **Add appropriate indexes** on frequently queried fields
4. **Use transactions** for multi-table operations
5. **Monitor query performance** and optimize slow queries

### Memory Management

1. **Close database connections** after each operation
2. **Use context managers** for automatic resource cleanup
3. **Implement pagination** for large result sets
4. **Cache frequently accessed data** when appropriate

### Scalability

1. **Consider database sharding** for very large datasets
2. **Implement read replicas** for read-heavy workloads
3. **Use connection pooling** for concurrent access
4. **Monitor database size** and implement archiving strategies

This database schema and migration guide provides everything needed to implement the Flask port with 100% database compatibility and optimal performance.
