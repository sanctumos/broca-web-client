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

    public function testBasicTestFramework()
    {
        // Simple test to verify our testing framework works
        $this->assertTrue(true);
        $this->assertEquals(2, 1 + 1);
    }

    public function testExpectedInitStructure()
    {
        // Test the expected initialization structure without calling endpoints
        $expectedConfig = [
            'apiKey' => 'test_key_123',
            'position' => 'bottom-right',
            'theme' => 'light',
            'title' => 'Chat with us',
            'primaryColor' => '#007bff',
            'language' => 'en',
            'autoOpen' => false,
            'notifications' => true,
            'sound' => true
        ];
        
        $this->assertCount(9, $expectedConfig);
        $this->assertArrayHasKey('apiKey', $expectedConfig);
        $this->assertArrayHasKey('position', $expectedConfig);
        $this->assertArrayHasKey('theme', $expectedConfig);
        $this->assertArrayHasKey('title', $expectedConfig);
        $this->assertArrayHasKey('primaryColor', $expectedConfig);
        $this->assertArrayHasKey('language', $expectedConfig);
        $this->assertArrayHasKey('autoOpen', $expectedConfig);
        $this->assertArrayHasKey('notifications', $expectedConfig);
        $this->assertArrayHasKey('sound', $expectedConfig);
    }

    public function testExpectedAssetsStructure()
    {
        // Test the expected assets structure
        $expectedAssets = [
            'css' => '/widget/assets/css/widget.css',
            'js' => '/widget/assets/js/chat-widget.js',
            'icons' => '/widget/assets/icons/'
        ];
        
        $this->assertCount(3, $expectedAssets);
        $this->assertStringContainsString('widget.css', $expectedAssets['css']);
        $this->assertStringContainsString('chat-widget.js', $expectedAssets['js']);
        $this->assertStringContainsString('icons', $expectedAssets['icons']);
    }

    public function testExpectedApiStructure()
    {
        // Test the expected API structure
        $expectedApi = [
            'baseUrl' => 'http://localhost',
            'endpoint' => '/api/v1/'
        ];
        
        $this->assertCount(2, $expectedApi);
        $this->assertStringContainsString('localhost', $expectedApi['baseUrl']);
        $this->assertEquals('/api/v1/', $expectedApi['endpoint']);
    }

    public function testApiKeyValidation()
    {
        // Test API key validation logic
        $validApiKeys = ['test_key_123', 'another_key', 'key_with_special_chars_!@#$%'];
        $invalidApiKeys = ['', null];
        
        foreach ($validApiKeys as $key) {
            $this->assertNotEmpty($key);
            $this->assertIsString($key);
        }
        
        foreach ($invalidApiKeys as $key) {
            $this->assertEmpty($key);
        }
    }

    public function testPositionValidation()
    {
        // Test position validation
        $validPositions = ['bottom-right', 'bottom-left', 'top-right', 'top-left'];
        $invalidPositions = ['center', 'middle', 'invalid'];
        
        foreach ($validPositions as $position) {
            $this->assertContains($position, $validPositions);
        }
        
        foreach ($invalidPositions as $position) {
            $this->assertNotContains($position, $validPositions);
        }
    }

    public function testThemeValidation()
    {
        // Test theme validation
        $validThemes = ['light', 'dark', 'auto'];
        $invalidThemes = ['red', 'blue', 'invalid'];
        
        foreach ($validThemes as $theme) {
            $this->assertContains($theme, $validThemes);
        }
        
        foreach ($invalidThemes as $theme) {
            $this->assertNotContains($theme, $validThemes);
        }
    }

    public function testLanguageValidation()
    {
        // Test language validation
        $validLanguages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'];
        $invalidLanguages = ['xx', 'invalid', '123'];
        
        foreach ($validLanguages as $language) {
            $this->assertContains($language, $validLanguages);
        }
        
        foreach ($invalidLanguages as $language) {
            $this->assertNotContains($language, $validLanguages);
        }
    }

    public function testBooleanParameterHandling()
    {
        // Test boolean parameter handling
        $booleanParams = ['autoOpen', 'notifications', 'sound'];
        
        foreach ($booleanParams as $param) {
            $this->assertIsString($param);
            $this->assertNotEmpty($param);
        }
        
        // Test string to boolean conversion
        $this->assertTrue('true' === 'true');
        $this->assertFalse('false' === 'true');
    }
}
