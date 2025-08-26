<?php
/**
 * Unit Tests for Widget Health Endpoint
 */

use PHPUnit\Framework\TestCase;

class WidgetHealthTest extends TestCase
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
     * Test successful health check
     */
    public function testSuccessfulHealthCheck()
    {
        TestUtils::mockRequest('GET', '/widget/health');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/health.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $this->assertTrue($response['success']);
        $this->assertEquals('Widget health check completed', $response['message']);
        $this->assertArrayHasKey('status', $response['data']);
        $this->assertArrayHasKey('version', $response['data']);
        $this->assertArrayHasKey('api_status', $response['data']);
        $this->assertArrayHasKey('timestamp', $response['data']);
    }
    
    /**
     * Test health status values
     */
    public function testHealthStatusValues()
    {
        TestUtils::mockRequest('GET', '/widget/health');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/health.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $data = $response['data'];
        
        // Verify status is healthy
        $this->assertEquals('healthy', $data['status']);
        
        // Verify version format
        $this->assertMatchesRegularExpression('/^\d+\.\d+\.\d+$/', $data['version']);
        
        // Verify API status is one of expected values
        $expectedApiStatuses = ['connected', 'disconnected', 'error'];
        $this->assertContains($data['api_status'], $expectedApiStatuses);
        
        // Verify timestamp is valid ISO format
        $this->assertMatchesRegularExpression('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$/', $data['timestamp']);
    }
    
    /**
     * Test health response structure
     */
    public function testHealthResponseStructure()
    {
        TestUtils::mockRequest('GET', '/widget/health');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/health.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        // Verify top-level structure
        $this->assertArrayHasKey('success', $response);
        $this->assertArrayHasKey('message', $response);
        $this->assertArrayHasKey('timestamp', $response);
        $this->assertArrayHasKey('data', $response);
        
        // Verify data structure
        $data = $response['data'];
        $this->assertArrayHasKey('status', $data);
        $this->assertArrayHasKey('version', $data);
        $this->assertArrayHasKey('api_status', $data);
        $this->assertArrayHasKey('timestamp', $data);
        
        // Verify data types
        $this->assertIsString($data['status']);
        $this->assertIsString($data['version']);
        $this->assertIsString($data['api_status']);
        $this->assertIsString($data['timestamp']);
    }
    
    /**
     * Test health with invalid HTTP method
     */
    public function testHealthInvalidMethod()
    {
        TestUtils::mockRequest('POST', '/widget/health');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/health.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        $this->assertFalse($response['success']);
        $this->assertEquals('Method not allowed', $response['error']);
    }
    
    /**
     * Test health with OPTIONS request (CORS preflight)
     */
    public function testHealthOptionsRequest()
    {
        TestUtils::mockRequest('OPTIONS', '/widget/health');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/health.php';
        });
        
        // OPTIONS request should exit early
        $this->assertEmpty($output);
    }
    
    /**
     * Test health check performance
     */
    public function testHealthCheckPerformance()
    {
        $startTime = microtime(true);
        
        TestUtils::mockRequest('GET', '/widget/health');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/health.php';
        });
        
        $endTime = microtime(true);
        $executionTime = $endTime - $startTime;
        
        // Health check should complete within 1 second
        $this->assertLessThan(1.0, $executionTime, 'Health check took too long: ' . $executionTime . ' seconds');
        
        $response = TestUtils::assertJsonResponse($output);
        $this->assertTrue($response['success']);
    }
    
    /**
     * Test health check with different server configurations
     */
    public function testHealthCheckWithDifferentServers()
    {
        // Test with HTTPS
        $_SERVER['HTTPS'] = 'on';
        $_SERVER['SERVER_PORT'] = '443';
        
        TestUtils::mockRequest('GET', '/widget/health');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/health.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        $this->assertTrue($response['success']);
        
        // Test with custom port
        $_SERVER['HTTPS'] = 'off';
        $_SERVER['SERVER_PORT'] = '8080';
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/health.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        $this->assertTrue($response['success']);
    }
    
    /**
     * Test health check error handling
     */
    public function testHealthCheckErrorHandling()
    {
        // Mock a scenario where API check might fail
        $_SERVER['HTTP_HOST'] = 'invalid-host';
        
        TestUtils::mockRequest('GET', '/widget/health');
        
        $output = TestUtils::captureOutput(function() {
            require_once __DIR__ . '/../../public/widget/health.php';
        });
        
        $response = TestUtils::assertJsonResponse($output);
        
        // Should still return success but with potentially different API status
        $this->assertTrue($response['success']);
        $this->assertArrayHasKey('api_status', $response['data']);
        
        // API status might be 'error' or 'disconnected' in this case
        $this->assertContains($response['data']['api_status'], ['connected', 'disconnected', 'error']);
    }
}
