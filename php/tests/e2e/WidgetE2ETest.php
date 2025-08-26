<?php
/**
 * End-to-End Tests for Widget System
 */

use PHPUnit\Framework\TestCase;

class WidgetE2ETest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        TestUtils::setupTestEnvironment();
    }
    
    protected function tearDown(): void
    {
        TestUtils::cleanupTestEnvironment();
        parent::tearDown();
    }
    
    /**
     * Test complete widget lifecycle
     */
    public function testCompleteWidgetLifecycle()
    {
        // Phase 1: Configuration Discovery
        $this->testConfigurationDiscovery();
        
        // Phase 2: Widget Initialization
        $this->testWidgetInitialization();
        
        // Phase 3: Health Monitoring
        $this->testHealthMonitoring();
        
        // Phase 4: Configuration Updates
        $this->testConfigurationUpdates();
        
        // Phase 5: Error Recovery
        $this->testErrorRecovery();
    }
    
    /**
     * Test configuration discovery phase
     */
    private function testConfigurationDiscovery()
    {
        // Get available configuration options
        TestUtils::mockRequest('GET', '/widget/config');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/config.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        $this->assertTrue($response['success']);
        
        // Verify all required configuration options are available
        $requiredOptions = ['positions', 'themes', 'languages', 'defaults'];
        foreach ($requiredOptions as $option) {
            $this->assertArrayHasKey($option, $response['data']);
            $this->assertNotEmpty($response['data'][$option]);
        }
        
        // Store configuration for later use
        $this->configOptions = $response['data'];
    }
    
    /**
     * Test widget initialization phase
     */
    private function testWidgetInitialization()
    {
        // Test initialization with each available position
        foreach ($this->configOptions['positions'] as $position) {
            $config = TestUtils::getTestWidgetConfig();
            $config['position'] = $position;
            
            TestUtils::mockRequest('GET', '/widget/init', $config);
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/init.php';
            });
            
            $response = TestUtils::assertJsonResponse($output);
            $this->assertTrue($response['success'], "Failed to initialize with position: $position");
            $this->assertEquals($position, $response['data']['config']['position']);
        }
        
        // Test initialization with each available theme
        foreach ($this->configOptions['themes'] as $theme) {
            $config = TestUtils::getTestWidgetConfig();
            $config['theme'] = $theme;
            
            TestUtils::mockRequest('GET', '/widget/init', $config);
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/init.php';
            });
            
            $response = TestUtils::assertJsonResponse($output);
            $this->assertTrue($response['success'], "Failed to initialize with theme: $theme");
            $this->assertEquals($theme, $response['data']['config']['theme']);
        }
        
        // Test initialization with each available language
        foreach ($this->configOptions['languages'] as $language) {
            $config = TestUtils::getTestWidgetConfig();
            $config['language'] = $language;
            
            TestUtils::mockRequest('GET', '/widget/init', $config);
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/init.php';
            });
            
            $response = TestUtils::assertJsonResponse($output);
            $this->assertTrue($response['success'], "Failed to initialize with language: $language");
            $this->assertEquals($language, $response['data']['config']['language']);
        }
    }
    
    /**
     * Test health monitoring phase
     */
    private function testHealthMonitoring()
    {
        // Perform multiple health checks
        for ($i = 0; $i < 3; $i++) {
            TestUtils::mockRequest('GET', '/widget/health');
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/health.php';
            });
            
            $response = TestUtils::assertJsonResponse($output);
            $this->assertTrue($response['success'], "Health check $i failed");
            $this->assertEquals('healthy', $response['data']['status']);
            $this->assertArrayHasKey('api_status', $response['data']);
            
            // Small delay between checks
            usleep(100000); // 0.1 seconds
        }
    }
    
    /**
     * Test configuration updates phase
     */
    private function testConfigurationUpdates()
    {
        $baseConfig = TestUtils::getTestWidgetConfig();
        
        // Test various configuration combinations
        $testConfigs = [
            // Minimal config
            ['apiKey' => $baseConfig['apiKey']],
            
            // Full custom config
            [
                'apiKey' => $baseConfig['apiKey'],
                'position' => 'top-left',
                'theme' => 'dark',
                'title' => 'Custom E2E Widget',
                'primaryColor' => '#ff6600',
                'language' => 'es',
                'autoOpen' => 'true',
                'notifications' => 'false',
                'sound' => 'false'
            ],
            
            // Mixed config
            [
                'apiKey' => $baseConfig['apiKey'],
                'position' => 'bottom-left',
                'theme' => 'auto',
                'title' => 'Mixed Config Widget',
                'primaryColor' => '#00ff00'
            ]
        ];
        
        foreach ($testConfigs as $i => $config) {
            TestUtils::mockRequest('GET', '/widget/init', $config);
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/init.php';
            });
            
            $response = TestUtils::assertJsonResponse($output);
            $this->assertTrue($response['success'], "Config $i failed");
            
            // Verify all provided values are correctly set
            foreach ($config as $key => $value) {
                if ($key === 'apiKey') {
                    $this->assertEquals($value, $response['data']['config'][$key]);
                }
            }
        }
    }
    
    /**
     * Test error recovery phase
     */
    private function testErrorRecovery()
    {
        // Test invalid requests
        $invalidRequests = [
            ['method' => 'POST', 'params' => TestUtils::getTestWidgetConfig()],
            ['method' => 'GET', 'params' => []],
            ['method' => 'GET', 'params' => ['apiKey' => '']],
            ['method' => 'PUT', 'params' => TestUtils::getTestWidgetConfig()]
        ];
        
        foreach ($invalidRequests as $i => $request) {
            TestUtils::mockRequest($request['method'], '/widget/init', $request['params']);
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/init.php';
            });
            
            $response = TestUtils::assertJsonResponse($output);
            $this->assertFalse($response['success'], "Invalid request $i should have failed");
            $this->assertArrayHasKey('error', $response);
        }
        
        // Test recovery with valid request
        TestUtils::mockRequest('GET', '/widget/init', TestUtils::getTestWidgetConfig());
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/init.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        $this->assertTrue($response['success'], 'Valid request should succeed after errors');
    }
    
    /**
     * Test widget performance under load
     */
    public function testWidgetPerformanceUnderLoad()
    {
        $startTime = microtime(true);
        $successCount = 0;
        $totalRequests = 10;
        
        // Make multiple concurrent-like requests
        for ($i = 0; $i < $totalRequests; $i++) {
            $config = TestUtils::getTestWidgetConfig();
            $config['title'] = "Performance Test Widget $i";
            
            TestUtils::mockRequest('GET', '/widget/init', $config);
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/init.php';
            });
            
            $response = TestUtils::assertJsonResponse($output);
            if ($response['success']) {
                $successCount++;
            }
        }
        
        $endTime = microtime(true);
        $totalTime = $endTime - $startTime;
        $avgTime = $totalTime / $totalRequests;
        
        // Performance assertions
        $this->assertEquals($totalRequests, $successCount, 'All requests should succeed');
        $this->assertLessThan(5.0, $totalTime, "Total time should be under 5 seconds, got: $totalTime");
        $this->assertLessThan(0.5, $avgTime, "Average time should be under 0.5 seconds, got: $avgTime");
    }
    
    /**
     * Test widget with extreme configuration values
     */
    public function testWidgetWithExtremeConfigurationValues()
    {
        $extremeConfigs = [
            // Very long title
            [
                'apiKey' => TestUtils::createTestApiKey(),
                'title' => str_repeat('A', 1000)
            ],
            
            // Very long API key
            [
                'apiKey' => str_repeat('a', 1000),
                'title' => 'Extreme API Key Test'
            ],
            
            // Special characters in title
            [
                'apiKey' => TestUtils::createTestApiKey(),
                'title' => 'Widget with special chars: !@#$%^&*()_+-=[]{}|;:,.<>?'
            ],
            
            // Unicode characters
            [
                'apiKey' => TestUtils::createTestApiKey(),
                'title' => 'Widget with unicode: 🚀🎯✨🔥💻📱🌐🔒'
            ]
        ];
        
        foreach ($extremeConfigs as $i => $config) {
            TestUtils::mockRequest('GET', '/widget/init', $config);
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/init.php';
            });
            
            $response = TestUtils::assertJsonResponse($output);
            $this->assertTrue($response['success'], "Extreme config $i failed");
            
            // Verify the extreme values are handled correctly
            $this->assertEquals($config['apiKey'], $response['data']['config']['apiKey']);
            if (isset($config['title'])) {
                $this->assertEquals($config['title'], $response['data']['config']['title']);
            }
        }
    }
    
    /**
     * Test widget CORS handling
     */
    public function testWidgetCORSHandling()
    {
        // Test OPTIONS requests for all endpoints
        $endpoints = ['/widget/init', '/widget/config', '/widget/health'];
        
        foreach ($endpoints as $endpoint) {
            TestUtils::mockRequest('OPTIONS', $endpoint);
            
            $output = TestUtils::captureOutput(function() use ($endpoint) {
                if ($endpoint === '/widget/init') {
                    require_once __DIR__ . '/../../public/widget/init.php';
                } elseif ($endpoint === '/widget/config') {
                    require_once __DIR__ . '/../../public/widget/config.php';
                } elseif ($endpoint === '/widget/health') {
                    require_once __DIR__ . '/../../public/widget/health.php';
                }
            });
            
            // OPTIONS requests should exit early
            $this->assertEmpty($output, "OPTIONS request to $endpoint should exit early");
        }
    }
}
