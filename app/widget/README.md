# Sanctum Chat Widget

A lightweight, embeddable chat widget that can be integrated into any website or application. Built with vanilla JavaScript and CSS, it provides a professional chat experience with minimal footprint.

## 🚀 Features

- **Floating Chat Bubble**: Always-visible chat trigger
- **Expandable Chat Window**: Full chat interface with smooth animations
- **Real-time Messaging**: Live chat with your existing Sanctum API
- **Session Persistence**: Maintains chat state across page interactions
- **Responsive Design**: Works perfectly on all device sizes
- **Theme System**: Light, dark, and auto themes
- **Position Variants**: 8 corner positions with mobile optimization
- **Customization**: Brand colors, titles, and appearance options
- **Notifications**: Browser notifications and sound alerts
- **Accessibility**: Full keyboard navigation and screen reader support

## 📦 Installation

### 1. Include the Widget Script

Add the widget script to your HTML page:

```html
<script src="https://yourdomain.com/widget/static/js/chat-widget.js"></script>
```

### 2. Initialize the Widget

Initialize the widget with your configuration:

```html
<script>
  SanctumChat.init({
    apiKey: 'your-api-key',
    position: 'bottom-right',
    theme: 'light'
  });
</script>
```

## ⚙️ Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | string | **required** | Your Sanctum API key for authentication |
| `position` | string | `'bottom-right'` | Widget position: `'bottom-right'`, `'bottom-left'`, `'top-right'`, `'top-left'` |
| `theme` | string | `'light'` | Widget theme: `'light'`, `'dark'`, `'auto'` |
| `title` | string | `'Chat with us'` | Chat window title |
| `primaryColor` | string | `'#007bff'` | Primary brand color (hex) |
| `language` | string | `'en'` | Widget language |
| `autoOpen` | boolean | `false` | Automatically open chat on page load |
| `notifications` | boolean | `true` | Enable browser notifications |
| `sound` | boolean | `true` | Enable sound notifications |

## 🔧 Advanced Usage

### Programmatic Control

```javascript
// Open/close chat
SanctumChat.open();
SanctumChat.close();
SanctumChat.toggle();

// Send message programmatically
SanctumChat.sendMessage('Hello from external code');

// Update configuration
SanctumChat.updateConfig({
  theme: 'dark',
  title: 'New Chat Title'
});
```

### Event Listeners

```javascript
// Listen for widget events
SanctumChat.on('open', function() {
  console.log('Chat opened');
});

SanctumChat.on('message', function(data) {
  console.log('New message:', data.message);
});

SanctumChat.on('close', function() {
  console.log('Chat closed');
});

SanctumChat.on('error', function(error) {
  console.error('Widget error:', error);
});
```

### Auto-initialization with Data Attributes

You can also initialize the widget using data attributes on the script tag:

```html
<script 
  src="https://yourdomain.com/widget/static/js/chat-widget.js"
  data-api-key="your-api-key"
  data-position="bottom-right"
  data-theme="dark"
  data-title="Support Chat">
</script>
```

## 🎨 Customization

### CSS Variables

The widget uses CSS custom properties for easy theming:

```css
:root {
  --primary-color: #007bff;
  --widget-bg: #ffffff;
  --widget-text: #333333;
  --widget-border: #e1e5e9;
  --widget-radius: 12px;
  --widget-padding: 16px;
}
```

### Custom Themes

Create custom themes by overriding CSS variables:

```css
.sanctum-chat-widget[data-theme="custom"] {
  --primary-color: #ff6b6b;
  --widget-bg: #2d3436;
  --widget-text: #ffffff;
  --widget-border: #636e72;
}
```

## 📱 Mobile Optimization

The widget automatically adapts to mobile devices:

- Responsive sizing and positioning
- Touch-friendly interactions
- Mobile-optimized animations
- Adaptive spacing and typography

## 🔒 Security

- **API Authentication**: Uses your existing Sanctum API key system
- **Session Isolation**: Each widget instance has unique session IDs
- **Input Sanitization**: All user input is properly sanitized
- **CORS Support**: Configured for cross-origin requests
- **Rate Limiting**: Inherits your existing rate limiting

## 🌐 Browser Support

- **Modern Browsers**: Chrome 60+, Firefox 55+, Safari 12+, Edge 79+
- **Mobile Browsers**: iOS Safari 12+, Chrome Mobile 60+
- **Legacy Support**: IE11+ (with polyfills)

## 📊 Performance

- **Lightweight**: ~15KB gzipped JavaScript
- **Fast Loading**: Optimized for quick initialization
- **Efficient Polling**: Smart API polling with exponential backoff
- **Memory Management**: Proper cleanup and event handling

## 🧪 Testing

### Demo Page

Visit `/widget/demo` to test the widget with different configurations.

### Health Check

Check widget status at `/widget/health`.

### Configuration

View available options at `/widget/config`.

## 🚨 Troubleshooting

### Common Issues

1. **Widget not appearing**
   - Check browser console for errors
   - Verify API key is correct
   - Ensure script is loaded before initialization

2. **Messages not sending**
   - Check API endpoint availability
   - Verify CORS configuration
   - Check network tab for failed requests

3. **Styling issues**
   - Ensure CSS is properly loaded
   - Check for conflicting CSS rules
   - Verify CSS custom properties support

### Debug Mode

Enable debug logging:

```javascript
SanctumChat.init({
  apiKey: 'your-key',
  debug: true
});
```

## 📚 API Reference

### Methods

- `SanctumChat.init(options)` - Initialize widget
- `SanctumChat.open()` - Open chat window
- `SanctumChat.close()` - Close chat window
- `SanctumChat.toggle()` - Toggle chat window
- `SanctumChat.sendMessage(message)` - Send message
- `SanctumChat.updateConfig(config)` - Update configuration
- `SanctumChat.on(event, callback)` - Add event listener
- `SanctumChat.off(event, callback)` - Remove event listener
- `SanctumChat.destroy()` - Destroy widget
- `SanctumChat.getState()` - Get current state
- `SanctumChat.getConfig()` - Get current configuration

### Events

- `open` - Chat window opened
- `close` - Chat window closed
- `message` - New message received
- `error` - Error occurred

### Properties

- `state.isInitialized` - Widget initialization status
- `state.isOpen` - Chat window open status
- `state.sessionId` - Current session ID
- `state.uid` - Current user ID
- `state.messageCount` - Total message count

## 🔄 Updates

The widget automatically checks for updates and can be configured to:

- Auto-update on version changes
- Notify users of new features
- Maintain backward compatibility

## 📞 Support

- **Documentation**: `/widget/` - Complete widget documentation
- **Demo**: `/widget/demo` - Interactive testing environment
- **Health**: `/widget/health` - Widget status check
- **API Docs**: `/api/docs` - API reference

## 📄 License

This widget is part of the Sanctum Chat system and follows the same licensing terms.

---

**Built with ❤️ for seamless customer communication**
