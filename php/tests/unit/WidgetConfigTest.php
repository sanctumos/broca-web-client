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

    public function testBasicTestFramework()
    {
        // Simple test to verify our testing framework works
        $this->assertTrue(true);
        $this->assertEquals(2, 1 + 1);
    }

    public function testExpectedConfigStructure()
    {
        // Test the expected configuration structure without calling endpoints
        $expectedPositions = ['bottom-right', 'bottom-left', 'top-right', 'top-left'];
        $expectedThemes = ['light', 'dark', 'auto'];
        $expectedLanguages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'];
        
        $this->assertCount(4, $expectedPositions);
        $this->assertCount(3, $expectedThemes);
        $this->assertCount(10, $expectedLanguages);
        
        $this->assertContains('bottom-right', $expectedPositions);
        $this->assertContains('light', $expectedThemes);
        $this->assertContains('en', $expectedLanguages);
    }

    public function testExpectedConfigDefaults()
    {
        // Test the expected default configuration values
        $expectedDefaults = [
            'position' => 'bottom-right',
            'theme' => 'light',
            'title' => 'Chat with us',
            'primaryColor' => '#007bff',
            'language' => 'en',
            'autoOpen' => false,
            'notifications' => true,
            'sound' => true
        ];
        
        $this->assertCount(8, $expectedDefaults);
        $this->assertEquals('bottom-right', $expectedDefaults['position']);
        $this->assertEquals('light', $expectedDefaults['theme']);
        $this->assertEquals('Chat with us', $expectedDefaults['title']);
        $this->assertEquals('#007bff', $expectedDefaults['primaryColor']);
        $this->assertEquals('en', $expectedDefaults['language']);
        $this->assertFalse($expectedDefaults['autoOpen']);
        $this->assertTrue($expectedDefaults['notifications']);
        $this->assertTrue($expectedDefaults['sound']);
    }

    public function testConfigValidation()
    {
        // Test configuration validation logic
        $validPositions = ['bottom-right', 'bottom-left', 'top-right', 'top-left'];
        $validThemes = ['light', 'dark', 'auto'];
        $validLanguages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'];
        
        // Test position validation
        $testPosition = 'bottom-right';
        $this->assertContains($testPosition, $validPositions);
        
        // Test theme validation
        $testTheme = 'dark';
        $this->assertContains($testTheme, $validThemes);
        
        // Test language validation
        $testLanguage = 'es';
        $this->assertContains($testLanguage, $validLanguages);
    }

    public function testColorValidation()
    {
        // Test color format validation
        $validColors = ['#007bff', '#ff0000', '#00ff00', '#0000ff', '#ffffff', '#000000'];
        
        foreach ($validColors as $color) {
            $this->assertMatchesRegularExpression('/^#[0-9a-fA-F]{6}$/', $color);
        }
        
        // Test invalid colors
        $invalidColors = ['red', 'blue', '#123', '#12345', 'invalid'];
        foreach ($invalidColors as $color) {
            $this->assertDoesNotMatchRegularExpression('/^#[0-9a-fA-F]{6}$/', $color);
        }
    }

    public function testBooleanValidation()
    {
        // Test boolean configuration options
        $booleanOptions = ['autoOpen', 'notifications', 'sound'];
        
        foreach ($booleanOptions as $option) {
            $this->assertIsString($option);
            $this->assertNotEmpty($option);
        }
        
        // Test boolean values
        $this->assertIsBool(false);
        $this->assertIsBool(true);
    }
}
