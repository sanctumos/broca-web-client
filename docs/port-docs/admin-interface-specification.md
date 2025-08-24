# Admin Interface Specification - Flask Port Requirements

## Overview

This document specifies the exact admin interface functionality that must be implemented in the Flask port. The admin interface provides comprehensive monitoring and management capabilities for the Web Chat Bridge system.

## Admin Interface Structure

### Base URL
- **Path:** `/admin` (Flask route)
- **Authentication:** Admin password required (stored in browser localStorage)
- **Access Control:** Same-origin requests only

### Authentication Flow
1. **Initial Access:** Prompt for admin password if not stored
2. **Storage:** Store password in `localStorage['web_chat_admin_key']`
3. **Validation:** Use stored password for all API requests
4. **Logout:** Clear stored password and require re-entry

## Page Layout and Navigation

### Header Section
```html
<div class="admin-header">
    <h1><i class="bi bi-gear"></i> Web Chat Admin</h1>
    <p>Monitor active sessions and system status</p>
    <div class="mt-3">
        <small class="text-light">
            <i class="bi bi-clock"></i> Sessions timeout after 30 minutes of inactivity
        </small>
        <div class="mt-2">
            <small class="text-light">
                <i class="bi bi-key"></i> Admin password stored in browser
            </small>
            <button class="btn btn-sm btn-outline-light ms-2" onclick="logout()">
                <i class="bi bi-box-arrow-right"></i> Logout
            </button>
        </div>
    </div>
</div>
```

### Tab Navigation
```html
<ul class="nav nav-tabs" id="adminTabs" role="tablist">
    <li class="nav-item" role="presentation">
        <button class="nav-link active" id="overview-tab" data-bs-toggle="tab" data-bs-target="#overview">
            <i class="bi bi-speedometer2"></i> Overview
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="sessions-tab" data-bs-toggle="tab" data-bs-target="#sessions">
            <i class="bi bi-people"></i> Sessions
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="config-tab" data-bs-toggle="tab" data-bs-target="#config">
            <i class="bi bi-gear"></i> Configuration
        </button>
    </li>
</ul>
```

## Tab 1: Overview

### Statistics Cards
Display real-time system statistics in a 4-column grid:

#### Active Sessions Card
```html
<div class="stat-card">
    <div class="stat-number" id="active-sessions">-</div>
    <div class="stat-label">Active Sessions</div>
</div>
```

#### Total Messages Card
```html
<div class="stat-card">
    <div class="stat-number" id="total-messages">-</div>
    <div class="stat-label">Total Messages</div>
</div>
```

#### Total Responses Card
```html
<div class="stat-card">
    <div class="stat-number" id="total-responses">-</div>
    <div class="stat-label">Total Responses</div>
</div>
```

#### Average Response Time Card
```html
<div class="stat-card">
    <div class="stat-number" id="avg-response-time">-</div>
    <div class="stat-label">Avg Response Time</div>
</div>
```

### Statistics Calculation Logic
```javascript
function updateStats(data) {
    const sessions = data.sessions;
    const totalMessages = sessions.reduce((sum, session) => sum + session.message_count, 0);
    const totalResponses = sessions.reduce((sum, session) => sum + session.response_count, 0);
    
    document.getElementById('active-sessions').textContent = sessions.length;
    document.getElementById('total-messages').textContent = totalMessages;
    document.getElementById('total-responses').textContent = totalResponses;
    document.getElementById('avg-response-time').textContent = 'N/A'; // Would need more data
}
```

## Tab 2: Sessions

### Sessions Header
```html
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2 class="mb-0"><i class="bi bi-people"></i> Active Sessions</h2>
    <button class="btn btn-refresh" onclick="loadSessions()">
        <i class="bi bi-arrow-clockwise"></i> Refresh
    </button>
</div>
```

### Sessions Table
Display active sessions in a ledger-style table:

```html
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th><i class="bi bi-person-circle"></i> Session ID</th>
                <th><i class="bi bi-chat"></i> Messages</th>
                <th><i class="bi bi-reply"></i> Responses</th>
                <th><i class="bi bi-calendar-plus"></i> Created</th>
                <th><i class="bi bi-clock"></i> Last Active</th>
            </tr>
        </thead>
        <tbody>
            <!-- Dynamic content -->
        </tbody>
    </table>
</div>
```

### Session Row Format
```html
<tr>
    <td>
        <code class="text-primary session-id-clickable" onclick="viewSessionHistory('${session.id}')">${session.id}</code>
    </td>
    <td>
        <span class="badge bg-primary">${session.message_count}</span>
    </td>
    <td>
        <span class="badge bg-success">${session.response_count}</span>
    </td>
    <td>
        <small class="text-muted">${formatTime(session.created_at)}</small>
    </td>
    <td>
        <small class="text-muted">${formatTime(session.last_active)}</small>
    </td>
</tr>
```

### Session History Modal
Clicking on a session ID opens a modal showing complete conversation history:

```html
<div class="modal fade" id="sessionHistoryModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="bi bi-chat-dots"></i> Session History
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="mb-3">
                    <strong>Session ID:</strong> <code id="modal-session-id"></code>
                </div>
                <div class="mb-3">
                    <strong>Created:</strong> <span id="modal-created-time"></span>
                </div>
                <div class="mb-3">
                    <strong>Last Active:</strong> <span id="modal-last-active"></span>
                </div>
                <hr>
                <div id="session-messages" class="session-messages">
                    <!-- Dynamic content -->
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        </div>
    </div>
</div>
```

### Message Display Format
```html
<!-- User Message -->
<div class="message-item user">
    <div class="message-header">
        <span class="message-sender">
            <i class="bi bi-person-circle"></i> User
        </span>
        <span class="message-time">${formatTime(message.timestamp)}</span>
    </div>
    <div class="message-content">${escapeHtml(message.message)}</div>
</div>

<!-- Agent Response -->
<div class="message-item agent">
    <div class="message-header">
        <span class="message-sender">
            <i class="bi bi-robot"></i> Agent
        </span>
        <span class="message-time">${formatTime(response.timestamp)}</span>
    </div>
    <div class="message-content">${escapeHtml(response.response)}</div>
</div>
```

## Tab 3: Configuration

### API Keys Section
```html
<div class="config-card">
    <h4><i class="bi bi-key"></i> API Keys</h4>
    <div class="mb-3">
        <label class="form-label">API Key</label>
        <div class="input-group">
            <input type="password" class="form-control" id="api-key" placeholder="Current API key">
            <button class="btn btn-outline-secondary" type="button" onclick="togglePasswordVisibility('api-key')">
                <i class="bi bi-eye" id="api-key-eye"></i>
            </button>
            <button class="btn btn-outline-secondary" type="button" onclick="generateApiKey()">
                <i class="bi bi-arrow-clockwise"></i> Generate
            </button>
        </div>
    </div>
    <div class="mb-3">
        <label class="form-label">Admin Password</label>
        <div class="input-group">
            <input type="password" class="form-control" id="admin-key" placeholder="Enter admin password">
            <button class="btn btn-outline-secondary" type="button" onclick="togglePasswordVisibility('admin-key')">
                <i class="bi bi-eye" id="admin-key-eye"></i>
            </button>
            <button class="btn btn-outline-secondary" type="button" onclick="generateAdminKey()">
                <i class="bi bi-arrow-clockwise"></i> Generate
            </button>
        </div>
        <small class="text-muted">Type your own password or click "Generate" for a random one</small>
    </div>
    <button class="btn btn-primary" onclick="updateKeys()">
        <i class="bi bi-check"></i> Update Keys
    </button>
</div>
```

### Maintenance Section
```html
<div class="config-card">
    <h4><i class="bi bi-trash"></i> Maintenance</h4>
    <div class="mb-3">
        <label class="form-label">Session Timeout (minutes)</label>
        <input type="number" class="form-control" id="session-timeout" min="1" max="1440" value="30">
    </div>
    <div class="mb-3">
        <button class="btn btn-warning" onclick="manualCleanup()">
            <i class="bi bi-broom"></i> Manual Cleanup
        </button>
        <small class="text-muted d-block mt-1">Remove inactive sessions</small>
    </div>
    <div class="mb-3">
        <button class="btn btn-info" onclick="cleanupLogs()">
            <i class="bi bi-file-earmark-text"></i> Cleanup Logs
        </button>
        <small class="text-muted d-block mt-1">Rotate and prune old log files</small>
    </div>
    <div class="mb-3">
        <button class="btn btn-danger" onclick="clearAllData()">
            <i class="bi bi-exclamation-triangle"></i> Clear All Data
        </button>
        <small class="text-muted d-block mt-1">⚠️ This will delete all sessions, messages, and responses</small>
    </div>
</div>
```

## JavaScript Functions

### Core Functions

#### Load Sessions
```javascript
async function loadSessions() {
    try {
        const response = await fetch('/api/v1/?action=sessions&limit=50', {
            headers: {
                'Authorization': `Bearer ${adminKey}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            updateStats(data.data);
            updateSessionList(data.data.sessions);
        } else {
            throw new Error(data.error || 'Failed to load sessions');
        }
        
    } catch (error) {
        console.error('Failed to load sessions:', error);
        document.getElementById('session-list').innerHTML = 
            `<div class="alert alert-danger error-alert" role="alert">
                <i class="bi bi-exclamation-triangle"></i> Failed to load sessions: ${error.message}
            </div>`;
    }
}
```

#### Update Session List
```javascript
function updateSessionList(sessions) {
    const sessionList = document.getElementById('session-list');
    
    if (sessions.length === 0) {
        sessionList.innerHTML = `
            <div class="no-sessions">
                <i class="bi bi-chat-dots"></i>
                <h4>No Active Sessions</h4>
                <p class="text-muted">No active chat sessions found</p>
            </div>
        `;
        return;
    }
    
    // Create ledger-style table
    sessionList.innerHTML = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead class="table-light">
                    <tr>
                        <th><i class="bi bi-person-circle"></i> Session ID</th>
                        <th><i class="bi bi-chat"></i> Messages</th>
                        <th><i class="bi bi-reply"></i> Responses</th>
                        <th><i class="bi bi-calendar-plus"></i> Created</th>
                        <th><i class="bi bi-clock"></i> Last Active</th>
                    </tr>
                </thead>
                <tbody>
                    ${sessions.map(session => `
                        <tr>
                            <td>
                                <code class="text-primary session-id-clickable" onclick="viewSessionHistory('${session.id}')">${session.id}</code>
                            </td>
                            <td>
                                <span class="badge bg-primary">${session.message_count}</span>
                            </td>
                            <td>
                                <span class="badge bg-success">${session.response_count}</span>
                            </td>
                            <td>
                                <small class="text-muted">${formatTime(session.created_at)}</small>
                            </td>
                            <td>
                                <small class="text-muted">${formatTime(session.last_active)}</small>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}
```

#### Time Formatting
```javascript
function formatTime(timestamp) {
    // Handle SQLite datetime format (YYYY-MM-DD HH:MM:SS)
    let date;
    if (typeof timestamp === 'string' && timestamp.match(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/)) {
        // Convert SQLite datetime to ISO format for proper parsing
        date = new Date(timestamp.replace(' ', 'T') + 'Z');
    } else {
        date = new Date(timestamp);
    }
    
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) { // Less than 1 minute
        return 'Just now';
    } else if (diff < 3600000) { // Less than 1 hour
        const minutes = Math.floor(diff / 60000);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (diff < 86400000) { // Less than 1 day
        const hours = Math.floor(diff / 3600000);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
}
```

### Configuration Functions

#### Generate API Key
```javascript
function generateApiKey() {
    const key = 'api_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    document.getElementById('api-key').value = key;
}
```

#### Generate Admin Key
```javascript
function generateAdminKey() {
    const password = 'admin_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    document.getElementById('admin-key').value = password;
}
```

#### Update Keys
```javascript
async function updateKeys() {
    const apiKey = document.getElementById('api-key').value;
    const adminPassword = document.getElementById('admin-key').value;
    
    if (!apiKey || !adminPassword) {
        alert('Please enter both API key and admin password');
        return;
    }
    
    try {
        const response = await fetch('/api/v1/?action=config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminKey}`
            },
            body: JSON.stringify({
                api_key: apiKey,
                admin_key: adminPassword
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            alert('Keys updated successfully!');
            // Update the admin password for future requests
            const newAdminPassword = document.getElementById('admin-key').value;
            updateStoredAdminKey(newAdminPassword);
        } else {
            throw new Error(data.error || 'Failed to update keys');
        }
        
    } catch (error) {
        console.error('Failed to update keys:', error);
        alert('Failed to update keys: ' + error.message);
    }
}
```

### Maintenance Functions

#### Manual Cleanup
```javascript
async function manualCleanup() {
    if (!confirm('Are you sure you want to clean up inactive sessions?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/v1/?action=cleanup', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${adminKey}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Cleanup completed! ${data.data.cleaned_count} sessions removed.`);
            loadSessions(); // Refresh the session list
        } else {
            throw new Error(data.error || 'Failed to perform cleanup');
        }
        
    } catch (error) {
        console.error('Failed to perform cleanup:', error);
        alert('Failed to perform cleanup: ' + error.message);
    }
}
```

#### Cleanup Logs
```javascript
async function cleanupLogs() {
    if (!confirm('This will rotate the current log file and remove old log files older than 30 days. Continue?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/v1/?action=cleanup_logs', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${adminKey}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Log cleanup completed!\n\nCurrent log size: ${data.data.current_log_size_mb} MB\nBackup files: ${data.data.backup_files_count}\nTotal log size: ${data.data.total_log_size_mb} MB\nRetention: ${data.data.retention_days} days\nMax size: ${data.data.max_size_mb} MB`);
        } else {
            throw new Error(data.error || 'Failed to cleanup logs');
        }
        
    } catch (error) {
        console.error('Failed to cleanup logs:', error);
        alert('Failed to cleanup logs: ' + error.message);
    }
}
```

#### Clear All Data
```javascript
async function clearAllData() {
    if (!confirm('⚠️ WARNING: This will delete ALL sessions, messages, and responses. This action cannot be undone. Are you absolutely sure?')) {
        return;
    }
    
    if (!confirm('Are you REALLY sure? This will permanently delete all data.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/v1/?action=clear_data', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${adminKey}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            alert('All data cleared successfully!');
            loadSessions(); // Refresh the session list
        } else {
            throw new Error(data.error || 'Failed to clear data');
        }
        
    } catch (error) {
        console.error('Failed to clear data:', error);
        alert('Failed to clear data: ' + error.message);
    }
}
```

### Utility Functions

#### Toggle Password Visibility
```javascript
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const eyeIcon = document.getElementById(inputId + '-eye');
    
    if (input.type === 'password') {
        input.type = 'text';
        eyeIcon.className = 'bi bi-eye-slash';
    } else {
        input.type = 'password';
        eyeIcon.className = 'bi bi-eye';
    }
}
```

#### Escape HTML
```javascript
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

#### Logout
```javascript
function logout() {
    if (confirm('Are you sure you want to logout? You will need to enter the admin password again.')) {
        localStorage.removeItem('web_chat_admin_key');
        alert('Logged out successfully. Please refresh the page to login again.');
    }
}
```

## Auto-refresh and Event Handling

### Page Load Events
```javascript
document.addEventListener('DOMContentLoaded', function() {
    loadSessions();
    loadConfig();
    
    // Handle tab switching
    const sessionsTab = document.getElementById('sessions-tab');
    sessionsTab.addEventListener('click', function() {
        // Refresh sessions when switching to sessions tab
        setTimeout(() => {
            loadSessions();
        }, 100);
    });
    
    // Handle URL hash for tab navigation
    const hash = window.location.hash;
    if (hash) {
        const targetTab = document.querySelector(`[data-bs-target="${hash}"]`);
        if (targetTab) {
            const tab = new bootstrap.Tab(targetTab);
            tab.show();
        }
    }
    
    // Update URL hash when tabs are clicked
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            window.location.hash = e.target.getAttribute('data-bs-target');
        });
    });
});
```

### Auto-refresh Timer
```javascript
// Auto-refresh every 30 seconds
setInterval(loadSessions, 30000);
```

## CSS Styling Requirements

### Color Scheme
- **Primary:** `#667eea` (Blue)
- **Secondary:** `#764ba2` (Purple)
- **Success:** `#28a745` (Green)
- **Warning:** `#ffc107` (Yellow)
- **Danger:** `#dc3545` (Red)
- **Info:** `#17a2b8` (Cyan)

### Gradient Backgrounds
```css
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.admin-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### Card Styling
```css
.stat-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    text-align: center;
    transition: transform 0.2s;
}

.stat-card:hover {
    transform: translateY(-2px);
}
```

### Responsive Design
- **Mobile-first approach**
- **Breakpoint:** 768px for mobile adjustments
- **Flexible grid system** using Bootstrap classes
- **Touch-friendly buttons** and interactions

## Flask Implementation Notes

### Route Structure
```python
@app.route('/admin')
def admin_interface():
    # Return admin.html template
    
@app.route('/admin/api/sessions')
def admin_sessions():
    # Handle AJAX requests for session data
    
@app.route('/admin/api/config', methods=['GET', 'POST'])
def admin_config():
    # Handle configuration operations
```

### Template Rendering
- **Use Jinja2 templates** for dynamic content
- **Implement CSRF protection** for form submissions
- **Handle authentication** at the route level
- **Return JSON responses** for AJAX requests

### Static Assets
- **Serve Bootstrap CSS/JS** from CDN or local files
- **Include Bootstrap Icons** for consistent iconography
- **Minimize custom CSS** to maintain consistency
- **Optimize JavaScript** for performance

### Security Considerations
- **Validate admin authentication** on all admin routes
- **Sanitize user inputs** before database operations
- **Implement proper session management** for admin users
- **Log all admin actions** for audit purposes

This specification provides complete details for implementing the admin interface in Flask while maintaining 100% visual and functional parity with the current PHP version.
