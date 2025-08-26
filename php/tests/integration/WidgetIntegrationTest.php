<?php
/**
 * Integration Tests for Widget System
 */

use PHPUnit\Framework\TestCase;

class WidgetIntegrationTest extends TestCase
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
     * Test complete widget initialization flow
     */
    public function testCompleteWidgetInitializationFlow()
    {
        // Step 1: Get configuration options
        TestUtils::mockRequest('GET', '/widget/config');
        
        $configOutput = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/config.php';
        });
        
        $configResponse = TestUtils::assertJsonResponse($configOutput);
        $this->assertTrue($configResponse['success']);
        
        // Step 2: Initialize widget with valid config
        $widgetConfig = TestUtils::getTestWidgetConfig();
        TestUtils::mockRequest('GET', '/widget/init', $widgetConfig);
        
        $initOutput = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/init.php';
        });
        
        $initResponse = TestUtils::assertJsonResponse($initOutput);
        $this->assertTrue($initResponse['success']);
        
        // Step 3: Check health
        TestUtils::mockRequest('GET', '/widget/health');
        
        $healthOutput = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/health.php';
        });
        
        $healthResponse = TestUtils::assertJsonResponse($healthOutput);
        $this->assertTrue($healthResponse['success']);
        
        // Verify consistency across all endpoints
        $this->assertEquals('1.0.0', $initResponse['data']['config']['version'] ?? $healthResponse['data']['version']);
    }
    
    /**
     * Test widget with different API keys
     */
    public function testWidgetWithDifferentApiKeys()
    {
        $apiKeys = [
            'test_api_key_123',
            'another_test_key',
            'key_with_special_chars_!@#$%',
            'very_long_api_key_' . str_repeat('a', 100)
        ];
        
        foreach ($apiKeys as $apiKey) {
            $config = TestUtils::getTestWidgetConfig();
            $config['apiKey'] = $apiKey;
            
            TestUtils::mockRequest('GET', '/widget/init', $config);
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/init.php';
            });
            
            $response = TestUtils::assertJsonResponse($output);
            $this->assertTrue($response['success'], "Failed with API key: $apiKey");
            $this->assertEquals($apiKey, $response['data']['config']['apiKey']);
        }
    }
    
    /**
     * Test widget with different positions
     */
    public function testWidgetWithDifferentPositions()
    {
        $positions = ['bottom-right', 'bottom-left', 'top-right', 'top-left'];
        
        foreach ($positions as $position) {
            $config = TestUtils::getTestWidgetConfig();
            $config['position'] = $position;
            
            TestUtils::mockRequest('GET', '/widget/init', $config);
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/init.php';
            });
            
            $response = TestUtils::assertJsonResponse($output);
            $this->assertTrue($response['success'], "Failed with position: $position");
            $this->assertEquals($position, $response['data']['config']['position']);
        }
    }
    
    /**
     * Test widget with different themes
     */
    public function testWidgetWithDifferentThemes()
    {
        $themes = ['light', 'dark', 'auto'];
        
        foreach ($themes as $theme) {
            $config = TestUtils::getTestWidgetConfig();
            $config['theme'] = $theme;
            
            TestUtils::mockRequest('GET', '/widget/init', $config);
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/init.php';
            });
            
            $response = TestUtils::assertJsonResponse($output);
            $this->assertTrue($response['success'], "Failed with theme: $theme");
            $this->assertEquals($theme, $response['data']['config']['theme']);
        }
    }
    
    /**
     * Test widget with different languages
     */
    public function testWidgetWithDifferentLanguages()
    {
        $languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'];
        
        foreach ($languages as $language) {
            $config = TestUtils::getTestWidgetConfig();
            $config['language'] = $language;
            
            TestUtils::mockRequest('GET', '/widget/init', $config);
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/init.php';
            });
            
            $response = TestUtils::assertJsonResponse($output);
            $this->assertTrue($response['success'], "Failed with language: $language");
            $this->assertEquals($language, $response['data']['config']['language']);
        }
    }
    
    /**
     * Test widget boolean configuration options
     */
    public function testWidgetBooleanConfigurationOptions()
    {
        $booleanOptions = [
            'autoOpen' => [true, false],
            'notifications' => [true, false],
            'sound' => [true, false]
        ];
        
        foreach ($booleanOptions as $option => $values) {
            foreach ($values as $value) {
                $config = TestUtils::getTestWidgetConfig();
                $config[$option] = $value ? 'true' : 'false';
                
                TestUtils::mockRequest('GET', '/widget/init', $config);
                
                $output = TestUtils::captureOutput(function() {
                    require_once __DIR__ . '/../../public/widget/init.php';
                });
                
                $response = TestUtils::assertJsonResponse($output);
                $this->assertTrue($response['success'], "Failed with $option: $value");
                $this->assertEquals($value, $response['data']['config'][$option]);
            }
        }
    }
    
    /**
     * Test widget color validation
     */
    public function testWidgetColorValidation()
    {
        $validColors = [
            '#007bff',
            '#ff0000',
            '#00ff00',
            '#0000ff',
            '#ffffff',
            '#000000',
            '#123456',
            '#abcdef'
        ];
        
        foreach ($validColors as $color) {
            $config = TestUtils::getTestWidgetConfig();
            $config['primaryColor'] = $color;
            
            TestUtils::mockRequest('GET', '/widget/init', $config);
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/init.php';
            });
            
            $response = TestUtils::assertJsonResponse($output);
            $this->assertTrue($response['success'], "Failed with color: $color");
            $this->assertEquals($color, $response['data']['config']['primaryColor']);
        }
    }
    
    /**
     * Test widget concurrent requests
     */
    public function testWidgetConcurrentRequests()
    {
        $configs = [];
        $responses = [];
        
        // Create multiple different configurations
        for ($i = 0; $i < 5; $i++) {
            $configs[] = [
                'apiKey' => 'test_key_' . $i,
                'position' => ['bottom-right', 'bottom-left', 'top-right', 'top-left'][$i % 4],
                'theme' => ['light', 'dark', 'auto'][$i % 3],
                'title' => 'Test Widget ' . $i
            ];
        }
        
        // Simulate concurrent requests
        foreach ($configs as $i => $config) {
            TestUtils::mockRequest('GET', '/widget/init', $config);
            
            $output = TestUtils::captureOutput(function() {
                require_once __DIR__ . '/../../public/widget/init.php';
            });
            
            $responses[] = TestUtils::assertJsonResponse($output);
        }
        
        // Verify all requests succeeded
        foreach ($responses as $i => $response) {
            $this->assertTrue($response['success'], "Request $i failed");
            $this->assertEquals($configs[$i]['apiKey'], $response['data']['config']['apiKey']);
            $this->assertEquals($configs[$i]['position'], $response['data']['config']['position']);
            $this->assertEquals($configs[$i]['theme'], $response['data']['config']['theme']);
            $this->assertEquals($configs[$i]['title'], $response['data']['config']['title']);
        }
    }
    
    /**
     * Test widget error handling integration
     */
    public function testWidgetErrorHandlingIntegration()
    {
        // Test missing API key
        TestUtils::mockRequest('GET', '/widget/init', []);
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/init.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        $this->assertFalse($response['success']);
        $this->assertEquals('API key is required', $response['error']);
        
        // Test invalid HTTP method
        TestUtils::mockRequest('POST', '/widget/init', TestUtils::getTestWidgetConfig());
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/init.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        $this->assertFalse($response['success']);
        $this->assertEquals('Method not allowed', $response['error']);
        
        // Test valid request after errors
        TestUtils::mockRequest('GET', '/widget/init', TestUtils::getTestWidgetConfig());
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/init.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        $this->assertTrue($response['success'], 'Valid request should succeed after errors');
    }
}
