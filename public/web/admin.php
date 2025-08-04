<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Chat Admin</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .admin-container {
            max-width: 1200px;
            margin: 2rem auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }
        
        .admin-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        .admin-header h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 600;
        }
        
        .admin-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        
        .stats-section {
            padding: 2rem;
            background: #f8f9fa;
        }
        
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
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #6c757d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .sessions-section {
            padding: 2rem;
        }
        
        .session-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.2s;
        }
        
        .session-card:hover {
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transform: translateY(-1px);
        }
        
        .session-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .session-id {
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            color: #667eea;
            font-weight: 600;
        }
        
        .session-time {
            font-size: 0.8rem;
            color: #6c757d;
        }
        
        .session-stats {
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }
        
        .session-stat {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .session-stat-label {
            color: #6c757d;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.25rem;
        }
        
        .session-stat-value {
            font-weight: bold;
            color: #333;
            font-size: 1.1rem;
        }
        
        .btn-refresh {
            background: #667eea;
            border: none;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 2rem;
            font-weight: 500;
            transition: all 0.2s;
            margin-bottom: 1.5rem;
        }
        
        .btn-refresh:hover {
            background: #5a6fd8;
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
        }
        
        .loading-spinner {
            text-align: center;
            padding: 3rem;
            color: #6c757d;
        }
        
        .error-alert {
            margin: 1rem 0;
        }
        
        .no-sessions {
            text-align: center;
            padding: 3rem;
            color: #6c757d;
        }
        
        .no-sessions i {
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .admin-container {
                margin: 1rem;
                border-radius: 10px;
            }
            
            .admin-header {
                padding: 1.5rem;
            }
            
            .admin-header h1 {
                font-size: 1.5rem;
            }
            
            .stats-section,
            .sessions-section {
                padding: 1rem;
            }
            
                    .session-stats {
            gap: 1rem;
        }
        
                         .config-section {
            background: white;
        }
        
        .config-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .config-card h4 {
            color: #667eea;
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }
        
        .config-card .btn {
            margin-right: 0.5rem;
        }
        
                 .config-card .text-muted {
             font-size: 0.8rem;
         }
         
         /* Tab Navigation Styles */
         .nav-section {
             background: white;
             border-bottom: 1px solid #e9ecef;
         }
         
         .nav-tabs {
             border-bottom: none;
             padding: 0 2rem;
         }
         
         .nav-tabs .nav-link {
             border: none;
             border-radius: 0;
             color: #6c757d;
             font-weight: 500;
             padding: 1rem 1.5rem;
             transition: all 0.2s;
             position: relative;
         }
         
         .nav-tabs .nav-link:hover {
             color: #667eea;
             background: rgba(102, 126, 234, 0.05);
             border: none;
         }
         
         .nav-tabs .nav-link.active {
             color: #667eea;
             background: white;
             border: none;
             border-bottom: 3px solid #667eea;
             transform: translateY(-1px);
         }
         
         .nav-tabs .nav-link i {
             margin-right: 0.5rem;
         }
         
         .tab-content {
             background: white;
         }
         
         .tab-pane {
             padding: 2rem;
         }
         
         /* Table styles for ledger display */
         .table {
             font-size: 0.9rem;
         }
         
         .table th {
             font-weight: 600;
             color: #667eea;
             border-bottom: 2px solid #e9ecef;
         }
         
         .table td {
             vertical-align: middle;
             padding: 0.75rem 0.5rem;
         }
         
         .table tbody tr:hover {
             background-color: rgba(102, 126, 234, 0.05);
         }
         
         .badge {
             font-size: 0.75rem;
             padding: 0.25rem 0.5rem;
         }
         
         /* Session History Modal Styles */
         .session-messages {
             max-height: 400px;
             overflow-y: auto;
             border: 1px solid #e9ecef;
             border-radius: 8px;
             padding: 1rem;
             background: #f8f9fa;
         }
         
         .message-item {
             margin-bottom: 1rem;
             padding: 0.75rem;
             border-radius: 8px;
             background: white;
             border-left: 4px solid #667eea;
         }
         
         .message-item.user {
             border-left-color: #28a745;
             background: #f8fff9;
         }
         
         .message-item.agent {
             border-left-color: #667eea;
             background: #f8f9ff;
         }
         
         .message-header {
             display: flex;
             justify-content: space-between;
             align-items: center;
             margin-bottom: 0.5rem;
             font-size: 0.8rem;
             color: #6c757d;
         }
         
         .message-sender {
             font-weight: 600;
             text-transform: capitalize;
         }
         
         .message-time {
             font-size: 0.75rem;
         }
         
         .message-content {
             font-size: 0.9rem;
             line-height: 1.4;
             word-wrap: break-word;
         }
         
         /* Clickable session ID styling */
         .session-id-clickable {
             cursor: pointer;
             transition: color 0.2s;
         }
         
         .session-id-clickable:hover {
             color: #5a6fd8 !important;
             text-decoration: underline;
         }
         
         /* Mobile table adjustments */
         @media (max-width: 768px) {
             .table {
                 font-size: 0.8rem;
             }
             
             .table td, .table th {
                 padding: 0.5rem 0.25rem;
             }
             
             .badge {
                 font-size: 0.7rem;
                 padding: 0.2rem 0.4rem;
             }
         }
         
         /* Mobile responsiveness for tabs */
         @media (max-width: 768px) {
             .nav-tabs {
                 padding: 0 1rem;
             }
             
             .nav-tabs .nav-link {
                 padding: 0.75rem 1rem;
                 font-size: 0.9rem;
             }
             
             .tab-pane {
                 padding: 1rem;
             }
         }
     }
     </style>
</head>
<body>
    <div class="container-fluid">
        <div class="admin-container">
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
            
            <!-- Navigation Tabs -->
            <div class="nav-section">
                <ul class="nav nav-tabs" id="adminTabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="overview-tab" data-bs-toggle="tab" data-bs-target="#overview" type="button" role="tab" aria-controls="overview" aria-selected="true">
                            <i class="bi bi-speedometer2"></i> Overview
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="sessions-tab" data-bs-toggle="tab" data-bs-target="#sessions" type="button" role="tab" aria-controls="sessions" aria-selected="false">
                            <i class="bi bi-people"></i> Sessions
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="config-tab" data-bs-toggle="tab" data-bs-target="#config" type="button" role="tab" aria-controls="config" aria-selected="false">
                            <i class="bi bi-gear"></i> Configuration
                        </button>
                    </li>
                </ul>
            </div>
            
            <!-- Tab Content -->
            <div class="tab-content" id="adminTabContent">
                <!-- Overview Tab -->
                <div class="tab-pane fade show active" id="overview" role="tabpanel" aria-labelledby="overview-tab">
                    <div class="stats-section">
                        <div class="row" id="stats">
                            <div class="col-md-3 col-sm-6 mb-3">
                                <div class="stat-card">
                                    <div class="stat-number" id="active-sessions">-</div>
                                    <div class="stat-label">Active Sessions</div>
                                </div>
                            </div>
                            <div class="col-md-3 col-sm-6 mb-3">
                                <div class="stat-card">
                                    <div class="stat-number" id="total-messages">-</div>
                                    <div class="stat-label">Total Messages</div>
                                </div>
                            </div>
                            <div class="col-md-3 col-sm-6 mb-3">
                                <div class="stat-card">
                                    <div class="stat-number" id="total-responses">-</div>
                                    <div class="stat-label">Total Responses</div>
                                </div>
                            </div>
                            <div class="col-md-3 col-sm-6 mb-3">
                                <div class="stat-card">
                                    <div class="stat-number" id="avg-response-time">-</div>
                                    <div class="stat-label">Avg Response Time</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Sessions Tab -->
                <div class="tab-pane fade" id="sessions" role="tabpanel" aria-labelledby="sessions-tab">
                    <div class="sessions-section">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h2 class="mb-0"><i class="bi bi-people"></i> Active Sessions</h2>
                            <button class="btn btn-refresh" onclick="loadSessions()">
                                <i class="bi bi-arrow-clockwise"></i> Refresh
                            </button>
                        </div>
                        <div id="session-list">
                            <div class="loading-spinner">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <p class="mt-2">Loading sessions...</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Configuration Tab -->
                <div class="tab-pane fade" id="config" role="tabpanel" aria-labelledby="config-tab">
                    <div class="config-section">
                        <h2 class="mb-3"><i class="bi bi-gear"></i> Configuration</h2>
                        <div class="row">
                            <div class="col-md-6">
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
                            </div>
                            <div class="col-md-6">
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
                            </div>
                        </div>
                    </div>
                </div>
            </div>
                 </div>
     </div>
     
     <!-- Session History Modal -->
     <div class="modal fade" id="sessionHistoryModal" tabindex="-1" aria-labelledby="sessionHistoryModalLabel" aria-hidden="true">
         <div class="modal-dialog modal-lg">
             <div class="modal-content">
                 <div class="modal-header">
                     <h5 class="modal-title" id="sessionHistoryModalLabel">
                         <i class="bi bi-chat-dots"></i> Session History
                     </h5>
                     <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
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
                         <div class="text-center text-muted">
                             <div class="spinner-border spinner-border-sm" role="status">
                                 <span class="visually-hidden">Loading...</span>
                             </div>
                             <p class="mt-2">Loading messages...</p>
                         </div>
                     </div>
                 </div>
                 <div class="modal-footer">
                     <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                 </div>
             </div>
         </div>
     </div>
 
     <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
                 // Get admin password from localStorage or prompt user
         let adminKey = localStorage.getItem('web_chat_admin_key');
         if (!adminKey) {
             adminKey = prompt('Enter admin password:');
             if (!adminKey) {
                 alert('Admin password required');
                 window.close();
             } else {
                 // Store the password for future use
                 localStorage.setItem('web_chat_admin_key', adminKey);
             }
         }
        
        async function loadSessions() {
            try {
                const response = await fetch('/api/v1/index.php?action=sessions&limit=50', {
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
        
        function updateStats(data) {
            const sessions = data.sessions;
            const totalMessages = sessions.reduce((sum, session) => sum + session.message_count, 0);
            const totalResponses = sessions.reduce((sum, session) => sum + session.response_count, 0);
            
            document.getElementById('active-sessions').textContent = sessions.length;
            document.getElementById('total-messages').textContent = totalMessages;
            document.getElementById('total-responses').textContent = totalResponses;
            document.getElementById('avg-response-time').textContent = 'N/A'; // Would need more data
        }
        
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
        
        // Load sessions on page load
        document.addEventListener('DOMContentLoaded', loadSessions);
        
        // Auto-refresh every 30 seconds
        setInterval(loadSessions, 30000);
        
        // Configuration functions
        function generateApiKey() {
            const key = 'api_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
            document.getElementById('api-key').value = key;
        }
        
                 function generateAdminKey() {
             const password = 'admin_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
             document.getElementById('admin-key').value = password;
         }
        
                 async function updateKeys() {
             const apiKey = document.getElementById('api-key').value;
             const adminPassword = document.getElementById('admin-key').value;
             
             if (!apiKey || !adminPassword) {
                 alert('Please enter both API key and admin password');
                 return;
             }
            
            try {
                const response = await fetch('/api/v1/index.php?action=config', {
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
        
        async function manualCleanup() {
            if (!confirm('Are you sure you want to clean up inactive sessions?')) {
                return;
            }
            
            try {
                const response = await fetch('/api/v1/index.php?action=cleanup', {
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
        
        async function cleanupLogs() {
            if (!confirm('This will rotate the current log file and remove old log files older than 30 days. Continue?')) {
                return;
            }
            
            try {
                const response = await fetch('/api/v1/index.php?action=cleanup_logs', {
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
        
        async function clearAllData() {
            if (!confirm('⚠️ WARNING: This will delete ALL sessions, messages, and responses. This action cannot be undone. Are you absolutely sure?')) {
                return;
            }
            
            if (!confirm('Are you REALLY sure? This will permanently delete all data.')) {
                return;
            }
            
            try {
                const response = await fetch('/api/v1/index.php?action=clear_data', {
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
        
        // Load current configuration on page load
        async function loadConfig() {
            try {
                const response = await fetch('/api/v1/index.php?action=config', {
                    headers: {
                        'Authorization': `Bearer ${adminKey}`
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        document.getElementById('session-timeout').value = Math.floor(data.data.session_timeout / 60);
                        
                        // Populate current keys (masked for security)
                        const apiKeyField = document.getElementById('api-key');
                        const adminKeyField = document.getElementById('admin-key');
                        
                        if (data.data.api_key) {
                            apiKeyField.value = data.data.api_key;
                        }
                        if (data.data.admin_key) {
                            adminKeyField.value = data.data.admin_key;
                        }
                    }
                }
            } catch (error) {
                console.error('Failed to load configuration:', error);
            }
        }
        
        // Load configuration on page load
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
        
        // Logout function
                 function logout() {
             if (confirm('Are you sure you want to logout? You will need to enter the admin password again.')) {
                 localStorage.removeItem('web_chat_admin_key');
                 alert('Logged out successfully. Please refresh the page to login again.');
             }
         }
        
                 // Update stored key when admin key is changed
         function updateStoredAdminKey(newKey) {
             localStorage.setItem('web_chat_admin_key', newKey);
             adminKey = newKey;
         }
         
         // Toggle password visibility
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
         
         // View session history
         async function viewSessionHistory(sessionId) {
             // Update modal header
             document.getElementById('modal-session-id').textContent = sessionId;
             
             // Show modal
             const modal = new bootstrap.Modal(document.getElementById('sessionHistoryModal'));
             modal.show();
             
             try {
                 // Fetch session messages
                 const response = await fetch(`/api/v1/index.php?action=session_messages&session_id=${sessionId}`, {
                     headers: {
                         'Authorization': `Bearer ${adminKey}`
                     }
                 });
                 
                 if (!response.ok) {
                     throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                 }
                 
                 const data = await response.json();
                 
                 if (data.success) {
                     displaySessionHistory(data.data);
                 } else {
                     throw new Error(data.error || 'Failed to load session history');
                 }
                 
             } catch (error) {
                 console.error('Failed to load session history:', error);
                 document.getElementById('session-messages').innerHTML = 
                     `<div class="alert alert-danger" role="alert">
                         <i class="bi bi-exclamation-triangle"></i> Failed to load session history: ${error.message}
                     </div>`;
             }
         }
         
         // Display session history in modal
         function displaySessionHistory(data) {
             const messagesContainer = document.getElementById('session-messages');
             
             // Update session info
             if (data.session) {
                 document.getElementById('modal-created-time').textContent = formatTime(data.session.created_at);
                 document.getElementById('modal-last-active').textContent = formatTime(data.session.last_active);
             }
             
             if (!data.messages || data.messages.length === 0) {
                 messagesContainer.innerHTML = `
                     <div class="text-center text-muted">
                         <i class="bi bi-chat-dots" style="font-size: 2rem;"></i>
                         <p class="mt-2">No messages found for this session</p>
                     </div>
                 `;
                 return;
             }
             
             // Sort messages by timestamp
             const sortedMessages = data.messages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
             
             // Display messages
             messagesContainer.innerHTML = sortedMessages.map(message => `
                 <div class="message-item user">
                     <div class="message-header">
                         <span class="message-sender">
                             <i class="bi bi-person-circle"></i> User
                         </span>
                         <span class="message-time">${formatTime(message.timestamp)}</span>
                     </div>
                     <div class="message-content">${escapeHtml(message.message)}</div>
                 </div>
             `).join('');
             
             // Add responses if available
             if (data.responses && data.responses.length > 0) {
                 const sortedResponses = data.responses.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
                 
                 sortedResponses.forEach(response => {
                     const responseElement = document.createElement('div');
                     responseElement.className = 'message-item agent';
                     responseElement.innerHTML = `
                         <div class="message-header">
                             <span class="message-sender">
                                 <i class="bi bi-robot"></i> Agent
                             </span>
                             <span class="message-time">${formatTime(response.timestamp)}</span>
                         </div>
                         <div class="message-content">${escapeHtml(response.response)}</div>
                     `;
                     messagesContainer.appendChild(responseElement);
                 });
             }
             
             // Scroll to bottom
             messagesContainer.scrollTop = messagesContainer.scrollHeight;
         }
         
         // Escape HTML to prevent XSS
         function escapeHtml(text) {
             const div = document.createElement('div');
             div.textContent = text;
             return div.innerHTML;
         }
    </script>
</body>
</html> 