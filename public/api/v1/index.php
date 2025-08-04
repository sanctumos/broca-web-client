<?php
/**
 * API v1 - Single entry point with querystring routing
 * Vanilla Nginx compatible
 */

// Include required files
require_once '../../config/settings.php';
require_once '../../includes/api_response.php';
require_once '../../includes/auth.php';
require_once '../../includes/utils.php';
require_once '../../config/database.php';

// Set CORS headers
set_cors_headers();

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit();
}

// Periodically cleanup inactive sessions (10% chance on each API call)
maybe_cleanup_inactive_sessions(0.1);

// Get the action from querystring
$action = $_GET['action'] ?? '';

// Route to appropriate handler based on action
switch ($action) {
    case 'messages':
        handle_messages();
        break;
    case 'inbox':
        handle_inbox();
        break;
    case 'outbox':
        handle_outbox();
        break;
    case 'responses':
        handle_responses();
        break;
    case 'sessions':
        handle_sessions();
        break;
    case 'config':
        handle_config();
        break;
    case 'cleanup':
        handle_cleanup();
        break;
                       case 'clear_data':
            handle_clear_data();
            break;
        case 'cleanup_logs':
            handle_cleanup_logs();
            break;
        case 'session_messages':
            handle_session_messages();
            break;
           default:
               send_error_response('Invalid action', 400);
               break;
}

/**
 * Handle POST /api/v1/index.php?action=messages
 * Send a message from the web chat widget
 */
function handle_messages() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        send_error_response('Method not allowed', 405);
    }
    
    // Rate limiting
    check_rate_limit('/api/messages');
    
    // Get and validate input
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!$input) {
        send_error_response('Invalid JSON', 400);
    }
    
    $session_id = sanitize_input($input['session_id'] ?? '');
    $message = sanitize_input($input['message'] ?? '');
    $timestamp = $input['timestamp'] ?? date('c');
    
    // Validate required fields
    if (empty($session_id) || empty($message)) {
        send_error_response('Missing required fields', 400);
    }
    
    if (!validate_session_id($session_id)) {
        send_error_response('Invalid session ID', 400);
    }
    
    if (!validate_message($message)) {
        send_error_response('Invalid message', 400);
    }
    
    try {
        $pdo = get_db_connection();
        
        // Check/create session
        if (!is_session_active($session_id)) {
            create_session($session_id);
        }
        
        // Get or create UID for this session
        $ip_address = get_client_ip();
        $user_data = get_or_create_web_chat_user($session_id, $ip_address);
        $uid = $user_data['uid'];
        $is_new_user = $user_data['is_new'];
        
        // Store message
        $stmt = $pdo->prepare("
            INSERT INTO web_chat_messages (session_id, message, timestamp)
            VALUES (?, ?, ?)
        ");
        $stmt->execute([$session_id, $message, $timestamp]);
        $message_id = $pdo->lastInsertId();
        
        // Log request
        log_api_request('/api/messages', 'POST');
        
        send_success_response([
            'message_id' => $message_id,
            'session_id' => $session_id,
            'timestamp' => $timestamp,
            'uid' => $uid,
            'is_new_user' => $is_new_user
        ], 'Message received');
        
    } catch (Exception $e) {
        log_api_request('/api/messages', 'POST', [], 500);
        send_error_response('Internal server error', 500);
    }
}

/**
 * Handle GET /api/v1/index.php?action=inbox
 * Retrieve unprocessed messages for Broca2 plugin
 */
function handle_inbox() {
    if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
        send_error_response('Method not allowed', 405);
    }
    
    // Authentication required
    require_auth();
    
    // Rate limiting
    check_rate_limit('/api/inbox');
    
    // Get query parameters
    $limit = min((int)($_GET['limit'] ?? 50), 100);
    $offset = (int)($_GET['offset'] ?? 0);
    $since = $_GET['since'] ?? '';
    
    try {
        $pdo = get_db_connection();
        
        // Build query
        $where_conditions = ['processed = 0'];
        $params = [];
        
        if ($since) {
            $where_conditions[] = 'timestamp > ?';
            $params[] = $since;
        }
        
        $where_clause = implode(' AND ', $where_conditions);
        
        // Get messages with UID information
        $stmt = $pdo->prepare("
            SELECT m.id, m.session_id, m.message, m.timestamp, s.uid
            FROM web_chat_messages m
            LEFT JOIN web_chat_sessions s ON m.session_id = s.id
            WHERE {$where_clause}
            ORDER BY m.timestamp ASC
            LIMIT ? OFFSET ?
        ");
        $params[] = $limit;
        $params[] = $offset;
        $stmt->execute($params);
        $messages = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        // Get total count
        $stmt = $pdo->prepare("
            SELECT COUNT(*) as total
            FROM web_chat_messages
            WHERE {$where_clause}
        ");
        array_pop($params); // Remove limit
        array_pop($params); // Remove offset
        $stmt->execute($params);
        $total = $stmt->fetch(PDO::FETCH_ASSOC)['total'];
        
        // Mark messages as processed
        if (!empty($messages)) {
            $message_ids = array_column($messages, 'id');
            $placeholders = str_repeat('?,', count($message_ids) - 1) . '?';
            $stmt = $pdo->prepare("
                UPDATE web_chat_messages
                SET processed = 1
                WHERE id IN ({$placeholders})
            ");
            $stmt->execute($message_ids);
        }
        
        // Log request
        log_api_request('/api/inbox', 'GET');
        
        send_success_response([
            'messages' => $messages,
            'pagination' => [
                'total' => $total,
                'limit' => $limit,
                'offset' => $offset,
                'has_more' => ($offset + $limit) < $total
            ]
        ]);
        
    } catch (Exception $e) {
        log_api_request('/api/inbox', 'GET', [], 500);
        send_error_response('Internal server error', 500);
    }
}

/**
 * Handle POST /api/v1/index.php?action=outbox
 * Send agent response back to web chat
 */
function handle_outbox() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        send_error_response('Method not allowed', 405);
    }
    
    // Authentication required
    require_auth();
    
    // Rate limiting
    check_rate_limit('/api/outbox');
    
    // Get and validate input
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!$input) {
        send_error_response('Invalid JSON', 400);
    }
    
    $session_id = sanitize_input($input['session_id'] ?? '');
    $response = sanitize_input($input['response'] ?? '');
    $message_id = (int)($input['message_id'] ?? 0);
    $timestamp = $input['timestamp'] ?? date('c');
    
    // Validate required fields
    if (empty($session_id) || empty($response)) {
        send_error_response('Missing required fields', 400);
    }
    
    if (!validate_session_id($session_id)) {
        send_error_response('Invalid session ID', 400);
    }
    
    if (!validate_message($response)) {
        send_error_response('Invalid response', 400);
    }
    
    try {
        $pdo = get_db_connection();
        
        // Check session activity
        if (!is_session_active($session_id)) {
            send_error_response('Invalid or expired session', 400);
        }
        
        // Store response
        $stmt = $pdo->prepare("
            INSERT INTO web_chat_responses (session_id, response, message_id, timestamp)
            VALUES (?, ?, ?, ?)
        ");
        $stmt->execute([$session_id, $response, $message_id ?: null, $timestamp]);
        $response_id = $pdo->lastInsertId();
        
        // Log request
        log_api_request('/api/outbox', 'POST');
        
        send_success_response([
            'response_id' => $response_id,
            'session_id' => $session_id,
            'timestamp' => $timestamp
        ], 'Response sent successfully');
        
    } catch (Exception $e) {
        log_api_request('/api/outbox', 'POST', [], 500);
        send_error_response('Internal server error', 500);
    }
}

/**
 * Handle GET /api/v1/index.php?action=responses&session_id=xxx
 * Get responses for a specific session
 */
function handle_responses() {
    if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
        send_error_response('Method not allowed', 405);
    }
    
    // Rate limiting
    check_rate_limit('/api/responses');
    
    $session_id = sanitize_input($_GET['session_id'] ?? '');
    $since = $_GET['since'] ?? '';
    
    if (empty($session_id)) {
        send_error_response('Missing session_id parameter', 400);
    }
    
    if (!validate_session_id($session_id)) {
        send_error_response('Invalid session ID', 400);
    }
    
    try {
        $pdo = get_db_connection();
        
        // Check session activity - create if doesn't exist
        if (!is_session_active($session_id)) {
            // Try to create the session if it doesn't exist
            if (!create_session($session_id)) {
                send_error_response('Invalid session ID', 400);
            }
        }
        
        // Build query
        $where_conditions = ['session_id = ?'];
        $params = [$session_id];
        
        if ($since) {
            $where_conditions[] = 'timestamp > ?';
            $params[] = $since;
        }
        
        $where_clause = implode(' AND ', $where_conditions);
        
        // Get responses
        $stmt = $pdo->prepare("
            SELECT id, response, timestamp, message_id
            FROM web_chat_responses
            WHERE {$where_clause}
            ORDER BY timestamp ASC
        ");
        $stmt->execute($params);
        $responses = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        // Log request
        log_api_request('/api/responses', 'GET');
        
        send_success_response([
            'session_id' => $session_id,
            'responses' => $responses
        ]);
        
    } catch (Exception $e) {
        log_api_request('/api/responses', 'GET', [], 500);
        send_error_response('Internal server error', 500);
    }
}

/**
 * Handle GET /api/v1/index.php?action=sessions
 * List active sessions (admin only)
 */
function handle_sessions() {
    if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
        send_error_response('Method not allowed', 405);
    }
    
    // Admin authentication required
    require_admin_auth();
    
    // Rate limiting
    check_rate_limit('/api/sessions');
    
    // Get query parameters
    $limit = min((int)($_GET['limit'] ?? 50), 100);
    $offset = (int)($_GET['offset'] ?? 0);
    $active = $_GET['active'] ?? 'true';
    
    try {
        $pdo = get_db_connection();
        
        // Build query
        $where_conditions = [];
        $params = [];
        
        if ($active === 'true') {
            // Show sessions active in the last 30 minutes (SESSION_TIMEOUT)
            $where_conditions[] = 'last_active > datetime("now", "-' . SESSION_TIMEOUT . ' seconds")';
        }
        
        $where_clause = !empty($where_conditions) ? 'WHERE ' . implode(' AND ', $where_conditions) : '';
        
        // Get sessions with counts and UID information
        $stmt = $pdo->prepare("
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
            {$where_clause}
            GROUP BY s.id
            ORDER BY s.last_active DESC
            LIMIT ? OFFSET ?
        ");
        $params[] = $limit;
        $params[] = $offset;
        $stmt->execute($params);
        $sessions = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        // Get total count
        $stmt = $pdo->prepare("
            SELECT COUNT(*) as total
            FROM web_chat_sessions s
            {$where_clause}
        ");
        array_pop($params); // Remove limit
        array_pop($params); // Remove offset
        $stmt->execute($params);
        $total = $stmt->fetch(PDO::FETCH_ASSOC)['total'];
        
        // Process metadata
        foreach ($sessions as &$session) {
            if ($session['metadata']) {
                $session['metadata'] = json_decode($session['metadata'], true);
            }
        }
        
        // Log request
        log_api_request('/api/sessions', 'GET');
        
        send_success_response([
            'sessions' => $sessions,
            'pagination' => [
                'total' => $total,
                'limit' => $limit,
                'offset' => $offset,
                'has_more' => ($offset + $limit) < $total
            ]
        ]);
        
    } catch (Exception $e) {
        log_api_request('/api/sessions', 'GET', [], 500);
        send_error_response('Internal server error', 500);
    }
}

/**
 * Handle GET/POST /api/v1/index.php?action=config
 * Get or update configuration settings
 */
function handle_config() {
    // Admin authentication required
    require_admin_auth();
    
    if ($_SERVER['REQUEST_METHOD'] === 'GET') {
        // Get current configuration
        try {
            send_success_response([
                'session_timeout' => SESSION_TIMEOUT,
                'api_key' => get_api_key(),
                'admin_key' => get_admin_key()
            ]);
        } catch (Exception $e) {
            send_error_response('Internal server error', 500);
        }
    } elseif ($_SERVER['REQUEST_METHOD'] === 'POST') {
        // Update configuration
        $input = json_decode(file_get_contents('php://input'), true);
        
        if (!$input) {
            send_error_response('Invalid JSON', 400);
        }
        
        $api_key = sanitize_input($input['api_key'] ?? '');
        $admin_key = sanitize_input($input['admin_key'] ?? '');
        
        if (empty($api_key) || empty($admin_key)) {
            send_error_response('Missing required fields', 400);
        }
        
        try {
            // Update keys in settings file
            update_config_keys($api_key, $admin_key);
            
            log_message('INFO', 'Configuration updated', [
                'api_key_updated' => !empty($api_key),
                'admin_key_updated' => !empty($admin_key)
            ]);
            
            send_success_response([
                'message' => 'Configuration updated successfully'
            ]);
            
        } catch (Exception $e) {
            log_message('ERROR', 'Failed to update configuration', [
                'error' => $e->getMessage()
            ]);
            send_error_response('Internal server error', 500);
        }
    } else {
        send_error_response('Method not allowed', 405);
    }
}

/**
 * Handle POST /api/v1/index.php?action=cleanup
 * Manual cleanup of inactive sessions
 */
function handle_cleanup() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        send_error_response('Method not allowed', 405);
    }
    
    // Admin authentication required
    require_admin_auth();
    
    try {
        $cleaned_count = cleanup_inactive_sessions();
        
        log_message('INFO', 'Manual cleanup performed', [
            'cleaned_count' => $cleaned_count
        ]);
        
        send_success_response([
            'cleaned_count' => $cleaned_count,
            'message' => "Cleaned up {$cleaned_count} inactive sessions"
        ]);
        
    } catch (Exception $e) {
        log_message('ERROR', 'Manual cleanup failed', [
            'error' => $e->getMessage()
        ]);
        send_error_response('Internal server error', 500);
    }
}

/**
 * Handle POST /api/v1/index.php?action=clear_data
 * Clear all data (dangerous operation)
 */
function handle_clear_data() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        send_error_response('Method not allowed', 405);
    }
    
    // Admin authentication required
    require_admin_auth();
    
    try {
        $pdo = get_db_connection();
        
        // Clear all data
        $pdo->exec("DELETE FROM web_chat_responses");
        $pdo->exec("DELETE FROM web_chat_messages");
        $pdo->exec("DELETE FROM web_chat_sessions");
        
        $response_count = $pdo->query("SELECT COUNT(*) FROM web_chat_responses")->fetchColumn();
        $message_count = $pdo->query("SELECT COUNT(*) FROM web_chat_messages")->fetchColumn();
        $session_count = $pdo->query("SELECT COUNT(*) FROM web_chat_sessions")->fetchColumn();
        
        log_message('WARNING', 'All data cleared by admin', [
            'admin_ip' => get_client_ip()
        ]);
        
        send_success_response([
            'message' => 'All data cleared successfully',
            'remaining_data' => [
                'responses' => $response_count,
                'messages' => $message_count,
                'sessions' => $session_count
            ]
        ]);
        
    } catch (Exception $e) {
        log_message('ERROR', 'Failed to clear data', [
            'error' => $e->getMessage()
        ]);
        send_error_response('Internal server error', 500);
    }
} 

/**
 * Handle GET /api/v1/index.php?action=session_messages&session_id={session_id}
 * Get messages and responses for a specific session
 */
function handle_session_messages() {
    if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
        send_error_response('Method not allowed', 405);
    }
    
    // Admin authentication required
    require_admin_auth();
    
    $session_id = sanitize_input($_GET['session_id'] ?? '');
    
    if (empty($session_id)) {
        send_error_response('Session ID required', 400);
    }
    
    if (!validate_session_id($session_id)) {
        send_error_response('Invalid session ID', 400);
    }
    
    try {
        $pdo = get_db_connection();
        
        // Get session info
        $stmt = $pdo->prepare("
            SELECT id, uid, created_at, last_active, ip_address, metadata
            FROM web_chat_sessions 
            WHERE id = ?
        ");
        $stmt->execute([$session_id]);
        $session = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if (!$session) {
            send_error_response('Session not found', 404);
        }
        
        // Get messages for this session
        $stmt = $pdo->prepare("
            SELECT id, session_id, message, timestamp
            FROM web_chat_messages 
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ");
        $stmt->execute([$session_id]);
        $messages = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        // Get responses for this session
        $stmt = $pdo->prepare("
            SELECT id, session_id, response, timestamp
            FROM web_chat_responses 
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ");
        $stmt->execute([$session_id]);
        $responses = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        // Log request
        log_api_request('/api/messages', 'GET');
        
        send_success_response([
            'session' => $session,
            'messages' => $messages,
            'responses' => $responses
        ], 'Session messages retrieved');
        
    } catch (Exception $e) {
        log_api_request('/api/messages', 'GET', [], 500);
        send_error_response('Internal server error', 500);
    }
}

/**
 * Handle POST /api/v1/index.php?action=cleanup_logs
 * Manually trigger log cleanup and rotation
 */
function handle_cleanup_logs() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        send_error_response('Method not allowed', 405);
    }
    
    // Admin authentication required
    require_admin_auth();
    
    try {
        // Force log pruning
        prune_logs();
        
        // Get log file info
        $log_file = LOG_FILE;
        $log_size = file_exists($log_file) ? filesize($log_file) : 0;
        $log_size_mb = round($log_size / (1024 * 1024), 2);
        
        // Count backup files
        $backup_files = glob($log_file . '.*');
        $backup_count = count($backup_files);
        
        // Calculate total log size including backups
        $total_size = $log_size;
        foreach ($backup_files as $backup) {
            $total_size += filesize($backup);
        }
        $total_size_mb = round($total_size / (1024 * 1024), 2);
        
        log_message('INFO', 'Manual log cleanup triggered by admin', [
            'admin_ip' => get_client_ip(),
            'current_size_mb' => $log_size_mb,
            'backup_count' => $backup_count,
            'total_size_mb' => $total_size_mb
        ]);
        
        send_success_response([
            'message' => 'Log cleanup completed successfully',
            'current_log_size_mb' => $log_size_mb,
            'backup_files_count' => $backup_count,
            'total_log_size_mb' => $total_size_mb,
            'retention_days' => LOG_RETENTION_DAYS,
            'max_size_mb' => LOG_MAX_SIZE_MB
        ]);
        
    } catch (Exception $e) {
        log_message('ERROR', 'Failed to cleanup logs', [
            'error' => $e->getMessage(),
            'admin_ip' => get_client_ip()
        ]);
        send_error_response('Internal server error', 500);
    }
} 