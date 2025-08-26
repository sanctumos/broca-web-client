<?php
/**
 * Unit Tests for Widget Init Endpoint
 */

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;

/**
 * Unit tests for Widget Initialization Endpoint
 */
class WidgetInitTest extends TestCase
{
    protected function setUp(): void
    {
        \Tests\TestUtils::setupTestEnvironment();
    }

    protected function tearDown(): void
    {
        \Tests\TestUtils::cleanupTestEnvironment();
    }

    public function testInitEndpointReturnsValidJson()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', ['apiKey' => 'test_key_123']);
        
        $this->assertNotEmpty($output);
        
        $data = json_decode($output, true);
        $this->assertNotNull($data, 'Response should be valid JSON');
        $this->assertIsArray($data);
    }

    public function testInitEndpointHasSuccessStructure()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', ['apiKey' => 'test_key_123']);
        $data = json_decode($output, true);
        
        $this->assertArrayHasKey('success', $data);
        $this->assertArrayHasKey('message', $data);
        $this->assertArrayHasKey('timestamp', $data);
        $this->assertArrayHasKey('data', $data);
        
        $this->assertTrue($data['success']);
        $this->assertIsString($data['message']);
        $this->assertIsString($data['timestamp']);
        $this->assertIsArray($data['data']);
    }

    public function testInitEndpointHasRequiredData()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', ['apiKey' => 'test_key_123']);
        $data = json_decode($output, true);
        
        $this->assertArrayHasKey('config', $data['data']);
        $this->assertArrayHasKey('assets', $data['data']);
        $this->assertArrayHasKey('api', $data['data']);
        
        $this->assertIsArray($data['data']['config']);
        $this->assertIsArray($data['data']['assets']);
        $this->assertIsArray($data['data']['api']);
    }

    public function testInitEndpointHasValidConfig()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', ['apiKey' => 'test_key_123']);
        $data = json_decode($output, true);
        
        $config = $data['data']['config'];
        
        $this->assertArrayHasKey('apiKey', $config);
        $this->assertArrayHasKey('position', $config);
        $this->assertArrayHasKey('theme', $config);
        $this->assertArrayHasKey('title', $config);
        $this->assertArrayHasKey('primaryColor', $config);
        $this->assertArrayHasKey('language', $config);
        $this->assertArrayHasKey('autoOpen', $config);
        $this->assertArrayHasKey('notifications', $config);
        $this->assertArrayHasKey('sound', $config);
        
        $this->assertEquals('test_key_123', $config['apiKey']);
        $this->assertEquals('bottom-right', $config['position']);
        $this->assertEquals('light', $config['theme']);
        $this->assertEquals('Chat with us', $config['title']);
        $this->assertEquals('#007bff', $config['primaryColor']);
        $this->assertEquals('en', $config['language']);
        $this->assertFalse($config['autoOpen']);
        $this->assertTrue($config['notifications']);
        $this->assertTrue($config['sound']);
    }

    public function testInitEndpointHasValidAssets()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', ['apiKey' => 'test_key_123']);
        $data = json_decode($output, true);
        
        $assets = $data['data']['assets'];
        
        $this->assertArrayHasKey('css', $assets);
        $this->assertArrayHasKey('js', $assets);
        $this->assertArrayHasKey('icons', $assets);
        
        $this->assertEquals('/widget/assets/css/widget.css', $assets['css']);
        $this->assertEquals('/widget/assets/js/chat-widget.js', $assets['js']);
        $this->assertEquals('/widget/assets/icons/', $assets['icons']);
    }

    public function testInitEndpointHasValidApi()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', ['apiKey' => 'test_key_123']);
        $data = json_decode($output, true);
        
        $api = $data['data']['api'];
        
        $this->assertArrayHasKey('baseUrl', $api);
        $this->assertArrayHasKey('endpoint', $api);
        
        $this->assertIsString($api['baseUrl']);
        $this->assertEquals('/api/v1/', $api['endpoint']);
    }

    public function testInitEndpointRejectsMissingApiKey()
    {
        $this->expectException(\Exception::class);
        
        // This should fail because apiKey is required
        \Tests\TestUtils::testWidgetEndpoint('init', 'GET', []);
    }

    public function testInitEndpointRejectsEmptyApiKey()
    {
        $this->expectException(\Exception::class);
        
        // This should fail because apiKey cannot be empty
        \Tests\TestUtils::testWidgetEndpoint('init', 'GET', ['apiKey' => '']);
    }

    public function testInitEndpointRejectsNonGetMethods()
    {
        $this->expectException(\Exception::class);
        
        // This should fail because the endpoint only accepts GET
        \Tests\TestUtils::testWidgetEndpoint('init', 'POST', ['apiKey' => 'test_key_123']);
    }
}
