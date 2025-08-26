<?php
/**
 * Unit Tests for Widget Config Endpoint
 */

use PHPUnit\Framework\TestCase;

class WidgetConfigTest extends TestCase
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
     * Test successful config retrieval
     */
    public function testSuccessfulConfigRetrieval()
    {
        TestUtils::mockRequest('GET', '/widget/config');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/config.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $this->assertTrue($response['success']);
        $this->assertEquals('Configuration options loaded', $response['message']);
        $this->assertArrayHasKey('positions', $response['data']);
        $this->assertArrayHasKey('themes', $response['data']);
        $this->assertArrayHasKey('languages', $response['data']);
        $this->assertArrayHasKey('defaults', $response['data']);
    }
    
    /**
     * Test available positions
     */
    public function testAvailablePositions()
    {
        TestUtils::mockRequest('GET', '/widget/config');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/config.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $expectedPositions = ['bottom-right', 'bottom-left', 'top-right', 'top-left'];
        $this->assertEquals($expectedPositions, $response['data']['positions']);
        
        // Verify each position is valid
        foreach ($response['data']['positions'] as $position) {
            $this->assertContains($position, $expectedPositions);
        }
    }
    
    /**
     * Test available themes
     */
    public function testAvailableThemes()
    {
        TestUtils::mockRequest('GET', '/widget/config');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/config.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $expectedThemes = ['light', 'dark', 'auto'];
        $this->assertEquals($expectedThemes, $response['data']['themes']);
        
        // Verify each theme is valid
        foreach ($response['data']['themes'] as $theme) {
            $this->assertContains($theme, $expectedThemes);
        }
    }
    
    /**
     * Test available languages
     */
    public function testAvailableLanguages()
    {
        TestUtils::mockRequest('GET', '/widget/config');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/config.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $expectedLanguages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'];
        $this->assertEquals($expectedLanguages, $response['data']['languages']);
        
        // Verify each language is valid
        foreach ($response['data']['languages'] as $language) {
            $this->assertContains($language, $expectedLanguages);
        }
    }
    
    /**
     * Test default configuration values
     */
    public function testDefaultConfigurationValues()
    {
        TestUtils::mockRequest('GET', '/widget/config');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/config.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $defaults = $response['data']['defaults'];
        
        // Verify default values
        $this->assertEquals('bottom-right', $defaults['position']);
        $this->assertEquals('light', $defaults['theme']);
        $this->assertEquals('Chat with us', $defaults['title']);
        $this->assertEquals('#007bff', $defaults['primaryColor']);
        $this->assertEquals('en', $defaults['language']);
        $this->assertFalse($defaults['autoOpen']);
        $this->assertTrue($defaults['notifications']);
        $this->assertTrue($defaults['sound']);
    }
    
    /**
     * Test config with invalid HTTP method
     */
    public function testConfigInvalidMethod()
    {
        TestUtils::mockRequest('POST', '/widget/config');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/config.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $this->assertFalse($response['success']);
        $this->assertEquals('Method not allowed', $response['error']);
    }
    
    /**
     * Test config with OPTIONS request (CORS preflight)
     */
    public function testConfigOptionsRequest()
    {
        TestUtils::mockRequest('OPTIONS', '/widget/config');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/config.php';
        });
        
        // OPTIONS request should exit early
        $this->assertEmpty($output);
    }
    
    /**
     * Test config response structure
     */
    public function testConfigResponseStructure()
    {
        TestUtils::mockRequest('GET', '/widget/config');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/config.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        // Verify top-level structure
        $this->assertArrayHasKey('success', $response);
        $this->assertArrayHasKey('message', $response);
        $this->assertArrayHasKey('timestamp', $response);
        $this->assertArrayHasKey('data', $response);
        
        // Verify data structure
        $data = $response['data'];
        $this->assertArrayHasKey('positions', $data);
        $this->assertArrayHasKey('themes', $data);
        $this->assertArrayHasKey('languages', $data);
        $this->assertArrayHasKey('defaults', $data);
        
        // Verify data types
        $this->assertIsArray($data['positions']);
        $this->assertIsArray($data['themes']);
        $this->assertIsArray($data['languages']);
        $this->assertIsArray($data['defaults']);
        
        // Verify non-empty arrays
        $this->assertNotEmpty($data['positions']);
        $this->assertNotEmpty($data['themes']);
        $this->assertNotEmpty($data['languages']);
        $this->assertNotEmpty($data['defaults']);
    }
}
