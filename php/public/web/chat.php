<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Chat</title>
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
        
        .chat-container {
            max-width: 800px;
            margin: 2rem auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            text-align: center;
        }
        
        .chat-header h1 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .chat-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 0.9rem;
        }
        
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 1rem;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 1rem;
            display: flex;
            align-items: flex-start;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message.agent {
            justify-content: flex-start;
        }
        
        .message-content {
            max-width: 70%;
            padding: 0.75rem 1rem;
            border-radius: 1rem;
            position: relative;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 0.25rem;
        }
        
        .message.agent .message-content {
            background: white;
            color: #333;
            border: 1px solid #e9ecef;
            border-bottom-left-radius: 0.25rem;
        }
        
        .message-time {
            font-size: 0.75rem;
            opacity: 0.7;
            margin-top: 0.25rem;
            text-align: right;
        }
        
        .message.user .message-time {
            text-align: right;
        }
        
        .message.agent .message-time {
            text-align: left;
        }
        
        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.75rem 1rem;
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 1rem;
            border-bottom-left-radius: 0.25rem;
            max-width: 70%;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            background: #6c757d;
            border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }
        
        .chat-input {
            padding: 1rem;
            background: white;
            border-top: 1px solid #e9ecef;
        }
        
        .input-group {
            position: relative;
        }
        
        .form-control {
            border-radius: 2rem;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            font-size: 0.9rem;
            resize: none;
            min-height: 50px;
            overflow: hidden;
        }
        
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        
        .btn-send {
            border-radius: 50%;
            width: 50px;
            height: 50px;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #667eea;
            border: none;
            color: white;
            transition: all 0.2s;
        }
        
        .btn-send:hover {
            background: #5a6fd8;
            transform: scale(1.05);
        }
        
        .btn-send:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.8rem;
            color: #6c757d;
            margin-bottom: 1rem;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            transition: background-color 0.3s;
        }
        
        .status-dot.connecting {
            background: #ffc107;
            animation: pulse 1s infinite;
        }
        
        .status-dot.connected {
            background: #28a745;
        }
        
        .status-dot.disconnected {
            background: #dc3545;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .error-message {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            border-radius: 0.5rem;
            padding: 0.75rem;
            margin-bottom: 1rem;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .chat-container {
                margin: 1rem;
                border-radius: 10px;
            }
            
            .chat-messages {
                height: 300px;
            }
            
            .message-content {
                max-width: 85%;
            }
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="chat-container">
            <div class="chat-header">
                <h1><i class="bi bi-chat-dots"></i> Web Chat</h1>
                <p>Connect with our AI assistant</p>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="text-center text-muted py-4">
                    <i class="bi bi-chat-dots fs-1"></i>
                    <p class="mt-2">Start a conversation by typing a message below</p>
                </div>
            </div>
            
            <div class="chat-input">
                <div class="status-indicator">
                    <div class="status-dot connecting"></div>
                    <span class="status-text">Connecting...</span>
                </div>
                
                <div class="input-group">
                    <textarea 
                        class="form-control" 
                        id="message-input" 
                        placeholder="Type your message here..."
                        rows="1"
                    ></textarea>
                    <button 
                        class="btn btn-send ms-2" 
                        id="send-button" 
                        type="button"
                        disabled
                    >
                        <i class="bi bi-send"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Chat JavaScript -->
    <script src="assets/chat.js"></script>
</body>
</html> 