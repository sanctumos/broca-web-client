<?php
/**
 * Database configuration for Web Chat Bridge
 */

// Database configuration
define('DB_PATH', __DIR__ . '/../../db/web_chat.db');
define('DB_TIMEOUT', 30);

// Database connection function
function get_db_connection() {
    try {
        $pdo = new PDO('sqlite:' . DB_PATH);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $pdo->setAttribute(PDO::ATTR_TIMEOUT, DB_TIMEOUT);
        return $pdo;
    } catch (PDOException $e) {
        error_log("Database connection failed: " . $e->getMessage());
        throw new Exception("Database connection failed");
    }
}

// Initialize database tables
function init_database() {
    $pdo = get_db_connection();
    
    // Create web chat sessions table with UID support
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS web_chat_sessions (
            id VARCHAR(64) PRIMARY KEY,
            uid VARCHAR(16) UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_active TEXT DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            metadata TEXT
        )
    ");
    
    // Create web chat messages table
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS web_chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id VARCHAR(64),
            message TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            processed INTEGER DEFAULT 0,
            broca_message_id INTEGER NULL,
            FOREIGN KEY (session_id) REFERENCES web_chat_sessions(id)
        )
    ");
    
    // Create web chat responses table
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS web_chat_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id VARCHAR(64),
            response TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            message_id INTEGER NULL,
            FOREIGN KEY (session_id) REFERENCES web_chat_sessions(id),
            FOREIGN KEY (message_id) REFERENCES web_chat_messages(id)
        )
    ");
    
    // Create rate limiting table
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS rate_limits (
            ip_address VARCHAR(45),
            endpoint VARCHAR(50),
            count INTEGER DEFAULT 1,
            window_start TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (ip_address, endpoint)
        )
    ");
    
    // Create indexes for better performance
    $pdo->exec("CREATE INDEX IF NOT EXISTS idx_messages_session ON web_chat_messages(session_id)");
    $pdo->exec("CREATE INDEX IF NOT EXISTS idx_messages_processed ON web_chat_messages(processed)");
    $pdo->exec("CREATE INDEX IF NOT EXISTS idx_responses_session ON web_chat_responses(session_id)");
    $pdo->exec("CREATE INDEX IF NOT EXISTS idx_rate_limits_window ON rate_limits(window_start)");
    $pdo->exec("CREATE INDEX IF NOT EXISTS idx_sessions_uid ON web_chat_sessions(uid)");
    $pdo->exec("CREATE INDEX IF NOT EXISTS idx_sessions_ip ON web_chat_sessions(ip_address)");
} 