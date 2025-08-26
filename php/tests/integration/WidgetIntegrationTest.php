<?php
/**
 * Integration Tests for Widget System
 */

namespace Tests\Integration;

use PHPUnit\Framework\TestCase;

/**
 * Integration tests for Widget Endpoints
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

    public function testConfigAndInitEndpointsWorkTogether()
    {
        // First get configuration
        $configOutput = \Tests\TestUtils::testWidgetEndpoint('config');
        $configData = json_decode($configOutput, true);
        
        $this->assertTrue($configData['success']);
        $this->assertArrayHasKey('positions', $configData['data']);
        $this->assertArrayHasKey('themes', $configData['data']);
        
        // Then use config to initialize widget
        $initOutput = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', [
            'apiKey' => 'test_key_123',
            'position' => $configData['data']['defaults']['position'],
            'theme' => $configData['data']['defaults']['theme']
        ]);
        
        $initData = json_decode($initOutput, true);
        $this->assertTrue($initData['success']);
        $this->assertEquals($configData['data']['defaults']['position'], $initData['data']['config']['position']);
        $this->assertEquals($configData['data']['defaults']['theme'], $initData['data']['config']['theme']);
    }

    public function testWidgetEndpointsHaveConsistentResponseFormat()
    {
        $endpoints = ['config', 'init', 'health'];
        
        foreach ($endpoints as $endpoint) {
            $params = [];
            if ($endpoint === 'init') {
                $params = ['apiKey' => 'test_key_123'];
            }
            
            $output = \Tests\TestUtils::testWidgetEndpoint($endpoint, 'GET', $params);
            $data = json_decode($output, true);
            
            $this->assertNotNull($data, "Endpoint $endpoint should return valid JSON");
            $this->assertArrayHasKey('success', $data, "Endpoint $endpoint should have success field");
            $this->assertArrayHasKey('message', $data, "Endpoint $endpoint should have message field");
            $this->assertArrayHasKey('timestamp', $data, "Endpoint $endpoint should have timestamp field");
            $this->assertArrayHasKey('data', $data, "Endpoint $endpoint should have data field");
        }
    }

    public function testWidgetEndpointsHandleCorsCorrectly()
    {
        $endpoints = ['config', 'init', 'health'];
        
        foreach ($endpoints as $endpoint) {
            $params = [];
            if ($endpoint === 'init') {
                $params = ['apiKey' => 'test_key_123'];
            }
            
            // Test OPTIONS request (CORS preflight)
            $output = \Tests\TestUtils::testWidgetEndpoint($endpoint, 'OPTIONS', $params);
            $this->assertEmpty($output, "OPTIONS request to $endpoint should exit early");
            
            // Test GET request (should work normally)
            $output = \Tests\TestUtils::testWidgetEndpoint($endpoint, 'GET', $params);
            $this->assertNotEmpty($output, "GET request to $endpoint should return data");
        }
    }

    public function testWidgetEndpointsRejectInvalidMethods()
    {
        $endpoints = ['config', 'init', 'health'];
        $invalidMethods = ['POST', 'PUT', 'DELETE', 'PATCH'];
        
        foreach ($endpoints as $endpoint) {
            foreach ($invalidMethods as $method) {
                $params = [];
                if ($endpoint === 'init') {
                    $params = ['apiKey' => 'test_key_123'];
                }
                
                $this->expectException(\Exception::class);
                \Tests\TestUtils::testWidgetEndpoint($endpoint, $method, $params);
            }
        }
    }

    public function testWidgetEndpointsMaintainStateIndependence()
    {
        // Test that one endpoint doesn't affect another
        $configOutput1 = \Tests\TestUtils::testWidgetEndpoint('config');
        $initOutput = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', ['apiKey' => 'test_key_123']);
        $configOutput2 = \Tests\TestUtils::testWidgetEndpoint('config');
        
        // Both config calls should return identical results
        $this->assertEquals($configOutput1, $configOutput2);
        
        // Parse and verify structure is maintained
        $configData1 = json_decode($configOutput1, true);
        $configData2 = json_decode($configOutput2, true);
        
        $this->assertEquals($configData1['data']['defaults'], $configData2['data']['defaults']);
    }

    public function testWidgetEndpointsHandleCustomParameters()
    {
        $customParams = [
            'position' => 'top-left',
            'theme' => 'dark',
            'title' => 'Custom Chat',
            'primaryColor' => '#ff0000',
            'language' => 'es',
            'autoOpen' => 'true',
            'notifications' => 'false',
            'sound' => 'false'
        ];
        
        $output = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', array_merge(
            ['apiKey' => 'test_key_123'],
            $customParams
        ));
        
        $data = json_decode($output, true);
        $this->assertTrue($data['success']);
        
        $config = $data['data']['config'];
        $this->assertEquals('top-left', $config['position']);
        $this->assertEquals('dark', $config['theme']);
        $this->assertEquals('Custom Chat', $config['title']);
        $this->assertEquals('#ff0000', $config['primaryColor']);
        $this->assertEquals('es', $config['language']);
        $this->assertTrue($config['autoOpen']);
        $this->assertFalse($config['notifications']);
        $this->assertFalse($config['sound']);
    }

    public function testWidgetEndpointsValidateRequiredParameters()
    {
        // Test init endpoint without required apiKey
        $this->expectException(\Exception::class);
        \Tests\TestUtils::testWidgetEndpoint('init', 'GET', []);
    }

    public function testWidgetEndpointsHandleEdgeCaseParameters()
    {
        // Test with very long values
        $longString = str_repeat('a', 1000);
        
        $output = \Tests\TestUtils::testWidgetEndpoint('init', 'GET', [
            'apiKey' => 'test_key_123',
            'title' => $longString,
            'primaryColor' => $longString
        ]);
        
        $data = json_decode($output, true);
        $this->assertTrue($data['success']);
        
        // Should handle long strings gracefully
        $this->assertEquals($longString, $data['data']['config']['title']);
        $this->assertEquals($longString, $data['data']['config']['primaryColor']);
    }
}
