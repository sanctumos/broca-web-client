# Flask Port Specification - Complete Technical Documentation

## Overview

This document provides complete technical specifications for porting the Web Chat Bridge system from PHP to Flask (Python). The Flask version must maintain 100% functional parity with the current PHP implementation, including all API endpoints, authentication mechanisms, database operations, and admin functionality.

## System Architecture

### Current PHP Architecture (Located in `php/` folder)
```
Admin Interface (php/public/web/admin.php) 
    ↓ (HTTP requests)
API Endpoints (php/public/api/v1/index.php)
    ↓ (direct calls)
Database Functions (php/public/includes/utils.php, php/public/includes/auth.php)
    ↓ (direct SQL)
SQLite Database (php/db/web_chat.db)
```

### Required Flask Architecture
```
Admin Interface (Flask templates/static)
    ↓ (HTTP requests)
Flask API Routes (app.py)
    ↓ (direct calls)
Database Functions (database.py, utils.py)
    ↓ (direct SQL)
SQLite Database (identical schema)
```

## Database Schema

### Core Tables

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

#### `rate_limits`
```sql
CREATE TABLE rate_limits (
    ip_address VARCHAR(45),
    endpoint VARCHAR(50),
    count INTEGER,
    window_start TEXT
);
```

### Database Relationships
- `web_chat_messages.session_id` → `web_chat_sessions.id`
- `web_chat_responses.session_id` → `web_chat_sessions.id`
- `web_chat_responses.message_id` → `web_chat_messages.id` (optional)

## Configuration Constants

All configuration values are stored in the database `system_config` table and can be updated through the admin interface. The system provides sensible defaults but allows runtime configuration changes.

### Database Configuration Keys
The following configuration keys are stored in the `system_config` table:

```sql
-- Core API Configuration
'api_key' = 'ObeyG1ant'              -- API key for external integrations
'admin_key' = 'FreeUkra1ne'          -- Admin authentication key

-- Rate Limiting
'rate_limit_window' = '3600'         -- 1 hour in seconds
'rate_limit_max_requests' = '1000'   -- Max requests per window per IP
'rate_limit_endpoint_max' = '100'    -- Max requests per window per endpoint per IP

-- Session Management
'session_timeout' = '1800'           -- 30 minutes in seconds
'max_sessions_per_ip' = '10'        -- Max concurrent sessions per IP

-- Logging and Maintenance
'log_retention_days' = '30'          -- Keep logs for 30 days
'cleanup_probability' = '0.1'        -- Probability of cleanup per request
'debug_mode' = '0'                   -- Enable debug mode (0=disabled, 1=enabled)

-- Security and CORS
'cors_origins' = '*'                 -- Allowed CORS origins
```

### Hardcoded Constants (Not in Database)
Some constants remain hardcoded for performance and consistency:

```python
# API Headers
API_KEY_HEADER = 'Authorization'
API_KEY_PREFIX = 'Bearer '

# Message Validation
MAX_MESSAGE_LENGTH = 10000  # 10KB max message size
MAX_SESSION_ID_LENGTH = 64
MIN_MESSAGE_LENGTH = 1

# Endpoint Rate Limits (can be overridden via database)
ENDPOINT_RATE_LIMITS = {
    '/api/messages': 50,      # 50 messages per hour per IP
    '/api/responses': 200,     # 200 response checks per hour per IP
    '/api/inbox': 120,         # 120 inbox checks per hour (for plugin)
    '/api/outbox': 200,        # 200 outbox posts per hour (for plugin)
    '/api/sessions': 20        # 20 session list requests per hour (admin)
}
```

## API Endpoints Specification

### 1. Message Submission
**Endpoint:** `POST /api/v1/?action=messages`

**Authentication:** None required (public endpoint)

**Rate Limiting:** 50 requests per hour per IP

**Request Body:**
```json
{
    "session_id": "session_abc123",
    "message": "Hello, how can you help me?",
    "timestamp": "2025-08-04T03:17:33+00:00"
}
```

**Required Fields:**
- `session_id`: String, max 64 characters, must match pattern `session_[timestamp]_[random]`
- `message`: String, 1-10KB, non-empty

**Response:**
```json
{
    "success": true,
    "message": "Message received",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "message_id": 1,
        "session_id": "session_abc123",
        "timestamp": "2025-08-04T03:17:33+00:00",
        "uid": "2632f72d266e529c",
        "is_new_user": false
    }
}
```

**Business Logic:**
1. Validate session ID format
2. Check/create session if doesn't exist
3. Generate or retrieve UID for user
4. Store message in database
5. Update session last_active timestamp
6. Return message ID and UID information

### 2. Plugin Inbox (Get Unprocessed Messages)
**Endpoint:** `GET /api/v1/?action=inbox`

**Authentication:** API Key required (Bearer token)

**Rate Limiting:** 120 requests per hour per API key

**Query Parameters:**
- `limit`: Integer, 1-100, default 50
- `offset`: Integer, default 0
- `since`: ISO timestamp (optional)

**Response:**
```json
{
    "success": true,
    "message": "Messages retrieved successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "messages": [
            {
                "id": 1,
                "session_id": "session_abc123",
                "message": "Hello, how can you help me?",
                "timestamp": "2025-08-04T03:08:55.484Z",
                "uid": "2632f72d266e529c"
            }
        ],
        "pagination": {
            "total": 1,
            "limit": 10,
            "offset": 0,
            "has_more": false
        }
    }
}
```

**Business Logic:**
1. Authenticate API key
2. Query unprocessed messages (processed = 0)
3. Join with sessions table to get UID
4. Apply pagination and optional time filtering
5. Mark retrieved messages as processed (processed = 1)
6. Return messages with pagination info

### 3. Plugin Outbox (Submit Response)
**Endpoint:** `POST /api/v1/?action=outbox`

**Authentication:** API Key required (Bearer token)

**Rate Limiting:** 200 requests per hour per API key

**Request Body:**
```json
{
    "session_id": "session_abc123",
    "response": "Hello! I'm here to help you. What can I assist you with today?",
    "message_id": 1,
    "timestamp": "2025-08-04T03:17:33+00:00"
}
```

**Required Fields:**
- `session_id`: String, must be valid session ID
- `response`: String, 1-10KB, non-empty
- `message_id`: Integer (optional), links response to specific message
- `timestamp`: ISO timestamp (optional, defaults to current time)

**Response:**
```json
{
    "success": true,
    "message": "Response sent successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "response_id": 1,
        "session_id": "session_abc123",
        "timestamp": "2025-08-04T03:17:33+00:00"
    }
}
```

**Business Logic:**
1. Authenticate API key
2. Validate session is active
3. Store response in database
4. Link response to message_id if provided
5. Update session last_active timestamp

### 4. Get Session Responses
**Endpoint:** `GET /api/v1/?action=responses`

**Authentication:** None required (public endpoint)

**Rate Limiting:** 200 requests per hour per IP

**Query Parameters:**
- `session_id`: String (required)
- `since`: ISO timestamp (optional)

**Response:**
```json
{
    "success": true,
    "message": "Responses retrieved successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "session_id": "session_abc123",
        "responses": [
            {
                "id": 1,
                "response": "Hello! I am here to help you. What can I assist you with today?",
                "timestamp": "2025-08-04T03:17:33+00:00",
                "message_id": 1
            }
        ]
    }
}
```

**Business Logic:**
1. Validate session ID format
2. Create session if doesn't exist
3. Query responses for session
4. Apply optional time filtering
5. Return responses ordered by timestamp

### 5. Admin: Get Active Sessions
**Endpoint:** `GET /api/v1/?action=sessions`

**Authentication:** Admin password required (Bearer token)

**Rate Limiting:** 20 requests per hour per IP

**Query Parameters:**
- `limit`: Integer, 1-100, default 50
- `offset`: Integer, default 0
- `active`: Boolean string, default 'true'

**Response:**
```json
{
    "success": true,
    "message": "Sessions retrieved successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "sessions": [
            {
                "id": "session_mdwj6vj5_okiiczierw",
                "uid": "2632f72d266e529c",
                "created_at": "2025-08-04 03:08:53",
                "last_active": "2025-08-04 03:17:13",
                "ip_address": "::1",
                "metadata": [],
                "message_count": 2,
                "response_count": 0
            }
        ],
        "pagination": {
            "total": 1,
            "limit": 10,
            "offset": 0,
            "has_more": false
        }
    }
}
```

**Business Logic:**
1. Authenticate admin password
2. Query sessions with message/response counts
3. Filter by active status (last_active > 30 minutes ago)
4. Apply pagination
5. Return sessions with metadata and counts

### 6. Admin: Get Session Messages
**Endpoint:** `GET /api/v1/?action=session_messages`

**Authentication:** Admin password required (Bearer token)

**Query Parameters:**
- `session_id`: String (required)

**Response:**
```json
{
    "success": true,
    "message": "Session messages retrieved",
    "timestamp": "2025-08-04T03:17:40+00:00",
    "data": {
        "session": {
            "id": "session_mdwj6vj5_okiiczierw",
            "uid": "2632f72d266e529c",
            "created_at": "2025-08-04 03:08:53",
            "last_active": "2025-08-04 03:17:13",
            "ip_address": "::1",
            "metadata": "[]"
        },
        "messages": [
            {
                "id": 9,
                "session_id": "session_mdwj6vj5_okiiczierw",
                "message": "whadduo",
                "timestamp": "2025-08-04T03:08:55.484Z"
            }
        ],
        "responses": []
    }
}
```

**Business Logic:**
1. Authenticate admin password
2. Get session information
3. Get all messages for session
4. Get all responses for session
5. Return combined data

### 7. Admin: Get Configuration
**Endpoint:** `GET /api/v1/?action=config`

**Authentication:** Admin password required (Bearer token)

**Response:**
```json
{
    "success": true,
    "message": "Configuration retrieved successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "api_key": "api_abc123def456",
        "admin_key": "free0ps",
        "session_timeout": 1800
    }
}
```

**Business Logic:**
1. Authenticate admin password
2. Return current configuration values
3. Include API key, admin key, and session timeout

### 8. Admin: Update Configuration
**Endpoint:** `POST /api/v1/?action=config`

**Authentication:** Admin password required (Bearer token)

**Request Body:**
```json
{
    "api_key": "api_new_key_123",
    "admin_key": "new_admin_password"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Configuration updated successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "message": "Configuration updated successfully"
    }
}
```

**Business Logic:**
1. Authenticate admin password
2. Validate input fields
3. Update configuration file or database
4. Log configuration change
5. Return success message

### 9. Admin: Manual Cleanup
**Endpoint:** `POST /api/v1/?action=cleanup`

**Authentication:** Admin password required (Bearer token)

**Response:**
```json
{
    "success": true,
    "message": "Cleanup completed successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "cleaned_count": 5,
        "message": "Cleaned up 5 inactive sessions"
    }
}
```

**Business Logic:**
1. Authenticate admin password
2. Find sessions inactive for > 30 minutes
3. Delete inactive sessions and associated data
4. Log cleanup operation
5. Return count of cleaned sessions

### 10. Admin: Clear All Data
**Endpoint:** `POST /api/v1/?action=clear_data`

**Authentication:** Admin password required (Bearer token)

**Response:**
```json
{
    "success": true,
    "message": "All data cleared successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "message": "All data cleared successfully",
        "remaining_data": {
            "responses": 0,
            "messages": 0,
            "sessions": 0
        }
    }
}
```

**Business Logic:**
1. Authenticate admin password
2. Delete all data from all tables
3. Log destructive operation
4. Return confirmation with remaining data counts

### 11. Admin: Cleanup Logs
**Endpoint:** `POST /api/v1/?action=cleanup_logs`

**Authentication:** Admin password required (Bearer token)

**Response:**
```json
{
    "success": true,
    "message": "Log cleanup completed successfully",
    "timestamp": "2025-08-04T03:17:33+00:00",
    "data": {
        "message": "Log cleanup completed successfully",
        "current_log_size_mb": 2.5,
        "backup_files_count": 3,
        "total_log_size_mb": 15.2,
        "retention_days": 30,
        "max_size_mb": 100
    }
}
```

**Business Logic:**
1. Authenticate admin password
2. Rotate current log file if > 100MB
3. Remove backup files older than 30 days
4. Calculate and return log statistics
5. Log cleanup operation

## Authentication System

### API Key Authentication
- **Header:** `Authorization: Bearer {api_key}`
- **Validation:** Compare with stored API key
- **Required for:** `/inbox`, `/outbox` endpoints
- **Rate limiting:** Per API key

### Admin Password Authentication
- **Header:** `Authorization: Bearer {admin_password}`
- **Validation:** Compare with stored admin key
- **Required for:** All admin endpoints
- **Rate limiting:** Per IP address

### Authentication Flow
1. Extract Bearer token from Authorization header
2. Remove "Bearer " prefix
3. Compare token with appropriate key (API or admin)
4. Return 401 Unauthorized if invalid
5. Log unauthorized access attempts

## Rate Limiting System

### Implementation Details
- **Window:** 1 hour (3600 seconds)
- **Storage:** SQLite database table `rate_limits`
- **Cleanup:** Old entries automatically removed
- **Per-endpoint limits:** Different limits for different endpoints
- **Per-IP limits:** Overall request limits per IP

### Rate Limit Check Process
1. Get client IP address
2. Calculate window start time (current_time - 3600)
3. Clean up old rate limit entries
4. Count requests in current window for IP + endpoint
5. Check against endpoint-specific limit
6. Add current request to tracking
7. Return 429 if limit exceeded

### Rate Limit Response
```json
{
    "success": false,
    "error": "Rate limit exceeded",
    "code": 429,
    "retry_after": 3600,
    "timestamp": "2025-08-04T03:17:33+00:00"
}
```

## Session Management

### Session ID Format
- **Pattern:** `session_{timestamp}_{random_string}`
- **Example:** `session_mdwj6vj5_okiiczierw`
- **Validation:** Must match regex pattern
- **Length:** Maximum 64 characters

### Session Lifecycle
1. **Creation:** Automatic when first message received
2. **Activity:** Updated on each message/response
3. **Timeout:** 30 minutes of inactivity
4. **Cleanup:** Automatic (10% chance per API call)

### UID System
- **Format:** 16-character hexadecimal string
- **Example:** `2632f72d266e529c`
- **Generation:** Cryptographically secure random bytes
- **Persistence:** Remains consistent across sessions for same user
- **Storage:** Stored in `web_chat_sessions.uid`

### Session Cleanup Process
1. **Trigger:** 10% probability on each API call
2. **Criteria:** Sessions inactive for > 30 minutes
3. **Process:** Delete inactive sessions and associated data
4. **Logging:** Record cleanup operations

## Input Validation

### Session ID Validation
```python
def validate_session_id(session_id: str) -> bool:
    # Must match pattern: session_[timestamp]_[random]
    pattern = r'^session_[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, session_id)) and len(session_id) <= 64
```

### Message Validation
```python
def validate_message(message: str) -> bool:
    return (
        isinstance(message, str) and
        len(message) >= MIN_MESSAGE_LENGTH and
        len(message) <= MAX_MESSAGE_LENGTH and
        message.strip() != ''
    )
```

### UID Validation
```python
def validate_uid(uid: str) -> bool:
    # Must be exactly 16 hex characters
    pattern = r'^[a-f0-9]{16}$'
    return bool(re.match(pattern, uid))
```

## Database Operations

### Connection Management
```python
def get_db_connection():
    # Return SQLite connection with proper configuration
    # Handle connection pooling if needed
    # Set timeout and other SQLite options
```

### Transaction Handling
- **Use transactions** for multi-table operations
- **Rollback on errors** to maintain data consistency
- **Handle SQLite-specific constraints** (foreign keys, etc.)

### Query Optimization
- **Use prepared statements** for all queries
- **Index on frequently queried fields:**
  - `web_chat_sessions.last_active`
  - `web_chat_messages.processed`
  - `web_chat_messages.session_id`
  - `web_chat_responses.session_id`
  - `rate_limits.ip_address, endpoint, window_start`

## Logging System

### Log Levels
- **DEBUG:** Detailed debugging information
- **INFO:** General information messages
- **WARNING:** Warning conditions
- **ERROR:** Error conditions

### Log Format
```
[2025-08-04 03:17:33] [INFO] Message description {"context": "data"}
```

### Log Rotation
- **Size limit:** 100MB per file
- **Backup retention:** 30 days
- **Backup count:** Maximum 3 files
- **Automatic pruning:** 1% chance on each log write

### Log Content
- **API requests:** Endpoint, method, status, timing
- **Authentication:** Success/failure, IP address
- **Rate limiting:** Exceeded limits, IP addresses
- **Database operations:** Errors, cleanup operations
- **Admin actions:** Configuration changes, data clearing

## Error Handling

### HTTP Status Codes
- **200 OK:** Request successful
- **400 Bad Request:** Invalid request parameters
- **401 Unauthorized:** Missing or invalid authentication
- **404 Not Found:** Resource not found
- **405 Method Not Allowed:** Invalid HTTP method
- **429 Too Many Requests:** Rate limit exceeded
- **500 Internal Server Error:** Server error

### Error Response Format
```json
{
    "success": false,
    "error": "Error description",
    "code": 400,
    "timestamp": "2025-08-04T03:17:33+00:00"
}
```

### Error Logging
- **Log all errors** with context information
- **Include stack traces** for debugging
- **Record client information** (IP, user agent, etc.)
- **Track error frequency** for monitoring

## CORS Configuration

### Headers
```python
# Set CORS headers for all responses
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400'  # 24 hours
}
```

### Preflight Handling
- **Handle OPTIONS requests** for CORS preflight
- **Return 200 status** for preflight requests
- **Include appropriate headers** in preflight response

## Security Considerations

### Input Sanitization
- **Sanitize all user inputs** before database operations
- **Use parameterized queries** to prevent SQL injection
- **Validate data types** and formats
- **Escape HTML output** in admin interface

### Authentication Security
- **Store keys securely** (environment variables preferred)
- **Use strong key generation** for new keys
- **Log authentication attempts** for monitoring
- **Implement key rotation** procedures

### Rate Limiting Security
- **Prevent rate limit bypass** attempts
- **Log rate limit violations** for analysis
- **Implement progressive delays** for repeated violations

## Performance Considerations

### Database Optimization
- **Use appropriate indexes** on frequently queried fields
- **Implement connection pooling** if needed
- **Optimize query patterns** for common operations
- **Monitor query performance** and optimize slow queries

### Caching Strategy
- **Cache session data** for active sessions
- **Cache configuration values** to reduce file reads
- **Implement response caching** for static data
- **Use Redis/Memcached** for distributed caching if needed

### Async Operations
- **Use async/await** for I/O operations
- **Implement background tasks** for cleanup operations
- **Handle concurrent requests** efficiently
- **Use connection pooling** for database connections

## Testing Requirements

### Unit Tests
- **Test all validation functions** with various inputs
- **Test database operations** with mock data
- **Test authentication logic** with valid/invalid credentials
- **Test rate limiting** with various scenarios

### Integration Tests
- **Test complete API workflows** end-to-end
- **Test database schema** and relationships
- **Test error handling** and edge cases
- **Test authentication flows** completely

### Performance Tests
- **Test rate limiting** under load
- **Test database performance** with large datasets
- **Test concurrent request handling**
- **Test memory usage** under various conditions

## Deployment Considerations

### Environment Variables
```bash
WEB_CHAT_API_KEY=your_api_key_here
WEB_CHAT_ADMIN_KEY=your_admin_key_here
WEB_CHAT_DEBUG=false
WEB_CHAT_DATABASE_PATH=/path/to/database.db
WEB_CHAT_LOG_PATH=/path/to/logs/
```

### File Permissions
- **Database file:** Read/write for application user
- **Log directory:** Write access for application user
- **Configuration files:** Read access for application user

### Process Management
- **Use process manager** (systemd, supervisor, etc.)
- **Implement health checks** for monitoring
- **Handle graceful shutdowns** for database connections
- **Implement automatic restarts** on failures

## Monitoring and Maintenance

### Health Checks
- **Database connectivity** verification
- **API endpoint availability** testing
- **Rate limiting status** monitoring
- **Session cleanup** status tracking

### Metrics Collection
- **Request counts** per endpoint
- **Response times** for API calls
- **Error rates** and types
- **Database performance** metrics

### Maintenance Tasks
- **Regular database cleanup** of old data
- **Log file rotation** and archiving
- **Configuration backup** and versioning
- **Security updates** and patches

## Migration Notes

### Data Preservation
- **Export existing data** from `php/db/web_chat.db` before migration
- **Verify data integrity** after migration
- **Test all functionality** with real data
- **Plan rollback strategy** if issues arise

### Configuration Migration
- **Transfer API keys** and admin passwords from `php/public/config/settings.php`
- **Update environment variables** in new system
- **Verify rate limiting** settings match
- **Test authentication** with existing keys

### File Structure Changes
- **Original PHP system** is now located in the `php/` folder
- **Database file** moved from `db/web_chat.db` to `php/db/web_chat.db`
- **Configuration files** moved from `public/config/` to `php/public/config/`
- **Admin interface** moved from `public/web/` to `php/public/web/`
- **API endpoints** moved from `public/api/` to `php/public/api/`

### Testing Strategy
- **Run both systems** in parallel initially
- **Compare responses** for identical inputs
- **Monitor performance** differences
- **Validate all edge cases** and error conditions

This specification provides complete technical details for recreating the PHP system in Flask while maintaining 100% functional parity. The development team should implement each component exactly as specified to ensure compatibility with existing clients and plugins.
