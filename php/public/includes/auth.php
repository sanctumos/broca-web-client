<?php
/**
 * Authentication and rate limiting functionality
 */

require_once __DIR__ . '/../config/settings.php';
require_once __DIR__ . '/../config/database.php';
require_once __DIR__ . '/api_response.php';

/**
 * Check if request is authenticated with API key
 * 
 * @return bool True if authenticated, false otherwise
 */
function is_authenticated() {
    $headers = getallheaders();
    $auth_header = $headers['Authorization'] ?? $headers['authorization'] ?? '';
    
    if (empty($auth_header)) {
        return false;
    }
    
    if (strpos($auth_header, API_KEY_PREFIX) !== 0) {
        return false;
    }
    
    $api_key = substr($auth_header, strlen(API_KEY_PREFIX));
    return $api_key === get_api_key();
}

/**
 * Check if request is authenticated with admin key
 * 
 * @return bool True if authenticated, false otherwise
 */
function is_admin_authenticated() {
    $headers = getallheaders();
    $auth_header = $headers['Authorization'] ?? $headers['authorization'] ?? '';
    
    if (empty($auth_header)) {
        return false;
    }
    
    if (strpos($auth_header, API_KEY_PREFIX) !== 0) {
        return false;
    }
    
    $admin_key = substr($auth_header, strlen(API_KEY_PREFIX));
    return $admin_key === get_admin_key();
}

/**
 * Require authentication for API key
 */
function require_auth() {
    if (!is_authenticated()) {
        log_message('WARNING', 'Unauthorized API access attempt', [
            'ip' => get_client_ip(),
            'endpoint' => $_SERVER['REQUEST_URI'] ?? 'unknown'
        ]);
        send_unauthorized_response('Invalid or missing API key');
    }
}

/**
 * Require authentication for admin key
 */
function require_admin_auth() {
    if (!is_admin_authenticated()) {
        log_message('WARNING', 'Unauthorized admin access attempt', [
            'ip' => get_client_ip(),
            'endpoint' => $_SERVER['REQUEST_URI'] ?? 'unknown'
        ]);
        send_unauthorized_response('Invalid or missing admin key');
    }
}

/**
 * Check rate limiting for current request
 * 
 * @param string $endpoint API endpoint
 * @return bool True if within limits, false if rate limited
 */
function check_rate_limit($endpoint) {
    $ip = get_client_ip();
    $current_time = time();
    $window_start = $current_time - RATE_LIMIT_WINDOW;
    
    try {
        $pdo = get_db_connection();
        
        // Clean up old rate limit entries
        $stmt = $pdo->prepare("DELETE FROM rate_limits WHERE window_start < ?");
        $stmt->execute([date('Y-m-d H:i:s', $window_start)]);
        
        // Check current rate limit for this IP and endpoint
        $stmt = $pdo->prepare("
            SELECT COUNT(*) as count 
            FROM rate_limits 
            WHERE ip_address = ? AND endpoint = ? AND window_start >= ?
        ");
        $stmt->execute([$ip, $endpoint, date('Y-m-d H:i:s', $window_start)]);
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        $current_count = $result['count'] ?? 0;
        
        // Get endpoint-specific limit
        global $ENDPOINT_RATE_LIMITS;
        $endpoint_limit = $ENDPOINT_RATE_LIMITS[$endpoint] ?? RATE_LIMIT_ENDPOINT_MAX;
        
        if ($current_count >= $endpoint_limit) {
            log_message('WARNING', 'Rate limit exceeded', [
                'ip' => $ip,
                'endpoint' => $endpoint,
                'count' => $current_count,
                'limit' => $endpoint_limit
            ]);
            return false;
        }
        
        // Add current request to rate limit tracking
        $stmt = $pdo->prepare("
            INSERT OR REPLACE INTO rate_limits (ip_address, endpoint, count, window_start)
            VALUES (?, ?, ?, ?)
        ");
        $stmt->execute([
            $ip,
            $endpoint,
            $current_count + 1,
            date('Y-m-d H:i:s', $current_time)
        ]);
        
        return true;
        
    } catch (Exception $e) {
        log_message('ERROR', 'Rate limit check failed', [
            'error' => $e->getMessage(),
            'ip' => $ip,
            'endpoint' => $endpoint
        ]);
        // If rate limiting fails, allow the request to proceed
        return true;
    }
}

/**
 * Check overall rate limiting for IP
 * 
 * @return bool True if within limits, false if rate limited
 */
function check_overall_rate_limit() {
    $ip = get_client_ip();
    $current_time = time();
    $window_start = $current_time - RATE_LIMIT_WINDOW;
    
    try {
        $pdo = get_db_connection();
        
        // Check total requests for this IP
        $stmt = $pdo->prepare("
            SELECT COUNT(*) as count 
            FROM rate_limits 
            WHERE ip_address = ? AND window_start >= ?
        ");
        $stmt->execute([$ip, date('Y-m-d H:i:s', $window_start)]);
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        $total_count = $result['count'] ?? 0;
        
        if ($total_count >= RATE_LIMIT_MAX_REQUESTS) {
            log_message('WARNING', 'Overall rate limit exceeded', [
                'ip' => $ip,
                'count' => $total_count,
                'limit' => RATE_LIMIT_MAX_REQUESTS
            ]);
            return false;
        }
        
        return true;
        
    } catch (Exception $e) {
        log_message('ERROR', 'Overall rate limit check failed', [
            'error' => $e->getMessage(),
            'ip' => $ip
        ]);
        // If rate limiting fails, allow the request to proceed
        return true;
    }
}

/**
 * Apply rate limiting to current request
 * 
 * @param string $endpoint API endpoint
 */
function apply_rate_limiting($endpoint) {
    // Check overall rate limit first
    if (!check_overall_rate_limit()) {
        send_rate_limit_response(RATE_LIMIT_WINDOW);
    }
    
    // Check endpoint-specific rate limit
    if (!check_rate_limit($endpoint)) {
        send_rate_limit_response(RATE_LIMIT_WINDOW);
    }
}

/**
 * Validate session and check if it's active
 * 
 * @param string $session_id Session ID to validate
 * @return bool True if session is active, false otherwise
 */
function is_session_active($session_id) {
    if (!validate_session_id($session_id)) {
        return false;
    }
    
    try {
        $pdo = get_db_connection();
        
        $stmt = $pdo->prepare("
            SELECT last_active 
            FROM web_chat_sessions 
            WHERE id = ?
        ");
        $stmt->execute([$session_id]);
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if (!$result) {
            return false;
        }
        
        $last_active = strtotime($result['last_active']);
        $current_time = time();
        
        // Check if session has timed out
        if (($current_time - $last_active) > SESSION_TIMEOUT) {
            // Remove expired session
            $stmt = $pdo->prepare("DELETE FROM web_chat_sessions WHERE id = ?");
            $stmt->execute([$session_id]);
            return false;
        }
        
        // Update last active time
        $stmt = $pdo->prepare("
            UPDATE web_chat_sessions 
            SET last_active = CURRENT_TIMESTAMP 
            WHERE id = ?
        ");
        $stmt->execute([$session_id]);
        
        return true;
        
    } catch (Exception $e) {
        log_message('ERROR', 'Session validation failed', [
            'error' => $e->getMessage(),
            'session_id' => $session_id
        ]);
        return false;
    }
}

/**
 * Create a new session
 * 
 * @param string $session_id Session ID
 * @param array $metadata Optional session metadata
 * @return bool True if created successfully, false otherwise
 */
function create_session($session_id, $metadata = []) {
    if (!validate_session_id($session_id)) {
        return false;
    }
    
    try {
        $pdo = get_db_connection();
        
        // Check if session already exists
        $stmt = $pdo->prepare("SELECT id FROM web_chat_sessions WHERE id = ?");
        $stmt->execute([$session_id]);
        if ($stmt->fetch()) {
            return true; // Session already exists
        }
        
        // Create new session
        $stmt = $pdo->prepare("
            INSERT INTO web_chat_sessions (id, metadata) 
            VALUES (?, ?)
        ");
        $stmt->execute([
            $session_id,
            json_encode($metadata)
        ]);
        
        log_message('INFO', 'Session created', [
            'session_id' => $session_id,
            'metadata' => $metadata
        ]);
        
        return true;
        
    } catch (Exception $e) {
        log_message('ERROR', 'Session creation failed', [
            'error' => $e->getMessage(),
            'session_id' => $session_id
        ]);
        return false;
    }
}

/**
 * Get session count for IP address
 * 
 * @param string $ip IP address
 * @return int Number of active sessions
 */
function get_session_count_for_ip($ip) {
    try {
        $pdo = get_db_connection();
        
        // This is a simplified check - in a real implementation,
        // you might want to track IP addresses in the sessions table
        $stmt = $pdo->prepare("
            SELECT COUNT(*) as count 
            FROM web_chat_sessions 
            WHERE last_active > datetime('now', '-1 day')
        ");
        $stmt->execute();
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        
        return $result['count'] ?? 0;
        
    } catch (Exception $e) {
        log_message('ERROR', 'Session count check failed', [
            'error' => $e->getMessage(),
            'ip' => $ip
        ]);
        return 0;
    }
}

/**
 * Check if IP has too many sessions
 * 
 * @param string $ip IP address
 * @return bool True if within limit, false if too many sessions
 */
function check_session_limit($ip) {
    $session_count = get_session_count_for_ip($ip);
    return $session_count < MAX_SESSIONS_PER_IP;
} 