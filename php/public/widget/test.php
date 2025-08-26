<?php
/**
 * Widget Test Page
 * Simple test to verify widget functionality
 */
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Widget Test</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .test-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .success { background: #d4edda; border-color: #c3e6cb; }
        .error { background: #f8d7da; border-color: #f5c6cb; }
        .info { background: #d1ecf1; border-color: #bee5eb; }
    </style>
</head>
<body>
    <h1>🧪 Widget Test Page</h1>
    
    <div class="test-section info">
        <h3>📋 Test Results</h3>
        <div id="test-results">Running tests...</div>
    </div>
    
    <div class="test-section">
        <h3>🔗 Test Links</h3>
        <ul>
            <li><a href="index.php" target="_blank">Widget Documentation</a></li>
            <li><a href="demo.php" target="_blank">Widget Demo</a></li>
            <li><a href="init.php?apiKey=test123" target="_blank">Widget Init</a></li>
            <li><a href="config.php" target="_blank">Widget Config</a></li>
            <li><a href="health.php" target="_blank">Widget Health</a></li>
            <li><a href="embed.php?apiKey=test123" target="_blank">Widget Embed</a></li>
        </ul>
    </div>
    
    <div class="test-section">
        <h3>🎯 Live Widget Test</h3>
        <p>If everything is working, you should see a chat widget below:</p>
        <div id="widget-container"></div>
    </div>
    
    <script>
        // Test widget functionality
        async function runTests() {
            const results = document.getElementById('test-results');
            const tests = [];
            
            // Test 1: Check if CSS loads
            try {
                const cssResponse = await fetch('assets/css/widget.css');
                if (cssResponse.ok) {
                    tests.push('✅ CSS loaded successfully');
                } else {
                    tests.push('❌ CSS failed to load');
                }
            } catch (e) {
                tests.push('❌ CSS load error: ' + e.message);
            }
            
            // Test 2: Check if JS loads
            try {
                const jsResponse = await fetch('assets/js/chat-widget.js');
                if (jsResponse.ok) {
                    tests.push('✅ JavaScript loaded successfully');
                } else {
                    tests.push('❌ JavaScript failed to load');
                }
            } catch (e) {
                tests.push('❌ JavaScript load error: ' + e.message);
            }
            
            // Test 3: Check if icon loads
            try {
                const iconResponse = await fetch('assets/icons/chat-icon.svg');
                if (iconResponse.ok) {
                    tests.push('✅ Icon loaded successfully');
                } else {
                    tests.push('❌ Icon failed to load');
                }
            } catch (e) {
                tests.push('❌ Icon load error: ' + e.message);
            }
            
            // Test 4: Check config endpoint
            try {
                const configResponse = await fetch('config.php');
                if (configResponse.ok) {
                    tests.push('✅ Config endpoint working');
                } else {
                    tests.push('❌ Config endpoint failed');
                }
            } catch (e) {
                tests.push('❌ Config endpoint error: ' + e.message);
            }
            
            // Test 5: Check health endpoint
            try {
                const healthResponse = await fetch('health.php');
                if (healthResponse.ok) {
                    tests.push('✅ Health endpoint working');
                } else {
                    tests.push('❌ Health endpoint failed');
                }
            } catch (e) {
                tests.push('❌ Health endpoint error: ' + e.message);
            }
            
            // Display results
            results.innerHTML = tests.join('<br>');
            
            // Load widget if tests pass
            if (tests.every(t => t.startsWith('✅'))) {
                loadWidget();
            }
        }
        
        function loadWidget() {
            // Load widget CSS and JS
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'assets/css/widget.css';
            document.head.appendChild(link);
            
            const script = document.createElement('script');
            script.src = 'assets/js/chat-widget.js';
            script.onload = function() {
                if (typeof SanctumChat !== 'undefined') {
                    SanctumChat.init({
                        apiKey: 'test123',
                        position: 'bottom-right',
                        theme: 'light',
                        title: 'Test Widget'
                    });
                    document.getElementById('test-results').innerHTML += '<br><br>🎉 <strong>Widget loaded successfully!</strong>';
                } else {
                    document.getElementById('test-results').innerHTML += '<br><br>❌ <strong>Widget failed to initialize</strong>';
                }
            };
            document.head.appendChild(script);
        }
        
        // Run tests when page loads
        window.addEventListener('load', runTests);
    </script>
</body>
</html>
