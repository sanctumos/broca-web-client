/**
 * Sanctum Chat Widget - Main JavaScript Library
 * 
 * A lightweight, embeddable chat widget that can be integrated
 * into any website or application.
 */

(function(window, document) {
    'use strict';

    // Default configuration
    let config = {
        apiKey: null,
        position: 'bottom-right',
        theme: 'light',
        title: 'Chat with us',
        primaryColor: '#007bff',
        language: 'en',
        autoOpen: false,
        notifications: true,
        sound: true
    };

    // Widget state
    let state = {
        isInitialized: false,
        isOpen: false,
        isTyping: false,
        sessionId: null,
        uid: null,
        messageCount: 0,
        eventListeners: {},
        typingTimeout: null
    };

    // Widget HTML template
    const widgetTemplate = `
        <div class="sanctum-chat-widget" data-position="${config.position}" data-theme="${config.theme}">
            <!-- Chat Bubble -->
            <div class="sanctum-chat-bubble" id="sanctum-chat-bubble">
                <svg viewBox="0 0 24 24">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                </svg>
                <div class="notification-badge sanctum-hidden" id="sanctum-notification-badge">0</div>
            </div>
            
            <!-- Chat Window -->
            <div class="sanctum-chat-window" id="sanctum-chat-window">
                <!-- Chat Header -->
                <div class="sanctum-chat-header">
                    <h3 id="sanctum-chat-title">${config.title}</h3>
                    <button class="close-btn" id="sanctum-chat-close">
                        <svg viewBox="0 0 24 24" width="20" height="20">
                            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="currentColor"/>
                        </svg>
                    </button>
                </div>
                
                <!-- Chat Messages -->
                <div class="sanctum-chat-messages" id="sanctum-chat-messages">
                    <div class="sanctum-message">
                        <div class="sanctum-message-avatar">S</div>
                        <div class="sanctum-message-content">
                            Hello! How can I help you today?
                            <div class="sanctum-message-time">${new Date().toLocaleTimeString()}</div>
                        </div>
                    </div>
                </div>
                
                <!-- Chat Input -->
                <div class="sanctum-chat-input">
                    <textarea 
                        id="sanctum-chat-input" 
                        placeholder="Type your message..."
                        rows="1"
                    ></textarea>
                    <button class="sanctum-chat-send" id="sanctum-chat-send" disabled>
                        <svg viewBox="0 0 24 24">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    `;

    // Utility functions
    const utils = {
        // Generate unique session ID
        generateSessionId: function() {
            return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        },

        // Generate unique UID
        generateUid: function() {
            return Math.random().toString(36).substr(2, 15);
        },

        // Format timestamp
        formatTime: function(timestamp) {
            return new Date(timestamp).toLocaleTimeString();
        },

        // Sanitize HTML
        sanitizeHtml: function(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        // Debounce function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        // Check if element is in viewport
        isInViewport: function(element) {
            const rect = element.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        }
    };

    // API communication
    const api = {
        // Make API request
        async request(action, data = {}, method = 'POST') {
            try {
                const response = await fetch('/api/v1/?action=' + action, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + config.apiKey
                    },
                    body: method === 'POST' ? JSON.stringify(data) : undefined
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const result = await response.json();
                
                if (!result.success) {
                    throw new Error(result.error || 'API request failed');
                }

                return result.data;
            } catch (error) {
                console.error('Sanctum Chat Widget API Error:', error);
                throw error;
            }
        },

        // Send message
        async sendMessage(message) {
            if (!state.sessionId) {
                throw new Error('No active session');
            }

            const data = {
                session_id: state.sessionId,
                message: message,
                uid: state.uid
            };

            return await this.request('inbox', data);
        },

        // Get messages
        async getMessages() {
            if (!state.sessionId) {
                throw new Error('No active session');
            }

            const data = {
                session_id: state.sessionId,
                uid: state.uid
            };

            return await this.request('responses', data);
        },

        // Update session
        async updateSession() {
            if (!state.sessionId) {
                throw new Error('No active session');
            }

            const data = {
                session_id: state.sessionId,
                uid: state.uid
            };

            return await this.request('session_response', data);
        }
    };

    // UI management
    const ui = {
        // Initialize UI
        init() {
            // Insert widget HTML
            document.body.insertAdjacentHTML('beforeend', widgetTemplate);
            
            // Get DOM elements
            this.elements = {
                widget: document.querySelector('.sanctum-chat-widget'),
                bubble: document.getElementById('sanctum-chat-bubble'),
                window: document.getElementById('sanctum-chat-window'),
                messages: document.getElementById('sanctum-chat-messages'),
                input: document.getElementById('sanctum-chat-input'),
                send: document.getElementById('sanctum-chat-send'),
                close: document.getElementById('sanctum-chat-close'),
                title: document.getElementById('sanctum-chat-title'),
                notificationBadge: document.getElementById('sanctum-notification-badge')
            };

            // Apply custom styles
            this.applyCustomStyles();
            
            // Bind events
            this.bindEvents();
            
            // Set initial theme
            this.setTheme(config.theme);
            
            // Auto-open if configured
            if (config.autoOpen) {
                setTimeout(() => this.open(), 1000);
            }
        },

        // Apply custom styles
        applyCustomStyles() {
            const style = document.createElement('style');
            style.textContent = `
                .sanctum-chat-widget {
                    --primary-color: ${config.primaryColor};
                    --primary-hover: ${this.adjustColor(config.primaryColor, -20)};
                }
            `;
            document.head.appendChild(style);
        },

        // Adjust color brightness
        adjustColor(color, amount) {
            const hex = color.replace('#', '');
            const num = parseInt(hex, 16);
            const r = Math.min(255, Math.max(0, (num >> 16) + amount));
            const g = Math.min(255, Math.max(0, ((num >> 8) & 0x00FF) + amount));
            const b = Math.min(255, Math.max(0, (num & 0x0000FF) + amount));
            return '#' + (r << 16 | g << 8 | b).toString(16).padStart(6, '0');
        },

        // Bind event listeners
        bindEvents() {
            // Chat bubble click
            this.elements.bubble.addEventListener('click', () => this.toggle());
            
            // Close button click
            this.elements.close.addEventListener('click', () => this.close());
            
            // Input events
            this.elements.input.addEventListener('input', () => this.updateSendButton());
            this.elements.input.addEventListener('keydown', (e) => this.handleKeydown(e));
            this.elements.input.addEventListener('input', utils.debounce(() => this.autoResizeTextarea(), 100));
            
            // Send button click
            this.elements.send.addEventListener('click', () => this.sendMessage());
            
            // Click outside to close
            document.addEventListener('click', (e) => this.handleOutsideClick(e));
            
            // Escape key to close
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && state.isOpen) {
                    this.close();
                }
            });
        },

        // Handle keydown events
        handleKeydown(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        },

        // Handle outside clicks
        handleOutsideClick(e) {
            if (state.isOpen && !this.elements.widget.contains(e.target)) {
                this.close();
            }
        },

        // Toggle chat window
        toggle() {
            if (state.isOpen) {
                this.close();
            } else {
                this.open();
            }
        },

        // Open chat window
        open() {
            if (state.isOpen) return;
            
            state.isOpen = true;
            this.elements.window.classList.add('open');
            this.elements.input.focus();
            
            // Emit open event
            this.emit('open');
            
            // Clear notification badge
            this.clearNotifications();
        },

        // Close chat window
        close() {
            if (!state.isOpen) return;
            
            state.isOpen = false;
            this.elements.window.classList.remove('open');
            this.elements.input.blur();
            
            // Emit close event
            this.emit('close');
        },

        // Send message
        async sendMessage() {
            const message = this.elements.input.value.trim();
            if (!message) return;

            try {
                // Add user message to UI
                this.addMessage(message, 'user');
                
                // Clear input
                this.elements.input.value = '';
                this.autoResizeTextarea();
                this.updateSendButton();
                
                // Send to API
                await api.sendMessage(message);
                
                // Emit message event
                this.emit('message', { message, type: 'user' });
                
                // Show typing indicator
                this.showTypingIndicator();
                
                // Poll for responses
                this.pollForResponses();
                
            } catch (error) {
                console.error('Failed to send message:', error);
                this.addMessage('Failed to send message. Please try again.', 'error');
            }
        },

        // Add message to chat
        addMessage(content, type = 'bot') {
            const messageDiv = document.createElement('div');
            messageDiv.className = `sanctum-message ${type}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'sanctum-message-avatar';
            avatar.textContent = type === 'user' ? 'U' : 'S';
            
            const messageContent = document.createElement('div');
            messageContent.className = 'sanctum-message-content';
            messageContent.innerHTML = utils.sanitizeHtml(content);
            
            const time = document.createElement('div');
            time.className = 'sanctum-message-time';
            time.textContent = utils.formatTime(new Date());
            
            messageContent.appendChild(time);
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
            
            this.elements.messages.appendChild(messageDiv);
            
            // Scroll to bottom
            this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
            
            // Update message count
            state.messageCount++;
            
            // Show notification if chat is closed
            if (!state.isOpen && type === 'bot') {
                this.showNotification();
            }
        },

        // Show typing indicator
        showTypingIndicator() {
            if (this.elements.typingIndicator) {
                this.elements.typingIndicator.remove();
            }
            
            const typingDiv = document.createElement('div');
            typingDiv.className = 'sanctum-typing-indicator';
            typingDiv.id = 'sanctum-typing-indicator';
            
            for (let i = 0; i < 3; i++) {
                const dot = document.createElement('div');
                dot.className = 'sanctum-typing-dot';
                typingDiv.appendChild(dot);
            }
            
            this.elements.messages.appendChild(typingDiv);
            this.elements.typingIndicator = typingDiv;
            this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
        },

        // Hide typing indicator
        hideTypingIndicator() {
            if (this.elements.typingIndicator) {
                this.elements.typingIndicator.remove();
                this.elements.typingIndicator = null;
            }
        },

        // Show notification
        showNotification() {
            if (!config.notifications) return;
            
            // Update badge
            const currentCount = parseInt(this.elements.notificationBadge.textContent) || 0;
            this.elements.notificationBadge.textContent = currentCount + 1;
            this.elements.notificationBadge.classList.remove('sanctum-hidden');
            
            // Browser notification
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification(config.title, {
                    body: 'You have a new message',
                    icon: '/widget/static/assets/icons/chat-icon.svg'
                });
            }
            
            // Sound notification
            if (config.sound) {
                this.playNotificationSound();
            }
        },

        // Clear notifications
        clearNotifications() {
            this.elements.notificationBadge.classList.add('sanctum-hidden');
            this.elements.notificationBadge.textContent = '0';
        },

        // Play notification sound
        playNotificationSound() {
            try {
                const audio = new Audio('/widget/static/assets/sounds/notification.mp3');
                audio.volume = 0.5;
                audio.play().catch(() => {
                    // Fallback: create a simple beep
                    const context = new (window.AudioContext || window.webkitAudioContext)();
                    const oscillator = context.createOscillator();
                    const gainNode = context.createGain();
                    
                    oscillator.connect(gainNode);
                    gainNode.connect(context.destination);
                    
                    oscillator.frequency.value = 800;
                    gainNode.gain.value = 0.1;
                    
                    oscillator.start();
                    setTimeout(() => oscillator.stop(), 200);
                });
            } catch (error) {
                console.warn('Could not play notification sound:', error);
            }
        },

        // Update send button state
        updateSendButton() {
            const hasText = this.elements.input.value.trim().length > 0;
            this.elements.send.disabled = !hasText;
        },

        // Auto-resize textarea
        autoResizeTextarea() {
            const textarea = this.elements.input;
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        },

        // Set theme
        setTheme(theme) {
            this.elements.widget.setAttribute('data-theme', theme);
            config.theme = theme;
        },

        // Update configuration
        updateConfig(newConfig) {
            Object.assign(config, newConfig);
            
            // Update theme
            if (newConfig.theme) {
                this.setTheme(newConfig.theme);
            }
            
            // Update title
            if (newConfig.title) {
                this.elements.title.textContent = newConfig.title;
            }
            
            // Update position
            if (newConfig.position) {
                this.elements.widget.setAttribute('data-position', newConfig.position);
            }
            
            // Update primary color
            if (newConfig.primaryColor) {
                this.applyCustomStyles();
            }
        },

        // Poll for responses
        async pollForResponses() {
            if (!state.sessionId) return;
            
            try {
                const responses = await api.getMessages();
                
                if (responses && responses.length > 0) {
                    this.hideTypingIndicator();
                    
                    responses.forEach(response => {
                        this.addMessage(response.response, 'bot');
                        this.emit('message', { message: response.response, type: 'bot' });
                    });
                }
                
                // Continue polling if chat is open
                if (state.isOpen) {
                    setTimeout(() => this.pollForResponses(), 3000);
                }
                
            } catch (error) {
                console.error('Failed to poll for responses:', error);
                this.hideTypingIndicator();
            }
        },

        // Emit events
        emit(event, data) {
            if (state.eventListeners[event]) {
                state.eventListeners[event].forEach(callback => {
                    try {
                        callback(data);
                    } catch (error) {
                        console.error('Event listener error:', error);
                    }
                });
            }
        }
    };

    // Public API
    const SanctumChat = {
        // Initialize widget
        init(options = {}) {
            // Validate required options
            if (!options.apiKey) {
                throw new Error('API key is required');
            }
            
            // Merge options with defaults
            Object.assign(config, options);
            
            // Initialize if not already done
            if (!state.isInitialized) {
                // Generate session ID and UID
                state.sessionId = utils.generateSessionId();
                state.uid = utils.generateUid();
                
                // Initialize UI
                ui.init();
                
                state.isInitialized = true;
            }
            
            return this;
        },

        // Open chat
        open() {
            if (state.isInitialized) {
                ui.open();
            }
        },

        // Close chat
        close() {
            if (state.isInitialized) {
                ui.close();
            }
        },

        // Toggle chat
        toggle() {
            if (state.isInitialized) {
                ui.toggle();
            }
        },

        // Send message programmatically
        sendMessage(message) {
            if (state.isInitialized && message) {
                ui.elements.input.value = message;
                ui.sendMessage();
            }
        },

        // Update configuration
        updateConfig(newConfig) {
            if (state.isInitialized) {
                ui.updateConfig(newConfig);
            }
        },

        // Event listeners
        on(event, callback) {
            if (!state.eventListeners[event]) {
                state.eventListeners[event] = [];
            }
            state.eventListeners[event].push(callback);
        },

        off(event, callback) {
            if (state.eventListeners[event]) {
                const index = state.eventListeners[event].indexOf(callback);
                if (index > -1) {
                    state.eventListeners[event].splice(index, 1);
                }
            }
        },

        // Destroy widget
        destroy() {
            if (state.isInitialized) {
                const widget = document.querySelector('.sanctum-chat-widget');
                if (widget) {
                    widget.remove();
                }
                state.isInitialized = false;
                state.eventListeners = {};
            }
        },

        // Get widget state
        getState() {
            return { ...state };
        },

        // Get configuration
        getConfig() {
            return { ...config };
        },

        // Simulate typing (for demo purposes)
        simulateTyping() {
            if (state.isInitialized) {
                ui.showTypingIndicator();
                setTimeout(() => ui.hideTypingIndicator(), 3000);
            }
        },

        // Clear chat
        clearChat() {
            if (state.isInitialized) {
                ui.elements.messages.innerHTML = `
                    <div class="sanctum-message">
                        <div class="sanctum-message-avatar">S</div>
                        <div class="sanctum-message-content">
                            Chat cleared. How can I help you?
                            <div class="sanctum-message-time">${utils.formatTime(new Date())}</div>
                        </div>
                    </div>
                `;
                state.messageCount = 1;
            }
        }
    };

    // Expose to global scope
    window.SanctumChat = SanctumChat;

    // Auto-initialize from data attributes
    document.addEventListener('DOMContentLoaded', () => {
        const script = document.currentScript || document.querySelector('script[src*="chat-widget.js"]');
        if (script) {
            const apiKey = script.getAttribute('data-api-key');
            const position = script.getAttribute('data-position');
            const theme = script.getAttribute('data-theme');
            const title = script.getAttribute('data-title');
            
            if (apiKey) {
                SanctumChat.init({
                    apiKey,
                    position: position || 'bottom-right',
                    theme: theme || 'light',
                    title: title || 'Chat with us'
                });
            }
        }
    });

})(window, document);
