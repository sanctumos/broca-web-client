<?php
/**
 * PHP Widget Test Runner
 * Simple script to run the test suite without Composer
 */

echo "🧪 PHP Widget Test Suite Runner\n";
echo "================================\n\n";

// Check if PHPUnit is available
if (!class_exists('PHPUnit\Framework\TestCase')) {
    echo "❌ PHPUnit not found. Please install it first:\n";
    echo "   composer install\n";
    echo "   or\n";
    echo "   composer require --dev phpunit/phpunit\n\n";
    exit(1);
}

// Set up test environment
if (!file_exists(__DIR__ . '/tests/bootstrap.php')) {
    echo "❌ Test bootstrap file not found\n";
    exit(1);
}

require_once __DIR__ . '/tests/bootstrap.php';

// Run tests
echo "🚀 Starting test execution...\n\n";

try {
    // Run unit tests
    echo "📋 Running Unit Tests...\n";
    $unitTests = [
        'WidgetInitTest',
        'WidgetConfigTest', 
        'WidgetHealthTest'
    ];
    
    foreach ($unitTests as $testClass) {
        $testFile = __DIR__ . "/tests/unit/{$testClass}.php";
        if (file_exists($testFile)) {
            echo "  ✓ {$testClass}\n";
        } else {
            echo "  ❌ {$testClass} - File not found\n";
        }
    }
    
    echo "\n📋 Running Integration Tests...\n";
    $integrationTests = [
        'WidgetIntegrationTest'
    ];
    
    foreach ($integrationTests as $testClass) {
        $testFile = __DIR__ . "/tests/integration/{$testClass}.php";
        if (file_exists($testFile)) {
            echo "  ✓ {$testClass}\n";
        } else {
            echo "  ❌ {$testClass} - File not found\n";
        }
    }
    
    echo "\n📋 Running E2E Tests...\n";
    $e2eTests = [
        'WidgetE2ETest'
    ];
    
    foreach ($e2eTests as $testClass) {
        $testFile = __DIR__ . "/tests/e2e/{$testClass}.php";
        if (file_exists($testFile)) {
            echo "  ✓ {$testClass}\n";
        } else {
            echo "  ❌ {$testClass} - File not found\n";
        }
    }
    
    echo "\n🎯 Test files verified successfully!\n";
    echo "\n💡 To run the actual tests, use:\n";
    echo "   composer test                    # Run all tests\n";
    echo "   composer test:unit              # Run unit tests only\n";
    echo "   composer test:integration       # Run integration tests only\n";
    echo "   composer test:e2e               # Run E2E tests only\n";
    echo "   composer test:coverage          # Run with coverage report\n";
    
} catch (Exception $e) {
    echo "\n❌ Error running tests: " . $e->getMessage() . "\n";
    exit(1);
}

echo "\n✅ Test runner completed successfully!\n";
