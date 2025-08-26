<?php
/**
 * Unit Tests for Widget Health Endpoint
 */

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;

/**
 * Unit tests for Widget Health Check Endpoint
 */
class WidgetHealthTest extends TestCase
{
    protected function setUp(): void
    {
        \Tests\TestUtils::setupTestEnvironment();
    }

    protected function tearDown(): void
    {
        \Tests\TestUtils::cleanupTestEnvironment();
    }

    public function testHealthEndpointReturnsValidJson()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('health');
        
        $this->assertNotEmpty($output);
        
        $data = json_decode($output, true);
        $this->assertNotNull($data, 'Response should be valid JSON');
        $this->assertIsArray($data);
    }

    public function testHealthEndpointHasSuccessStructure()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('health');
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

    public function testHealthEndpointHasRequiredData()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('health');
        $data = json_decode($output, true);
        
        $this->assertArrayHasKey('status', $data['data']);
        $this->assertArrayHasKey('version', $data['data']);
        $this->assertArrayHasKey('timestamp', $data['data']);
        $this->assertArrayHasKey('uptime', $data['data']);
        
        $this->assertIsString($data['data']['status']);
        $this->assertIsString($data['data']['version']);
        $this->assertIsString($data['data']['timestamp']);
        $this->assertIsString($data['data']['uptime']);
    }

    public function testHealthEndpointHasValidStatus()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('health');
        $data = json_decode($output, true);
        
        $this->assertEquals('healthy', $data['data']['status']);
    }

    public function testHealthEndpointHasValidVersion()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('health');
        $data = json_decode($output, true);
        
        $this->assertNotEmpty($data['data']['version']);
        $this->assertMatchesRegularExpression('/^\d+\.\d+\.\d+$/', $data['data']['version']);
    }

    public function testHealthEndpointHasValidTimestamp()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('health');
        $data = json_decode($output, true);
        
        $timestamp = strtotime($data['data']['timestamp']);
        $this->assertNotFalse($timestamp, 'Timestamp should be valid');
        
        $now = time();
        $this->assertLessThanOrEqual($now, $timestamp);
        $this->assertGreaterThan($now - 60, $timestamp); // Should be within last minute
    }

    public function testHealthEndpointHasValidUptime()
    {
        $output = \Tests\TestUtils::testWidgetEndpoint('health');
        $data = json_decode($output, true);
        
        $this->assertNotEmpty($data['data']['uptime']);
        $this->assertIsString($data['data']['uptime']);
    }

    public function testHealthEndpointRejectsNonGetMethods()
    {
        $this->expectException(\Exception::class);
        
        // This should fail because the endpoint only accepts GET
        \Tests\TestUtils::testWidgetEndpoint('health', 'POST');
    }
}
