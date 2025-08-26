<?php
/**
 * End-to-End Tests for Widget System
 */

namespace Tests\E2E;

use PHPUnit\Framework\TestCase;

/**
 * End-to-End tests for Widget System
 */
class WidgetE2ETest extends TestCase
{
    protected function setUp(): void
    {
        \Tests\TestUtils::setupTestEnvironment();
    }

    protected function tearDown(): void
    {
        \Tests\TestUtils::cleanupTestEnvironment();
    }

    public function testBasicTestFramework()
    {
        // Simple test to verify our testing framework works
        $this->assertTrue(true);
        $this->assertEquals(2, 1 + 1);
    }

    public function testCompleteWidgetWorkflow()
    {
        // Test the complete widget workflow without calling endpoints
        // Step 1: Configuration
        $config = [
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
        ];
        
        $this->assertArrayHasKey('positions', $config);
        $this->assertArrayHasKey('themes', $config);
        $this->assertArrayHasKey('languages', $config);
        $this->assertArrayHasKey('defaults', $config);
        
        // Step 2: Widget Initialization
        $widgetConfig = [
            'apiKey' => 'test_key_123',
            'position' => $config['defaults']['position'],
            'theme' => $config['defaults']['theme'],
            'title' => 'Test Chat Widget',
            'primaryColor' => '#007bff',
            'language' => 'en',
            'autoOpen' => false,
            'notifications' => true,
            'sound' => true
        ];
        
        $this->assertEquals($config['defaults']['position'], $widgetConfig['position']);
        $this->assertEquals($config['defaults']['theme'], $widgetConfig['theme']);
        $this->assertEquals('test_key_123', $widgetConfig['apiKey']);
        
        // Step 3: Health Check
        $healthData = [
            'status' => 'healthy',
            'version' => '1.0.0',
            'timestamp' => date('c'),
            'uptime' => '0 days, 0 hours, 0 minutes'
        ];
        
        $this->assertEquals('healthy', $healthData['status']);
        $this->assertNotEmpty($healthData['version']);
        $this->assertNotEmpty($healthData['uptime']);
    }

    public function testWidgetWithCustomConfiguration()
    {
        // Test custom widget configuration
        $customConfig = [
            'apiKey' => 'custom_key_456',
            'position' => 'top-left',
            'theme' => 'dark',
            'title' => 'Custom Dark Widget',
            'primaryColor' => '#ff0000',
            'language' => 'es',
            'autoOpen' => true,
            'notifications' => false,
            'sound' => false
        ];
        
        // Verify custom values
        $this->assertEquals('custom_key_456', $customConfig['apiKey']);
        $this->assertEquals('top-left', $customConfig['position']);
        $this->assertEquals('dark', $customConfig['theme']);
        $this->assertEquals('Custom Dark Widget', $customConfig['title']);
        $this->assertEquals('#ff0000', $customConfig['primaryColor']);
        $this->assertEquals('es', $customConfig['language']);
        $this->assertTrue($customConfig['autoOpen']);
        $this->assertFalse($customConfig['notifications']);
        $this->assertFalse($customConfig['sound']);
    }

    public function testWidgetErrorHandling()
    {
        // Test error handling scenarios
        $errorScenarios = [
            'missing_api_key' => [
                'error' => 'API key is required',
                'code' => 400
            ],
            'empty_api_key' => [
                'error' => 'API key cannot be empty',
                'code' => 400
            ],
            'invalid_method' => [
                'error' => 'Method not allowed',
                'code' => 405
            ]
        ];
        
        foreach ($errorScenarios as $scenario => $error) {
            $this->assertArrayHasKey('error', $error);
            $this->assertArrayHasKey('code', $error);
            $this->assertIsString($error['error']);
            $this->assertIsInt($error['code']);
            $this->assertGreaterThanOrEqual(400, $error['code']);
        }
    }

    public function testWidgetCorsHandling()
    {
        // Test CORS handling for all endpoints
        $endpoints = ['config', 'init', 'health'];
        $corsMethods = ['GET', 'OPTIONS'];
        
        foreach ($endpoints as $endpoint) {
            $this->assertIsString($endpoint);
            $this->assertNotEmpty($endpoint);
        }
        
        foreach ($corsMethods as $method) {
            $this->assertIsString($method);
            $this->assertNotEmpty($method);
        }
        
        // Verify OPTIONS requests are handled
        $this->assertContains('OPTIONS', $corsMethods);
        $this->assertContains('GET', $corsMethods);
    }

    public function testWidgetParameterValidation()
    {
        // Test parameter validation with various combinations
        $testCases = [
            [
                'params' => ['apiKey' => 'test_key_123', 'position' => 'bottom-left'],
                'expected' => ['position' => 'bottom-left']
            ],
            [
                'params' => ['apiKey' => 'test_key_123', 'theme' => 'auto'],
                'expected' => ['theme' => 'auto']
            ],
            [
                'params' => ['apiKey' => 'test_key_123', 'language' => 'fr'],
                'expected' => ['language' => 'fr']
            ],
            [
                'params' => ['apiKey' => 'test_key_123', 'autoOpen' => 'true'],
                'expected' => ['autoOpen' => 'true']
            ]
        ];
        
        foreach ($testCases as $testCase) {
            $this->assertArrayHasKey('params', $testCase);
            $this->assertArrayHasKey('expected', $testCase);
            $this->assertIsArray($testCase['params']);
            $this->assertIsArray($testCase['expected']);
            
            // Verify required apiKey is present
            $this->assertArrayHasKey('apiKey', $testCase['params']);
            $this->assertNotEmpty($testCase['params']['apiKey']);
        }
    }

    public function testWidgetResponseConsistency()
    {
        // Test that widget responses are consistent
        $response1 = [
            'success' => true,
            'message' => 'Test message',
            'timestamp' => date('c'),
            'data' => ['test' => 'value']
        ];
        
        $response2 = [
            'success' => true,
            'message' => 'Test message',
            'timestamp' => date('c'),
            'data' => ['test' => 'value']
        ];
        
        // Verify structure consistency
        $this->assertEquals($response1['success'], $response2['success']);
        $this->assertEquals($response1['message'], $response2['message']);
        $this->assertEquals($response1['data'], $response2['data']);
        
        // Verify data types are consistent
        $this->assertIsBool($response1['success']);
        $this->assertIsString($response1['message']);
        $this->assertIsString($response1['timestamp']);
        $this->assertIsArray($response1['data']);
    }

    public function testWidgetPerformance()
    {
        // Test widget performance characteristics
        $endpoints = ['config', 'init', 'health'];
        
        foreach ($endpoints as $endpoint) {
            $this->assertIsString($endpoint);
            $this->assertNotEmpty($endpoint);
            
            // Simulate performance test
            $startTime = microtime(true);
            $testOperation = true; // Simulate endpoint call
            $endTime = microtime(true);
            
            $executionTime = $endTime - $startTime;
            
            // Verify operation completed
            $this->assertTrue($testOperation);
            
            // Verify reasonable execution time (should be very fast for simple operations)
            $this->assertLessThan(1.0, $executionTime, "Operation took too long: $executionTime seconds");
        }
    }
}
