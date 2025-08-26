<?php
/**
 * Unit Tests for Widget Init Endpoint
 */

use PHPUnit\Framework\TestCase;

class WidgetInitTest extends TestCase
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
     * Test successful widget initialization
     */
    public function testSuccessfulWidgetInit()
    {
        $config = TestUtils::getTestWidgetConfig();
        
        TestUtils::mockRequest('GET', '/widget/init', $config);
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/init.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $this->assertTrue($response['success']);
        $this->assertEquals('Widget configuration loaded', $response['message']);
        $this->assertArrayHasKey('config', $response['data']);
        $this->assertArrayHasKey('assets', $response['data']);
        $this->assertArrayHasKey('api', $response['data']);
        
        // Verify config data
        $this->assertEquals($config['apiKey'], $response['data']['config']['apiKey']);
        $this->assertEquals($config['position'], $response['data']['config']['position']);
        $this->assertEquals($config['theme'], $response['data']['config']['theme']);
        
        // Verify assets
        $this->assertStringContainsString('widget.css', $response['data']['assets']['css']);
        $this->assertStringContainsString('chat-widget.js', $response['data']['assets']['js']);
        $this->assertStringContainsString('icons', $response['data']['assets']['icons']);
        
        // Verify API info
        $this->assertStringContainsString('localhost', $response['data']['api']['baseUrl']);
        $this->assertEquals('/api/v1/', $response['data']['api']['endpoint']);
    }
    
    /**
     * Test widget init with missing API key
     */
    public function testWidgetInitMissingApiKey()
    {
        $config = TestUtils::getTestWidgetConfig();
        unset($config['apiKey']);
        
        TestUtils::mockRequest('GET', '/widget/init', $config);
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/init.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $this->assertFalse($response['success']);
        $this->assertEquals('API key is required', $response['error']);
    }
    
    /**
     * Test widget init with empty API key
     */
    public function testWidgetInitEmptyApiKey()
    {
        $config = TestUtils::getTestWidgetConfig();
        $config['apiKey'] = '';
        
        TestUtils::mockRequest('GET', '/widget/init', $config);
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/init.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $this->assertFalse($response['success']);
        $this->assertEquals('API key is required', $response['error']);
    }
    
    /**
     * Test widget init with default values
     */
    public function testWidgetInitWithDefaults()
    {
        $config = ['apiKey' => TestUtils::createTestApiKey()];
        
        TestUtils::mockRequest('GET', '/widget/init', $config);
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/init.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $this->assertTrue($response['success']);
        
        // Verify default values
        $this->assertEquals('bottom-right', $response['data']['config']['position']);
        $this->assertEquals('light', $response['data']['config']['theme']);
        $this->assertEquals('Chat with us', $response['data']['config']['title']);
        $this->assertEquals('#007bff', $response['data']['config']['primaryColor']);
        $this->assertEquals('en', $response['data']['config']['language']);
        $this->assertFalse($response['data']['config']['autoOpen']);
        $this->assertTrue($response['data']['config']['notifications']);
        $this->assertTrue($response['data']['config']['sound']);
    }
    
    /**
     * Test widget init with custom values
     */
    public function testWidgetInitWithCustomValues()
    {
        $config = [
            'apiKey' => TestUtils::createTestApiKey(),
            'position' => 'top-left',
            'theme' => 'dark',
            'title' => 'Custom Chat Title',
            'primaryColor' => '#ff0000',
            'language' => 'es',
            'autoOpen' => 'true',
            'notifications' => 'false',
            'sound' => 'false'
        ];
        
        TestUtils::mockRequest('GET', '/widget/init', $config);
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/init.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $this->assertTrue($response['success']);
        
        // Verify custom values
        $this->assertEquals('top-left', $response['data']['config']['position']);
        $this->assertEquals('dark', $response['data']['config']['theme']);
        $this->assertEquals('Custom Chat Title', $response['data']['config']['title']);
        $this->assertEquals('#ff0000', $response['data']['config']['primaryColor']);
        $this->assertEquals('es', $response['data']['config']['language']);
        $this->assertTrue($response['data']['config']['autoOpen']);
        $this->assertFalse($response['data']['config']['notifications']);
        $this->assertFalse($response['data']['config']['sound']);
    }
    
    /**
     * Test widget init with invalid HTTP method
     */
    public function testWidgetInitInvalidMethod()
    {
        TestUtils::mockRequest('POST', '/widget/init', ['apiKey' => 'test']);
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/init.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $this->assertFalse($response['success']);
        $this->assertEquals('Method not allowed', $response['error']);
    }
    
    /**
     * Test widget init with OPTIONS request (CORS preflight)
     */
    public function testWidgetInitOptionsRequest()
    {
        TestUtils::mockRequest('OPTIONS', '/widget/init');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/init.php';
        });
        
        // OPTIONS request should exit early
        $this->assertEmpty($output);
    }
}
