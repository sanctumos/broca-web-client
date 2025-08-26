<?php
/**
 * Unit Tests for Widget Config Endpoint
 */

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;

/**
 * Unit tests for Widget Configuration Endpoint
 */
class WidgetConfigTest extends TestCase
{
    protected function setUp(): void
    {
        \Tests\TestUtils::setupTestEnvironment();
    }

    protected function tearDown(): void
    {
        \Tests\TestUtils::cleanupTestEnvironment();
    }

    public function testConfigEndpointReturnsValidJson()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('config');
        
        $this->assertNotEmpty($output);
        
        $data = json_decode($output, true);
        $this->assertNotNull($data, 'Response should be valid JSON');
        $this->assertIsArray($data);
    }

    public function testConfigEndpointHasSuccessStructure()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('config');
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

    public function testConfigEndpointHasRequiredOptions()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('config');
        $data = json_decode($output, true);
        
        $this->assertArrayHasKey('positions', $data['data']);
        $this->assertArrayHasKey('themes', $data['data']);
        $this->assertArrayHasKey('languages', $data['data']);
        $this->assertArrayHasKey('defaults', $data['data']);
        
        $this->assertIsArray($data['data']['positions']);
        $this->assertIsArray($data['data']['themes']);
        $this->assertIsArray($data['data']['languages']);
        $this->assertIsArray($data['data']['defaults']);
    }

    public function testConfigEndpointHasValidPositions()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('config');
        $data = json_decode($output, true);
        
        $expectedPositions = ['bottom-right', 'bottom-left', 'top-right', 'top-left'];
        $this->assertEquals($expectedPositions, $data['data']['positions']);
    }

    public function testConfigEndpointHasValidThemes()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('config');
        $data = json_decode($output, true);
        
        $expectedThemes = ['light', 'dark', 'auto'];
        $this->assertEquals($expectedThemes, $data['data']['themes']);
    }

    public function testConfigEndpointHasValidLanguages()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('config');
        $data = json_decode($output, true);
        
        $expectedLanguages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'];
        $this->assertEquals($expectedLanguages, $data['data']['languages']);
    }

    public function testConfigEndpointHasValidDefaults()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('config');
        $data = json_decode($output, true);
        
        $defaults = $data['data']['defaults'];
        
        $this->assertArrayHasKey('position', $defaults);
        $this->assertArrayHasKey('theme', $defaults);
        $this->assertArrayHasKey('title', $defaults);
        $this->assertArrayHasKey('primaryColor', $defaults);
        $this->assertArrayHasKey('language', $defaults);
        $this->assertArrayHasKey('autoOpen', $defaults);
        $this->assertArrayHasKey('notifications', $defaults);
        $this->assertArrayHasKey('sound', $defaults);
        
        $this->assertEquals('bottom-right', $defaults['position']);
        $this->assertEquals('light', $defaults['theme']);
        $this->assertEquals('Chat with us', $defaults['title']);
        $this->assertEquals('#007bff', $defaults['primaryColor']);
        $this->assertEquals('en', $defaults['language']);
        $this->assertFalse($defaults['autoOpen']);
        $this->assertTrue($defaults['notifications']);
        $this->assertTrue($defaults['sound']);
    }

    public function testConfigEndpointRejectsNonGetMethods()
    {
        $this->expectException(\Exception::class);
        
        // This should fail because the endpoint only accepts GET
        \Tests\TestUtils::testWidgetEndpoint('config', 'POST');
    }
}
