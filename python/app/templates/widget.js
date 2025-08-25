// Web Chat Bridge Widget JavaScript
// This file provides the client-side functionality for the chat widget

(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        apiEndpoint: '/chat/api',
        pollInterval: 3000, // 3 seconds
        maxRetries: 3,
        retryDelay: 1000 // 1 second
    };
    
    // Widget state
    let widgetState = {
        sessionId: null,
        uid: null,
        isConnected: false,
        retryCount: 0,
        pollTimer: null
    };
    
    // Initialize widget
    function initWidget() {
        // Generate session ID if not exists
        if (!widgetState.sessionId) {
            widgetState.sessionId = 'widget_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        
        // Generate UID if not exists
        if (!widgetState.uid) {
            widgetState.uid = 'uid_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        
        // Start polling for responses
        startPolling();
        
        console.log('Web Chat Bridge Widget initialized');
    }
    
    // Send message to server
    function sendMessage(message) {
        if (!message || !message.trim()) {
            console.warn('Empty message, not sending');
            return Promise.reject(new Error('Empty message'));
        }
        
        const messageData = {
            session_id: widgetState.sessionId,
            message: message.trim()
        };
        
        return fetch(`${CONFIG.apiEndpoint}/send_message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(messageData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                widgetState.uid = data.data.uid;
                console.log('Message sent successfully:', data.data);
                return data.data;
            } else {
                throw new Error(data.error || 'Failed to send message');
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            throw error;
        });
    }
    
    // Get responses from server
    function getResponses(since = null) {
        const params = new URLSearchParams({
            session_id: widgetState.sessionId
        });
        
        if (since) {
            params.append('since', since);
        }
        
        return fetch(`${CONFIG.apiEndpoint}/get_responses?${params}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                return data.data.responses || [];
            } else {
                throw new Error(data.error || 'Failed to get responses');
            }
        })
        .catch(error => {
            console.error('Error getting responses:', error);
            throw error;
        });
    }
    
    // Start polling for responses
    function startPolling() {
        if (widgetState.pollTimer) {
            clearInterval(widgetState.pollTimer);
        }
        
        widgetState.pollTimer = setInterval(() => {
            pollResponses();
        }, CONFIG.pollInterval);
        
        widgetState.isConnected = true;
    }
    
    // Stop polling for responses
    function stopPolling() {
        if (widgetState.pollTimer) {
            clearInterval(widgetState.pollTimer);
            widgetState.pollTimer = null;
        }
        
        widgetState.isConnected = false;
    }
    
    // Poll for new responses
    function pollResponses() {
        if (!widgetState.isConnected) {
            return;
        }
        
        getResponses()
        .then(responses => {
            if (responses && responses.length > 0) {
                // Process new responses
                responses.forEach(response => {
                    handleNewResponse(response);
                });
            }
            
            // Reset retry count on successful request
            widgetState.retryCount = 0;
        })
        .catch(error => {
            console.warn('Polling error:', error);
            widgetState.retryCount++;
            
            // Stop polling if too many retries
            if (widgetState.retryCount >= CONFIG.maxRetries) {
                console.error('Max retries reached, stopping polling');
                stopPolling();
            }
        });
    }
    
    // Handle new response from server
    function handleNewResponse(response) {
        // Emit custom event for new response
        const event = new CustomEvent('webChatResponse', {
            detail: {
                response: response,
                sessionId: widgetState.sessionId,
                timestamp: new Date().toISOString()
            }
        });
        
        document.dispatchEvent(event);
        
        console.log('New response received:', response);
    }
    
    // Get widget state
    function getState() {
        return { ...widgetState };
    }
    
    // Update configuration
    function updateConfig(newConfig) {
        Object.assign(CONFIG, newConfig);
        console.log('Widget configuration updated:', CONFIG);
    }
    
    // Cleanup widget
    function cleanup() {
        stopPolling();
        widgetState = {
            sessionId: null,
            uid: null,
            isConnected: false,
            retryCount: 0,
            pollTimer: null
        };
        console.log('Widget cleaned up');
    }
    
    // Expose public API
    window.WebChatBridge = {
        init: initWidget,
        sendMessage: sendMessage,
        getResponses: getResponses,
        startPolling: startPolling,
        stopPolling: stopPolling,
        getState: getState,
        updateConfig: updateConfig,
        cleanup: cleanup
    };
    
    // Auto-initialize if DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWidget);
    } else {
        initWidget();
    }
    
})();
