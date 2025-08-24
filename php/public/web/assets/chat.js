/**
 * Web Chat Widget JavaScript
 * Handles the frontend functionality for the web chat interface
 */

class WebChatWidget {
    constructor() {
        this.apiUrl = window.location.origin + '/api/v1/index.php';
        this.sessionId = this.generateSessionId();
        this.userUid = null;  // Will be set by PHP
        this.lastResponseCheck = null;
        this.isConnected = false;
        this.messageQueue = [];
        this.pollingInterval = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.updateStatus('connecting');
        this.startPolling();
        this.updateStatus('connected');
    }
    
    generateSessionId() {
        // Generate a unique session ID
        const timestamp = Date.now().toString(36);
        const random = Math.random().toString(36).substring(2);
        return `session_${timestamp}_${random}`;
    }
    
    bindEvents() {
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        
        // Handle input changes
        messageInput.addEventListener('input', () => {
            this.adjustTextareaHeight(messageInput);
            this.updateSendButton();
        });
        
        // Handle Enter key
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Handle send button click
        sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Auto-resize textarea
        messageInput.addEventListener('input', () => {
            this.adjustTextareaHeight(messageInput);
        });
    }
    
    adjustTextareaHeight(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }
    
    updateSendButton() {
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        const hasText = messageInput.value.trim().length > 0;
        
        sendButton.disabled = !hasText || !this.isConnected;
    }
    
    updateStatus(status) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');
        
        statusDot.className = 'status-dot ' + status;
        
        switch (status) {
            case 'connecting':
                statusText.textContent = 'Connecting...';
                this.isConnected = false;
                break;
            case 'connected':
                statusText.textContent = 'Connected';
                this.isConnected = true;
                break;
            case 'disconnected':
                statusText.textContent = 'Disconnected';
                this.isConnected = false;
                break;
        }
        
        this.updateSendButton();
    }
    
    async sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        
        if (!message || !this.isConnected) {
            return;
        }
        
        // Clear input
        messageInput.value = '';
        this.adjustTextareaHeight(messageInput);
        this.updateSendButton();
        
        // Add user message to UI
        this.addMessageToUI('user', message);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch(`${this.apiUrl}?action=messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: message,
                    timestamp: new Date().toISOString()
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to send message');
            }
            
            // Store UID if this is a new user
            if (data.data && data.data.uid && !this.userUid) {
                this.userUid = data.data.uid;
                console.log(`New user UID: ${this.userUid}`);
            }
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
        } catch (error) {
            console.error('Failed to send message:', error);
            this.hideTypingIndicator();
            this.addMessageToUI('error', 'Failed to send message. Please try again.');
        }
    }
    
    startPolling() {
        // Poll for responses every 2 seconds
        this.pollingInterval = setInterval(() => {
            this.checkForResponses();
        }, 2000);
    }
    
    async checkForResponses() {
        try {
            const since = this.lastResponseCheck || new Date(Date.now() - 60000).toISOString();
            
            const response = await fetch(`${this.apiUrl}?action=responses&session_id=${this.sessionId}&since=${since}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.data && data.data.responses && data.data.responses.length > 0) {
                this.hideTypingIndicator();
                
                for (const response of data.data.responses) {
                    this.addMessageToUI('agent', response.response, response.timestamp);
                }
                
                this.lastResponseCheck = new Date().toISOString();
            }
            
        } catch (error) {
            console.error('Failed to check responses:', error);
            this.updateStatus('disconnected');
        }
    }
    
    addMessageToUI(type, content, timestamp = null) {
        const messagesContainer = document.getElementById('chat-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        // Decode HTML entities before setting content
        const decodedContent = this.decodeHtmlEntities(content);
        contentDiv.textContent = decodedContent;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = timestamp ? this.formatTime(timestamp) : 'Just now';
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    showTypingIndicator() {
        const messagesContainer = document.getElementById('chat-messages');
        
        // Remove existing typing indicator
        this.hideTypingIndicator();
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message agent typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            typingDiv.appendChild(dot);
        }
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    decodeHtmlEntities(text) {
        const textarea = document.createElement('textarea');
        textarea.innerHTML = text;
        return textarea.value;
    }
    
    formatTime(timestamp) {
        const date = new Date(timestamp);
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
    
    destroy() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
    }
}

// Initialize the chat widget when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.chatWidget = new WebChatWidget();
});

// Clean up when the page unloads
window.addEventListener('beforeunload', () => {
    if (window.chatWidget) {
        window.chatWidget.destroy();
    }
}); 