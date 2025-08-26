<?php
/**
 * Test Utilities
 * Common functions and helpers for PHP widget tests
 */

class TestUtils
{
    /**
     * Set up the test environment
     */
    public static function setupTestEnvironment()
    {
        // Create test database
        self::createTestDatabase();
        
        // Set up test data
        self::setupTestData();
    }
    
    /**
     * Create a test database
     */
    public static function createTestDatabase()
    {
        $dbPath = $_ENV['TEST_DATABASE_PATH'];
        
        // Remove existing test database
        if (file_exists($dbPath)) {
            unlink($dbPath);
        }
        
        // Create new test database
        $pdo = new PDO("sqlite:$dbPath");
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        // Create tables (simplified schema for testing)
        $pdo->exec("
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ");
        
        $pdo->exec("
            CREATE TABLE IF NOT EXISTS web_chat_sessions (
                id TEXT PRIMARY KEY,
                uid TEXT,
                ip_address TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ");
        
        $pdo->exec("
            CREATE TABLE IF NOT EXISTS web_chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                processed INTEGER DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES web_chat_sessions(id)
            )
        ");
        
        $pdo->exec("
            CREATE TABLE IF NOT EXISTS web_chat_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES web_chat_messages(id)
            )
        ");
        
        $pdo->close();
    }
    
    /**
     * Set up test data
     */
    public static function setupTestData()
    {
        $dbPath = $_ENV['TEST_DATABASE_PATH'];
        $pdo = new PDO("sqlite:$dbPath");
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        // Insert test configuration
        $pdo->exec("
            INSERT OR REPLACE INTO system_config (config_key, config_value, description) VALUES 
            ('api_key', 'test_api_key_123', 'Test API key'),
            ('admin_key', 'test_admin_key_456', 'Test admin key'),
            ('session_timeout', '1800', 'Test session timeout'),
            ('max_message_length', '10000', 'Test max message length'),
            ('rate_limit_window', '3600', 'Test rate limit window')
        ");
        
        // Insert test session
        $pdo->exec("
            INSERT OR REPLACE INTO web_chat_sessions (id, uid, ip_address) VALUES 
            ('session_test_123', 'test_uid_456', '127.0.0.1')
        ");
        
        $pdo->close();
    }
    
    /**
     * Clean up test environment
     */
    public static function cleanupTestEnvironment()
    {
        $dbPath = $_ENV['TEST_DATABASE_PATH'];
        if (file_exists($dbPath)) {
            unlink($dbPath);
        }
    }
    
    /**
     * Mock HTTP request
     */
    public static function mockRequest($method = 'GET', $uri = '/', $params = [], $headers = [])
    {
        $_SERVER['REQUEST_METHOD'] = $method;
        $_SERVER['REQUEST_URI'] = $uri;
        $_GET = $params;
        $_POST = $method === 'POST' ? $params : [];
        $_SERVER['HTTP_ACCEPT'] = $headers['Accept'] ?? 'application/json';
        $_SERVER['HTTP_CONTENT_TYPE'] = $headers['Content-Type'] ?? 'application/json';
        
        if (isset($headers['Authorization'])) {
            $_SERVER['HTTP_AUTHORIZATION'] = $headers['Authorization'];
        }
    }
    
    /**
     * Capture output from a PHP script
     */
    public static function captureOutput($callback)
    {
        ob_start();
        $callback();
        $output = ob_get_contents();
        ob_end_clean();
        return $output;
    }
    
    /**
     * Assert JSON response
     */
    public static function assertJsonResponse($output, $expectedStatus = 200)
    {
        $lines = explode("\n", $output);
        $headers = [];
        $body = '';
        $inBody = false;
        
        foreach ($lines as $line) {
            if (empty($line)) {
                $inBody = true;
                continue;
            }
            
            if ($inBody) {
                $body .= $line;
            } else {
                $headers[] = $line;
            }
        }
        
        // Check if response contains JSON
        $jsonData = json_decode($body, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception("Response is not valid JSON: " . json_last_error_msg());
        }
        
        return $jsonData;
    }
    
    /**
     * Create test API key
     */
    public static function createTestApiKey()
    {
        return 'test_api_key_' . uniqid();
    }
    
    /**
     * Create test session ID
     */
    public static function createTestSessionId()
    {
        return 'session_test_' . uniqid();
    }
    
    /**
     * Simulate widget configuration
     */
    public static function getTestWidgetConfig()
    {
        return [
            'apiKey' => self::createTestApiKey(),
            'position' => 'bottom-right',
            'theme' => 'light',
            'title' => 'Test Chat Widget',
            'primaryColor' => '#007bff',
            'language' => 'en',
            'autoOpen' => false,
            'notifications' => true,
            'sound' => true
        ];
    }
}
