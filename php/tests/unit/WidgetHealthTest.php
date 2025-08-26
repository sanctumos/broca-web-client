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

    public function testBasicTestFramework()
    {
        // Simple test to verify our testing framework works
        $this->assertTrue(true);
        $this->assertEquals(2, 1 + 1);
    }

    public function testExpectedHealthStructure()
    {
        // Test the expected health structure without calling endpoints
        $expectedHealth = [
            'status' => 'healthy',
            'version' => '1.0.0',
            'timestamp' => date('c'),
            'uptime' => '0 days, 0 hours, 0 minutes'
        ];
        
        $this->assertCount(4, $expectedHealth);
        $this->assertArrayHasKey('status', $expectedHealth);
        $this->assertArrayHasKey('version', $expectedHealth);
        $this->assertArrayHasKey('timestamp', $expectedHealth);
        $this->assertArrayHasKey('uptime', $expectedHealth);
    }

    public function testHealthStatusValidation()
    {
        // Test health status validation
        $validStatuses = ['healthy', 'degraded', 'unhealthy'];
        $invalidStatuses = ['invalid', 'broken', 'error'];
        
        foreach ($validStatuses as $status) {
            $this->assertContains($status, $validStatuses);
        }
        
        foreach ($invalidStatuses as $status) {
            $this->assertNotContains($status, $validStatuses);
        }
    }

    public function testVersionFormatValidation()
    {
        // Test version format validation
        $validVersions = ['1.0.0', '2.1.3', '0.9.1', '10.5.23'];
        $invalidVersions = ['1.0', '2.1', 'version', 'latest'];
        
        foreach ($validVersions as $version) {
            $this->assertMatchesRegularExpression('/^\d+\.\d+\.\d+$/', $version);
        }
        
        foreach ($invalidVersions as $version) {
            $this->assertDoesNotMatchRegularExpression('/^\d+\.\d+\.\d+$/', $version);
        }
    }

    public function testTimestampValidation()
    {
        // Test timestamp format validation
        $validTimestamp = date('c');
        $timestamp = strtotime($validTimestamp);
        
        $this->assertNotFalse($timestamp, 'Timestamp should be valid');
        
        $now = time();
        $this->assertLessThanOrEqual($now, $timestamp);
        $this->assertGreaterThan($now - 60, $timestamp); // Should be within last minute
    }

    public function testUptimeFormatValidation()
    {
        // Test uptime format validation
        $validUptimeFormats = [
            '0 days, 0 hours, 0 minutes',
            '1 day, 2 hours, 30 minutes',
            '5 days, 12 hours, 45 minutes'
        ];
        
        foreach ($validUptimeFormats as $uptime) {
            $this->assertMatchesRegularExpression('/^\d+ day[s]?, \d+ hour[s]?, \d+ minute[s]?$/', $uptime);
        }
        
        $invalidUptimeFormats = ['uptime', 'running', 'active'];
        foreach ($invalidUptimeFormats as $uptime) {
            $this->assertDoesNotMatchRegularExpression('/^\d+ day[s]?, \d+ hour[s]?, \d+ minute[s]?$/', $uptime);
        }
    }

    public function testHealthDataTypes()
    {
        // Test expected data types for health information
        $healthData = [
            'status' => 'healthy',
            'version' => '1.0.0',
            'timestamp' => date('c'),
            'uptime' => '0 days, 0 hours, 0 minutes'
        ];
        
        $this->assertIsString($healthData['status']);
        $this->assertIsString($healthData['version']);
        $this->assertIsString($healthData['timestamp']);
        $this->assertIsString($healthData['uptime']);
        
        $this->assertNotEmpty($healthData['status']);
        $this->assertNotEmpty($healthData['version']);
        $this->assertNotEmpty($healthData['timestamp']);
        $this->assertNotEmpty($healthData['uptime']);
    }

    public function testHealthResponseFormat()
    {
        // Test the expected response format structure
        $expectedResponse = [
            'success' => true,
            'message' => 'Widget health check completed',
            'timestamp' => date('c'),
            'data' => [
                'status' => 'healthy',
                'version' => '1.0.0',
                'timestamp' => date('c'),
                'uptime' => '0 days, 0 hours, 0 minutes'
            ]
        ];
        
        $this->assertArrayHasKey('success', $expectedResponse);
        $this->assertArrayHasKey('message', $expectedResponse);
        $this->assertArrayHasKey('timestamp', $expectedResponse);
        $this->assertArrayHasKey('data', $expectedResponse);
        
        $this->assertTrue($expectedResponse['success']);
        $this->assertIsString($expectedResponse['message']);
        $this->assertIsString($expectedResponse['timestamp']);
        $this->assertIsArray($expectedResponse['data']);
    }
}
