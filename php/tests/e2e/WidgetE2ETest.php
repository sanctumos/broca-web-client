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

    public function testCompleteWidgetWorkflow()
    {
        // Step 1: Get widget configuration
        $configOutput = \Tests\TestUtils::testWidgetEndpoint('config');
        $configData = json_decode($configOutput, true);
        
        $this->assertTrue($configData['success']);
        $this->assertArrayHasKey('positions', $configData['data']);
        $this->assertArrayHasKey('themes', $configData['data']);
        $this->assertArrayHasKey('languages', $configData['data']);
        $this->assertArrayHasKey('defaults', $configData['data']);
        
        // Step 2: Initialize widget with configuration
        $initOutput = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', [
            'apiKey' => 'test_key_123',
            'position' => $configData['data']['defaults']['position'],
            'theme' => $configData['data']['defaults']['theme'],
            'title' => 'Test Chat Widget',
            'primaryColor' => '#007bff',
            'language' => 'en',
            'autoOpen' => 'false',
            'notifications' => 'true',
            'sound' => 'true'
        ]);
        
        $initData = json_decode($initOutput, true);
        $this->assertTrue($initData['success']);
        $this->assertArrayHasKey('config', $initData['data']);
        $this->assertArrayHasKey('assets', $initData['data']);
        $this->assertArrayHasKey('api', $initData['data']);
        
        // Step 3: Verify configuration matches
        $config = $initData['data']['config'];
        $this->assertEquals('test_key_123', $config['apiKey']);
        $this->assertEquals($configData['data']['defaults']['position'], $config['position']);
        $this->assertEquals($configData['data']['defaults']['theme'], $config['theme']);
        $this->assertEquals('Test Chat Widget', $config['title']);
        $this->assertEquals('#007bff', $config['primaryColor']);
        $this->assertEquals('en', $config['language']);
        $this->assertFalse($config['autoOpen']);
        $this->assertTrue($config['notifications']);
        $this->assertTrue($config['sound']);
        
        // Step 4: Check health status
        $healthOutput = \Tests\TestUtils::testWidgetEndpoint('health');
        $healthData = json_decode($healthOutput, true);
        
        $this->assertTrue($healthData['success']);
        $this->assertArrayHasKey('status', $healthData['data']);
        $this->assertArrayHasKey('version', $healthData['data']);
        $this->assertArrayHasKey('timestamp', $healthData['data']);
        $this->assertArrayHasKey('uptime', $healthData['data']);
        
        $this->assertEquals('healthy', $healthData['data']['status']);
        $this->assertNotEmpty($healthData['data']['version']);
        $this->assertNotEmpty($healthData['data']['uptime']);
    }

    public function testWidgetWithCustomConfiguration()
    {
        // Test with custom position and theme
        $customConfig = [
            'apiKey' => 'custom_key_456',
            'position' => 'top-left',
            'theme' => 'dark',
            'title' => 'Custom Dark Widget',
            'primaryColor' => '#ff0000',
            'language' => 'es',
            'autoOpen' => 'true',
            'notifications' => 'false',
            'sound' => 'false'
        ];
        
        $output = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', $customConfig);
        $data = json_decode($output, true);
        
        $this->assertTrue($data['success']);
        
        $config = $data['data']['config'];
        $this->assertEquals('custom_key_456', $config['apiKey']);
        $this->assertEquals('top-left', $config['position']);
        $this->assertEquals('dark', $config['theme']);
        $this->assertEquals('Custom Dark Widget', $config['title']);
        $this->assertEquals('#ff0000', $config['primaryColor']);
        $this->assertEquals('es', $config['language']);
        $this->assertTrue($config['autoOpen']);
        $this->assertFalse($config['notifications']);
        $this->assertFalse($config['sound']);
    }

    public function testWidgetErrorHandling()
    {
        // Test missing API key
        $this->expectException(\Exception::class);
        \Tests\TestUtils::testWidgetEndpoint('init', 'GET', []);
        
        // Test empty API key
        $this->expectException(\Exception::class);
        \Tests\TestUtils::testWidgetEndpoint('init', 'GET', ['apiKey' => '']);
        
        // Test invalid HTTP method
        $this->expectException(\Exception::class);
        \Tests\TestUtils::testWidgetEndpoint('init', 'POST', ['apiKey' => 'test_key']);
    }

    public function testWidgetCorsHandling()
    {
        // Test OPTIONS request (CORS preflight)
        $endpoints = ['config', 'init', 'health'];
        
        foreach ($endpoints as $endpoint) {
            $params = [];
            if ($endpoint === 'init') {
                $params = ['apiKey' => 'test_key_123'];
            }
            
            $output = \Tests\TestUtils::testWidgetEndpoint($endpoint, 'OPTIONS', $params);
            $this->assertEmpty($output, "OPTIONS request to $endpoint should exit early");
        }
    }

    public function testWidgetParameterValidation()
    {
        // Test with various parameter combinations
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
                'expected' => ['autoOpen' => true]
            ]
        ];
        
        foreach ($testCases as $testCase) {
            $output = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', $testCase['params']);
            $data = json_decode($output, true);
            
            $this->assertTrue($data['success']);
            
            foreach ($testCase['expected'] as $key => $expectedValue) {
                $this->assertEquals($expectedValue, $data['data']['config'][$key]);
            }
        }
    }

    public function testWidgetResponseConsistency()
    {
        // Test that multiple calls to the same endpoint return consistent results
        $configOutput1 = \Tests\TestUtils::testWidgetEndpoint('config');
        $configOutput2 = \Tests\TestUtils::testWidgetEndpoint('config');
        
        $this->assertEquals($configOutput1, $configOutput2);
        
        $initOutput1 = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', ['apiKey' => 'test_key_123']);
        $initOutput2 = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', ['apiKey' => 'test_key_123']);
        
        $this->assertEquals($initOutput1, $initOutput2);
        
        $healthOutput1 = \Tests\TestUtils::testWidgetEndpoint('health');
        $healthOutput2 = \Tests\TestUtils::testWidgetEndpoint('health');
        
        $this->assertEquals($healthOutput1, $healthOutput2);
    }

    public function testWidgetPerformance()
    {
        // Test that endpoints respond within reasonable time
        $endpoints = ['config', 'init', 'health'];
        
        foreach ($endpoints as $endpoint) {
            $startTime = microtime(true);
            
            $params = [];
            if ($endpoint === 'init') {
                $params = ['apiKey' => 'test_key_123'];
            }
            
            $output = \Tests\TestUtils::testWidgetEndpoint($endpoint, 'GET', $params);
            
            $endTime = microtime(true);
            $executionTime = $endTime - $startTime;
            
            // Endpoints should respond within 1 second
            $this->assertLessThan(1.0, $executionTime, "Endpoint $endpoint took too long: $executionTime seconds");
            
            $data = json_decode($output, true);
            $this->assertTrue($data['success']);
        }
    }
}
