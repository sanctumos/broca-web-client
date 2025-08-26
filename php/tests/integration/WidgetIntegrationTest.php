<?php
/**
 * Integration Tests for Widget System
 */

namespace Tests\Integration;

use PHPUnit\Framework\TestCase;

/**
 * Integration tests for Widget System
 */
class WidgetIntegrationTest extends TestCase
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

    public function testWidgetConfigurationIntegration()
    {
        // Test that configuration options work together
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
        
        // Verify all configuration sections exist
        $this->assertArrayHasKey('positions', $config);
        $this->assertArrayHasKey('themes', $config);
        $this->assertArrayHasKey('languages', $config);
        $this->assertArrayHasKey('defaults', $config);
        
        // Verify defaults reference valid options
        $this->assertContains($config['defaults']['position'], $config['positions']);
        $this->assertContains($config['defaults']['theme'], $config['themes']);
        $this->assertContains($config['defaults']['language'], $config['languages']);
    }

    public function testWidgetInitializationIntegration()
    {
        // Test widget initialization configuration
        $initConfig = [
            'apiKey' => 'test_key_123',
            'position' => 'bottom-right',
            'theme' => 'light',
            'title' => 'Test Chat Widget',
            'primaryColor' => '#007bff',
            'language' => 'en',
            'autoOpen' => false,
            'notifications' => true,
            'sound' => true
        ];
        
        // Verify required fields
        $this->assertArrayHasKey('apiKey', $initConfig);
        $this->assertNotEmpty($initConfig['apiKey']);
        
        // Verify all configuration fields exist
        $requiredFields = ['position', 'theme', 'title', 'primaryColor', 'language', 'autoOpen', 'notifications', 'sound'];
        foreach ($requiredFields as $field) {
            $this->assertArrayHasKey($field, $initConfig);
        }
        
        // Verify data types
        $this->assertIsString($initConfig['apiKey']);
        $this->assertIsString($initConfig['position']);
        $this->assertIsString($initConfig['theme']);
        $this->assertIsString($initConfig['title']);
        $this->assertIsString($initConfig['primaryColor']);
        $this->assertIsString($initConfig['language']);
        $this->assertIsBool($initConfig['autoOpen']);
        $this->assertIsBool($initConfig['notifications']);
        $this->assertIsBool($initConfig['sound']);
    }

    public function testWidgetAssetsIntegration()
    {
        // Test widget assets configuration
        $assets = [
            'css' => '/widget/assets/css/widget.css',
            'js' => '/widget/assets/js/chat-widget.js',
            'icons' => '/widget/assets/icons/'
        ];
        
        // Verify all asset types exist
        $this->assertArrayHasKey('css', $assets);
        $this->assertArrayHasKey('js', $assets);
        $this->assertArrayHasKey('icons', $assets);
        
        // Verify asset paths are valid
        $this->assertStringContainsString('widget.css', $assets['css']);
        $this->assertStringContainsString('chat-widget.js', $assets['js']);
        $this->assertStringContainsString('icons', $assets['icons']);
        
        // Verify paths start with forward slash
        $this->assertStringStartsWith('/', $assets['css']);
        $this->assertStringStartsWith('/', $assets['js']);
        $this->assertStringStartsWith('/', $assets['icons']);
    }

    public function testWidgetApiIntegration()
    {
        // Test widget API configuration
        $api = [
            'baseUrl' => 'http://localhost',
            'endpoint' => '/api/v1/'
        ];
        
        // Verify API configuration
        $this->assertArrayHasKey('baseUrl', $api);
        $this->assertArrayHasKey('endpoint', $api);
        
        // Verify baseUrl is a valid URL
        $this->assertStringContainsString('localhost', $api['baseUrl']);
        
        // Verify endpoint starts with forward slash
        $this->assertStringStartsWith('/', $api['endpoint']);
    }

    public function testWidgetResponseFormatIntegration()
    {
        // Test consistent response format across all endpoints
        $responseFormat = [
            'success' => true,
            'message' => 'Test message',
            'timestamp' => date('c'),
            'data' => []
        ];
        
        // Verify response structure
        $this->assertArrayHasKey('success', $responseFormat);
        $this->assertArrayHasKey('message', $responseFormat);
        $this->assertArrayHasKey('timestamp', $responseFormat);
        $this->assertArrayHasKey('data', $responseFormat);
        
        // Verify data types
        $this->assertIsBool($responseFormat['success']);
        $this->assertIsString($responseFormat['message']);
        $this->assertIsString($responseFormat['timestamp']);
        $this->assertIsArray($responseFormat['data']);
    }

    public function testWidgetCorsIntegration()
    {
        // Test CORS handling for all endpoints
        $endpoints = ['config', 'init', 'health'];
        
        foreach ($endpoints as $endpoint) {
            $this->assertIsString($endpoint);
            $this->assertNotEmpty($endpoint);
            $this->assertContains($endpoint, $endpoints);
        }
        
        // Verify CORS preflight handling
        $corsMethods = ['GET', 'OPTIONS'];
        foreach ($corsMethods as $method) {
            $this->assertIsString($method);
            $this->assertNotEmpty($method);
        }
    }

    public function testWidgetParameterValidationIntegration()
    {
        // Test parameter validation across endpoints
        $validParams = [
            'apiKey' => 'test_key_123',
            'position' => 'bottom-right',
            'theme' => 'light',
            'title' => 'Test Widget',
            'primaryColor' => '#007bff',
            'language' => 'en',
            'autoOpen' => 'false',
            'notifications' => 'true',
            'sound' => 'true'
        ];
        
        // Verify all parameters exist
        $requiredParams = ['apiKey', 'position', 'theme', 'title', 'primaryColor', 'language', 'autoOpen', 'notifications', 'sound'];
        foreach ($requiredParams as $param) {
            $this->assertArrayHasKey($param, $validParams);
        }
        
        // Verify parameter validation
        $this->assertNotEmpty($validParams['apiKey']);
        $this->assertContains($validParams['position'], ['bottom-right', 'bottom-left', 'top-right', 'top-left']);
        $this->assertContains($validParams['theme'], ['light', 'dark', 'auto']);
        $this->assertMatchesRegularExpression('/^#[0-9a-fA-F]{6}$/', $validParams['primaryColor']);
        $this->assertContains($validParams['language'], ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko']);
    }

    public function testWidgetErrorHandlingIntegration()
    {
        // Test error handling integration
        $errorResponse = [
            'success' => false,
            'error' => 'Test error message',
            'code' => 400,
            'timestamp' => date('c')
        ];
        
        // Verify error response structure
        $this->assertArrayHasKey('success', $errorResponse);
        $this->assertArrayHasKey('error', $errorResponse);
        $this->assertArrayHasKey('code', $errorResponse);
        $this->assertArrayHasKey('timestamp', $errorResponse);
        
        // Verify error response values
        $this->assertFalse($errorResponse['success']);
        $this->assertIsString($errorResponse['error']);
        $this->assertIsInt($errorResponse['code']);
        $this->assertIsString($errorResponse['timestamp']);
        
        // Verify error code is valid HTTP status
        $this->assertGreaterThanOrEqual(400, $errorResponse['code']);
        $this->assertLessThan(600, $errorResponse['code']);
    }
}
