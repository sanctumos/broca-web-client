# Web Chat Plugin: Broca2's First External API Integration

Sanctum: Broca2 now features its first external API integration with the revolutionary Web Chat Plugin. This plugin demonstrates the power of Broca2's new auto-discovery architecture by seamlessly bridging web chat widgets with Broca2 agents through a secure, polling-based API system.

We're excited to announce the Web Chat Plugin for Broca2, the first plugin to fully leverage the new auto-discovery and dynamic loading capabilities introduced in v0.10.0. This plugin represents a breakthrough in Broca2's extensibility, demonstrating how external APIs can be seamlessly integrated without modifying core Broca2 code or requiring new public ports on the Sanctum server.

Repository: github.com/actuallyrizzn/sanctum-web-client

## Highlights of This Plugin

### 🌐 External API Integration
**Secure web chat bridge**: Complete integration with external PHP APIs for secure web chat functionality without exposing Broca2 directly to the internet.

**Polling-based architecture**: Broca2 plugins now poll external APIs for messages, eliminating the need for new public ports on the Sanctum server.

**Session management**: Unique user identification with 16-character hex UIDs for persistent identity across web sessions.

### 🔒 Security-First Design
**API key authentication**: Secure communication between Broca2 and the web chat bridge using configurable API keys.

**Rate limiting**: Built-in protection against abuse with per-IP and per-endpoint rate limits.

**Session timeout**: Automatic cleanup of inactive sessions after 30 minutes of inactivity.

### 🎨 Modern Web Interface
**Bootstrap 5 UI**: Clean, responsive web chat widget with modern styling and auto-expanding input.

**Admin dashboard**: Comprehensive monitoring and management interface for sessions, configuration, and system health.

**Real-time updates**: Live polling for message delivery and response retrieval.

## Why This Matters

This plugin demonstrates the true power of Broca2's new plugin architecture. Previously, integrating external systems required complex webhook setups and public port configurations. Now, plugins can seamlessly integrate with external APIs through a simple polling mechanism:

- **Zero public ports**: No need to expose Broca2 directly to the internet
- **Secure communication**: API key authentication ensures only authorized access
- **Scalable architecture**: Polling-based design handles high message volumes
- **Easy deployment**: Drop-in plugin installation with automatic discovery

## Technical Architecture

### Plugin Components
- **`plugin.py`**: Main plugin entry point with Broca2 integration
- **`api_client.py`**: HTTP client for communicating with the web chat bridge
- **`message_handler.py`**: Message processing and response routing logic
- **`settings.py`**: Configuration management and validation

### Web Chat Bridge
- **PHP API server**: Vanilla Nginx-compatible API with querystring routing
- **SQLite database**: Lightweight, file-based storage for sessions and messages
- **Session management**: Automatic UID generation and session lifecycle management
- **Admin interface**: Web-based dashboard for monitoring and configuration

### Data Flow
1. **Web chat widget** sends messages to PHP API
2. **Broca2 plugin** polls API for new messages
3. **Broca2 processes** messages through agent pipeline
4. **Plugin sends** responses back to API
5. **Web widget** polls for responses and displays them

## Key Features

### 🔍 Auto-Discovery Integration
**Dynamic plugin loading**: Automatically discovered and loaded by Broca2's new plugin system without manual registration.

**Self-contained architecture**: All dependencies are lazy-loaded only when the plugin is actually used.

**Dynamic configuration**: Plugin settings are automatically injected via the new `apply_settings()` method.

### 🌐 Web Chat Capabilities
**Real-time messaging**: Instant message delivery and response retrieval through polling.

**Session persistence**: Users maintain conversation context across browser sessions.

**Admin monitoring**: Comprehensive dashboard for session management and system health.

**Mobile responsive**: Bootstrap 5 interface works seamlessly on all devices.

### 🔧 Advanced Configuration
**API key management**: Secure authentication with configurable keys.

**Rate limiting**: Protection against abuse with customizable limits.

**Session timeout**: Automatic cleanup of inactive sessions.

**Log management**: Comprehensive logging with automatic rotation and cleanup.

## Getting Started

### For Broca2 Users
1. **Install the plugin**: Copy the `plugin_web_chat/` directory to your Broca2 `plugins/` folder
2. **Configure settings**: Update `plugin_web_chat/settings.py` with your API endpoint and key
3. **Deploy web bridge**: Set up the PHP web chat bridge on your server
4. **Start Broca2**: The plugin will be automatically discovered and loaded

### For Web Chat Bridge Deployment
1. **Upload files**: Place the `public/` directory contents in your web server
2. **Create database**: The SQLite database will be automatically initialized
3. **Configure API key**: Update `public/config/settings.php` with your desired API key
4. **Access web interface**: Navigate to your domain to access the chat widget

### Example Configuration
```python
# plugin_web_chat/settings.py
WEB_CHAT_API_URL = "https://your-domain.com/api/v1/"
WEB_CHAT_API_KEY = "your-secure-api-key"
POLL_INTERVAL = 5  # seconds
```

## Technical Implementation

### Plugin Architecture
The web chat plugin follows Broca2's new plugin patterns:

```python
from plugins import Plugin

class WebChatPlugin(Plugin):
    def get_name(self) -> str:
        return "web_chat"
    
    def get_platform(self) -> str:
        return "web"
    
    def get_message_handler(self):
        return self._handle_response
    
    async def _handle_response(self, response: str, profile, message_id: int) -> None:
        # Send response back to web chat API
        await self.api_client.send_response(response, profile, message_id)
```

### API Integration
The plugin communicates with the web chat bridge through a simple HTTP API:

- **GET `/api/v1/?action=inbox`**: Retrieve new messages
- **POST `/api/v1/?action=outbox`**: Send responses
- **GET `/api/v1/?action=sessions`**: List active sessions
- **GET `/api/v1/?action=responses`**: Retrieve responses for a session

### Security Features
- **API key authentication**: All requests require valid API key
- **Rate limiting**: Per-IP and per-endpoint limits prevent abuse
- **Input validation**: All user input is sanitized and validated
- **Session isolation**: Messages are isolated by session ID

## What's Next

This plugin opens the door for many new integration possibilities:

- **Multi-platform chat**: Extend to support Discord, Slack, and other platforms
- **Advanced analytics**: Message analytics and conversation insights
- **File sharing**: Support for image and document sharing
- **Voice integration**: Add voice message capabilities
- **Plugin marketplace**: Easy distribution of community plugins

## Key Learnings from Development

The development of this plugin revealed important patterns for external API integration:

- **Polling vs Webhooks**: Polling provides better security and reliability for external integrations
- **Session Management**: Proper session lifecycle management is crucial for user experience
- **Error Handling**: Robust error handling and retry logic ensures reliable operation
- **Configuration Management**: Dynamic configuration enables flexible deployment

## Community Impact

This plugin demonstrates the power of Broca2's new plugin architecture and provides a reference implementation for future plugin development. The web chat bridge serves as a template for integrating Broca2 with any external system, while the plugin shows how to leverage Broca2's auto-discovery capabilities.

We invite the community to:
- **Deploy the web chat plugin** and provide feedback
- **Develop new plugins** using this as a reference implementation
- **Contribute improvements** to the web chat bridge
- **Share integration patterns** for other platforms

The web chat plugin represents a major milestone in Broca2's evolution toward becoming a truly extensible platform for agent communication and integration. This plugin proves that Broca2's new architecture can handle real-world integration challenges while maintaining security and simplicity.

---

*The web chat plugin is available now and ready for deployment. Check out the [plugin development guide](docs/plugin-development.md) for detailed implementation details and the [API documentation](docs/api-documentation.md) for complete endpoint reference.* 