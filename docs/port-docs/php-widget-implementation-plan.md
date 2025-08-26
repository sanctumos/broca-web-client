# 🎯 PHP Web Widget Implementation Plan

## **📋 Project Overview**

This document outlines the complete implementation plan for creating a web widget system in the PHP version of Sanctum Web Chat. The widget will provide the exact same functionality as the Flask version, allowing users to embed a chat interface on any website.

## **🎯 Implementation Strategy**

### **Core Principles**
1. **Zero Core Changes**: Keep all existing PHP API routes and functionality untouched
2. **Parallel Widget System**: Create widget endpoints that mirror Flask widget functionality
3. **LEMP Compatible**: Use standard PHP includes and no server config modifications
4. **Same API Integration**: Widget will use the existing `/api/v1/?action=*` endpoints
5. **Feature Parity**: 100% identical functionality to Flask widget version

## **📁 File Structure**

```
php/public/
├── widget/                    # New widget directory
│   ├── index.php             # Widget documentation & embed instructions
│   ├── demo.php              # Interactive widget demo page
│   ├── embed.php             # Widget iframe endpoint
│   ├── init.php              # Widget initialization endpoint
│   ├── config.php             # Widget configuration endpoint
│   ├── health.php             # Widget health check endpoint
│   ├── assets/
│   │   ├── css/
│   │   │   └── widget.css    # Widget styles (copied from Flask)
│   │   ├── js/
│   │   │   └── chat-widget.js # Widget JavaScript (copied from Flask)
│   │   └── icons/
│   │       └── chat-icon.svg # Chat icon (copied from Flask)
│   └── templates/
│       └── widget.html       # Widget HTML template (copied from Flask)
├── web/                      # Existing web interface (unchanged)
├── api/                      # Existing API (unchanged)
└── config/                   # Existing config (unchanged)
```

## **🔧 Implementation Phases**

### **Phase 1: Core Widget Structure**
- [ ] Create `php/public/widget/` directory
- [ ] Copy static assets from Flask version (CSS, JS, icons)
- [ ] Create basic PHP routing structure
- [ ] Test static file serving

### **Phase 2: Widget Endpoints**
- [ ] Implement `/widget/` - Documentation page
- [ ] Implement `/widget/demo` - Interactive demo
- [ ] Implement `/widget/init` - Initialization endpoint
- [ ] Implement `/widget/config` - Configuration endpoint
- [ ] Implement `/widget/health` - Health check endpoint
- [ ] Implement `/widget/embed` - Iframe endpoint

### **Phase 3: PHP-Specific Adaptations**
- [ ] Adapt Flask templates to PHP/HTML
- [ ] Convert Flask route logic to PHP
- [ ] Integrate with existing PHP authentication system
- [ ] Test API integration with existing PHP endpoints

### **Phase 4: Testing & Validation**
- [ ] Test widget functionality
- [ ] Verify API integration
- [ ] Test cross-origin embedding
- [ ] Validate responsive design
- [ ] Test browser compatibility

## **📝 Detailed Implementation**

### **1. Widget Documentation Page (`/widget/`)**

**File**: `php/public/widget/index.php`
**Purpose**: Main widget documentation and embed instructions
**Content**: 
- Embed code examples
- Configuration options
- Integration guides
- Feature descriptions
- Demo link

**Implementation**:
```php
<?php
// Include common functions
require_once '../config/settings.php';
require_once '../includes/utils.php';

// Set page title and content
$page_title = "Sanctum Chat Widget - Embed Instructions";
$page_content = file_get_contents('templates/widget.html');

// Output the page
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($page_title); ?></title>
    <link rel="stylesheet" href="assets/css/widget.css">
</head>
<body>
    <?php echo $page_content; ?>
</body>
</html>
```

### **2. Widget Demo Page (`/widget/demo`)**

**File**: `php/public/widget/demo.php`
**Purpose**: Interactive testing environment for the widget
**Content**:
- Live widget instance
- Configuration controls
- Event logging
- Integration examples
- Testing tools

**Implementation**:
```php
<?php
require_once '../config/settings.php';
require_once '../includes/utils.php';

$page_title = "Sanctum Chat Widget - Interactive Demo";
$demo_content = file_get_contents('templates/widget_demo.html');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($page_title); ?></title>
    <link rel="stylesheet" href="assets/css/widget.css">
</head>
<body>
    <?php echo $demo_content; ?>
    <script src="assets/js/chat-widget.js"></script>
</body>
</html>
```

### **3. Widget Initialization Endpoint (`/widget/init`)**

**File**: `php/public/widget/init.php`
**Purpose**: Provide widget configuration and assets
**Functionality**:
- Validate API key
- Return configuration options
- Provide asset URLs
- Return API endpoint information

**Implementation**:
```php
<?php
require_once '../config/settings.php';
require_once '../includes/api_response.php';
require_once '../includes/auth.php';

// Set CORS headers
set_cors_headers();

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    send_error_response('Method not allowed', 405);
}

// Get configuration from query parameters
$config = [
    'apiKey' => $_GET['apiKey'] ?? '',
    'position' => $_GET['position'] ?? 'bottom-right',
    'theme' => $_GET['theme'] ?? 'light',
    'title' => $_GET['title'] ?? 'Chat with us',
    'primaryColor' => $_GET['primaryColor'] ?? '#007bff',
    'language' => $_GET['language'] ?? 'en',
    'autoOpen' => ($_GET['autoOpen'] ?? 'false') === 'true',
    'notifications' => ($_GET['notifications'] ?? 'true') === 'true',
    'sound' => ($_GET['sound'] ?? 'true') === 'true'
];

// Validate API key
if (empty($config['apiKey'])) {
    send_error_response('API key is required', 400);
}

// Return configuration
send_success_response([
    'config' => $config,
    'assets' => [
        'css' => '/widget/assets/css/widget.css',
        'js' => '/widget/assets/js/chat-widget.js',
        'icons' => '/widget/assets/icons/'
    ],
    'api' => [
        'baseUrl' => get_base_url(),
        'endpoint' => '/api/v1/'
    ]
], 'Widget configuration loaded');
```

### **4. Widget Configuration Endpoint (`/widget/config`)**

**File**: `php/public/widget/config.php`
**Purpose**: Return available widget configuration options
**Functionality**:
- List available positions
- List available themes
- List available languages
- Return default values

**Implementation**:
```php
<?php
require_once '../config/settings.php';
require_once '../includes/api_response.php';

set_cors_headers();

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    send_error_response('Method not allowed', 405);
}

send_success_response([
    'positions' => ['bottom-right', 'bottom-left', 'top-right', 'top-left'],
    'themes' => ['light', 'dark', 'auto'],
    'languages' => ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'],
    'defaults' => [
        'position' => 'bottom-right',
        'theme' => 'light',
        'title' => 'Chat with us',
        'primaryColor' => '#007bff',
        'language' => 'en',
        'autoOpen' => false,
        'notifications' => true,
        'sound' => true
    ]
], 'Configuration options loaded');
```

### **5. Widget Health Check Endpoint (`/widget/health`)**

**File**: `php/public/widget/health.php`
**Purpose**: Widget status and health information
**Functionality**:
- Widget status
- Version information
- API connection status
- System health

**Implementation**:
```php
<?php
require_once '../config/settings.php';
require_once '../includes/api_response.php';

set_cors_headers();

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    send_error_response('Method not allowed', 405);
}

// Check API connectivity
$api_status = 'connected';
try {
    // Test basic API functionality
    $test_response = file_get_contents(get_base_url() . '/api/v1/?action=config');
    if ($test_response === false) {
        $api_status = 'disconnected';
    }
} catch (Exception $e) {
    $api_status = 'error';
}

send_success_response([
    'status' => 'healthy',
    'version' => '1.0.0',
    'api_status' => $api_status,
    'timestamp' => date('c')
], 'Widget health check completed');
```

### **6. Widget Embed Endpoint (`/widget/embed`)**

**File**: `php/public/widget/embed.php`
**Purpose**: Iframe-compatible widget endpoint
**Functionality**:
- Standalone widget page
- Configurable via URL parameters
- Cross-origin compatible
- Mobile responsive

**Implementation**:
```php
<?php
require_once '../config/settings.php';
require_once '../includes/utils.php';

// Get configuration from query parameters
$api_key = $_GET['apiKey'] ?? '';
$position = $_GET['position'] ?? 'bottom-right';
$theme = $_GET['theme'] ?? 'light';
$title = $_GET['title'] ?? 'Chat with us';
$primary_color = $_GET['primaryColor'] ?? '#007bff';

// Validate API key
if (empty($api_key)) {
    http_response_code(400);
    echo '<html><body><h1>Error: API key required</h1></body></html>';
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($title); ?></title>
    <link rel="stylesheet" href="assets/css/widget.css">
    <style>
        body { margin: 0; padding: 0; }
        .sanctum-chat-widget { position: relative !important; }
    </style>
</head>
<body>
    <script>
        // Auto-initialize widget with URL parameters
        window.addEventListener('load', function() {
            if (typeof SanctumChat !== 'undefined') {
                SanctumChat.init({
                    apiKey: '<?php echo htmlspecialchars($api_key); ?>',
                    position: '<?php echo htmlspecialchars($position); ?>',
                    theme: '<?php echo htmlspecialchars($theme); ?>',
                    title: '<?php echo htmlspecialchars($title); ?>',
                    primaryColor: '<?php echo htmlspecialchars($primary_color); ?>',
                    autoOpen: true
                });
            }
        });
    </script>
    <script src="assets/js/chat-widget.js"></script>
</body>
</html>
```

## **📋 Static Assets to Copy**

### **CSS Files**
- **Source**: `python/app/widget/static/css/widget.css`
- **Destination**: `php/public/widget/assets/css/widget.css`
- **Changes**: None - direct copy

### **JavaScript Files**
- **Source**: `python/app/widget/static/js/chat-widget.js`
- **Destination**: `php/public/widget/assets/js/chat-widget.js`
- **Changes**: None - direct copy

### **Icon Files**
- **Source**: `python/app/widget/static/assets/icons/chat-icon.svg`
- **Destination**: `php/public/widget/assets/icons/chat-icon.svg`
- **Changes**: None - direct copy

### **HTML Templates**
- **Source**: `python/app/widget/templates/widget.html`
- **Destination**: `php/public/widget/templates/widget.html`
- **Changes**: Convert Flask template syntax to static HTML

- **Source**: `python/app/widget/templates/widget_demo.html`
- **Destination**: `php/public/widget/templates/widget_demo.html`
- **Changes**: Convert Flask template syntax to static HTML

## **🔌 API Integration Points**

### **Existing PHP API Endpoints Used**
1. **`/api/v1/?action=messages`** - Send messages
2. **`/api/v1/?action=inbox`** - Retrieve messages (for Broca plugin)
3. **`/api/v1/?action=outbox`** - Send responses (for Broca plugin)
4. **`/api/v1/?action=responses`** - Get responses
5. **`/api/v1/?action=sessions`** - Session management
6. **`/api/v1/?action=config`** - Configuration

### **No New API Endpoints Required**
- Widget uses existing API structure
- No modifications to existing PHP API code
- Maintains 100% backward compatibility

## **🎨 Customization & Theming**

### **CSS Variables**
- Primary color customization
- Theme switching (light/dark/auto)
- Position variants (8 corner positions)
- Responsive design breakpoints

### **Configuration Options**
- API key validation
- Position selection
- Theme selection
- Language selection
- Auto-open behavior
- Notification settings
- Sound settings

## **📱 Responsive Design**

### **Mobile Optimization**
- Touch-friendly interactions
- Adaptive sizing
- Mobile-specific positioning
- Responsive typography

### **Desktop Features**
- Hover effects
- Keyboard navigation
- Drag and drop (future enhancement)
- Multi-window support (future enhancement)

## **🔒 Security Considerations**

### **Authentication**
- Uses existing PHP API key system
- No new authentication mechanisms
- Inherits existing rate limiting
- Session isolation maintained

### **CORS & Cross-Origin**
- Proper CORS headers
- Cross-origin embedding support
- Input sanitization
- XSS protection

## **🧪 Testing Strategy**

### **Unit Testing**
- Widget endpoint functionality
- Configuration validation
- Error handling
- API integration

### **Integration Testing**
- End-to-end widget functionality
- Cross-origin embedding
- Mobile responsiveness
- Browser compatibility

### **User Acceptance Testing**
- Widget demo functionality
- Configuration options
- Embedding process
- Documentation clarity

## **📚 Documentation Requirements**

### **User Documentation**
- Embed instructions
- Configuration options
- Integration examples
- Troubleshooting guide

### **Developer Documentation**
- API integration details
- Customization guide
- Extension points
- Performance considerations

## **🚀 Deployment & Rollout**

### **Phase 1: Development**
- Implement core widget functionality
- Test with existing PHP API
- Validate cross-origin compatibility

### **Phase 2: Testing**
- Internal testing and validation
- User acceptance testing
- Performance testing
- Security testing

### **Phase 3: Production**
- Deploy to production environment
- Monitor widget performance
- Collect user feedback
- Iterate and improve

## **📊 Success Metrics**

### **Functional Metrics**
- Widget loads successfully
- Messages send/receive correctly
- Configuration options work
- Cross-origin embedding successful

### **Performance Metrics**
- Widget load time < 2 seconds
- Message response time < 500ms
- Mobile performance parity
- Browser compatibility > 95%

### **User Experience Metrics**
- Easy embedding process
- Clear documentation
- Responsive design
- Professional appearance

## **🔮 Future Enhancements**

### **Short Term**
- Additional theme options
- More positioning variants
- Enhanced mobile experience
- Performance optimizations

### **Long Term**
- Real-time WebSocket support
- Advanced customization options
- Analytics integration
- Multi-language support expansion

## **📝 Implementation Checklist**

### **Setup & Infrastructure**
- [ ] Create widget directory structure
- [ ] Copy static assets from Flask version
- [ ] Set up PHP routing
- [ ] Configure CORS headers

### **Core Endpoints**
- [ ] Implement widget documentation page
- [ ] Implement widget demo page
- [ ] Implement initialization endpoint
- [ ] Implement configuration endpoint
- [ ] Implement health check endpoint
- [ ] Implement embed endpoint

### **Integration & Testing**
- [ ] Test API integration
- [ ] Validate cross-origin functionality
- [ ] Test mobile responsiveness
- [ ] Verify browser compatibility
- [ ] Test error handling

### **Documentation & Deployment**
- [ ] Create user documentation
- [ ] Create developer documentation
- [ ] Deploy to test environment
- [ ] Deploy to production
- [ ] Monitor and iterate

## **🎯 Conclusion**

This implementation plan provides a comprehensive roadmap for creating a PHP web widget that maintains 100% feature parity with the Flask version while preserving the existing PHP API structure. The approach ensures zero impact on existing functionality while providing users with the same powerful embedding capabilities.

The widget will be fully LEMP compatible, require no server configuration changes, and integrate seamlessly with the existing PHP authentication and rate limiting systems. Users will be able to embed the chat widget on any website using simple JavaScript code, just like with the Flask version.

---

**Next Steps**: Begin Phase 1 implementation by creating the widget directory structure and copying static assets from the Flask version.
