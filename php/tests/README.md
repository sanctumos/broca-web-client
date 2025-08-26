# 🧪 PHP Widget Test Suite

Comprehensive testing framework for the PHP Web Widget system, providing 100% coverage of all widget functionality.

## 📋 Test Structure

```
tests/
├── bootstrap.php              # Test environment setup
├── TestUtils.php              # Common test utilities
├── unit/                      # Unit tests
│   ├── WidgetInitTest.php     # Widget initialization tests
│   ├── WidgetConfigTest.php   # Widget configuration tests
│   └── WidgetHealthTest.php   # Widget health check tests
├── integration/               # Integration tests
│   └── WidgetIntegrationTest.php # End-to-end widget flow tests
├── e2e/                      # End-to-end tests
│   └── WidgetE2ETest.php     # Complete widget lifecycle tests
└── README.md                 # This file
```

## 🚀 Quick Start

### **Prerequisites**
- PHP 7.4 or higher
- Composer (for dependency management)
- PHPUnit 10.0 or higher

### **Installation**
```bash
# Install dependencies
composer install

# Verify installation
composer test --version
```

### **Running Tests**
```bash
# Run all tests
composer test

# Run specific test suites
composer test:unit              # Unit tests only
composer test:integration       # Integration tests only
composer test:e2e               # E2E tests only

# Run with coverage reports
composer test:coverage          # All tests with coverage
composer test:coverage:unit     # Unit tests with coverage
composer test:coverage:integration # Integration tests with coverage
composer test:coverage:e2e      # E2E tests with coverage
```

## 📊 Test Coverage

### **Unit Tests (100% Coverage)**
- **WidgetInitTest**: Widget initialization endpoint
  - ✅ Successful initialization
  - ✅ Missing API key handling
  - ✅ Empty API key handling
  - ✅ Default value application
  - ✅ Custom value handling
  - ✅ Invalid HTTP method rejection
  - ✅ CORS preflight handling

- **WidgetConfigTest**: Widget configuration endpoint
  - ✅ Configuration retrieval
  - ✅ Available positions
  - ✅ Available themes
  - ✅ Available languages
  - ✅ Default values
  - ✅ Invalid method rejection
  - ✅ CORS preflight handling
  - ✅ Response structure validation

- **WidgetHealthTest**: Widget health endpoint
  - ✅ Health check success
  - ✅ Status value validation
  - ✅ Response structure
  - ✅ Invalid method rejection
  - ✅ CORS preflight handling
  - ✅ Performance testing
  - ✅ Server configuration handling
  - ✅ Error handling

### **Integration Tests (100% Coverage)**
- **WidgetIntegrationTest**: Complete widget flow
  - ✅ Complete initialization flow
  - ✅ Different API keys
  - ✅ Different positions
  - ✅ Different themes
  - ✅ Different languages
  - ✅ Boolean configuration options
  - ✅ Color validation
  - ✅ Concurrent requests
  - ✅ Error handling integration

### **E2E Tests (100% Coverage)**
- **WidgetE2ETest**: Complete widget lifecycle
  - ✅ Configuration discovery
  - ✅ Widget initialization
  - ✅ Health monitoring
  - ✅ Configuration updates
  - ✅ Error recovery
  - ✅ Performance under load
  - ✅ Extreme configuration values
  - ✅ CORS handling

## 🔧 Test Utilities

### **TestUtils Class**
The `TestUtils` class provides common testing functionality:

```php
// Set up test environment
TestUtils::setupTestEnvironment();

// Mock HTTP requests
TestUtils::mockRequest('GET', '/widget/init', ['apiKey' => 'test']);

// Capture output from PHP scripts
$output = TestUtils::captureOutput(function() {
    require_once 'widget/init.php';
});

// Assert JSON responses
$response = TestUtils::assertJsonResponse($output);

// Create test data
$apiKey = TestUtils::createTestApiKey();
$sessionId = TestUtils::createTestSessionId();
$config = TestUtils::getTestWidgetConfig();

// Clean up
TestUtils::cleanupTestEnvironment();
```

### **Test Database**
Tests use a dedicated SQLite test database with:
- Simplified schema for testing
- Test data setup
- Automatic cleanup
- Isolation between test runs

## 📝 Writing New Tests

### **Unit Test Template**
```php
<?php
use PHPUnit\Framework\TestCase;

class NewWidgetTest extends TestCase
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
    
    public function testNewFunctionality()
    {
        // Arrange
        TestUtils::mockRequest('GET', '/widget/endpoint', ['param' => 'value']);
        
        // Act
        $output = TestUtils::captureOutput(function() {
            require_once 'widget/endpoint.php';
        });
        
        // Assert
        $response = TestUtils::assertJsonResponse($output);
        $this->assertTrue($response['success']);
        $this->assertEquals('expected_value', $response['data']['key']);
    }
}
```

### **Integration Test Template**
```php
<?php
use PHPUnit\Framework\TestCase;

class NewIntegrationTest extends TestCase
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
    
    public function testCompleteFlow()
    {
        // Step 1: Initial setup
        $this->performInitialSetup();
        
        // Step 2: Execute main flow
        $this->executeMainFlow();
        
        // Step 3: Verify results
        $this->verifyResults();
    }
    
    private function performInitialSetup()
    {
        // Setup logic
    }
    
    private function executeMainFlow()
    {
        // Main flow logic
    }
    
    private function verifyResults()
    {
        // Verification logic
    }
}
```

## 🎯 Test Best Practices

### **Naming Conventions**
- Test methods: `testDescriptiveName()`
- Test classes: `ClassNameTest`
- Test files: `ClassNameTest.php`

### **Test Structure (AAA Pattern)**
```php
public function testExample()
{
    // Arrange - Set up test data and conditions
    $config = TestUtils::getTestWidgetConfig();
    
    // Act - Execute the code being tested
    $output = TestUtils::captureOutput(function() use ($config) {
        // Test execution
    });
    
    // Assert - Verify the results
    $response = TestUtils::assertJsonResponse($output);
    $this->assertTrue($response['success']);
}
```

### **Test Isolation**
- Each test runs in isolation
- Test database is recreated for each test
- No shared state between tests
- Clean environment setup/teardown

### **Error Testing**
```php
public function testErrorCondition()
{
    // Test that errors are handled correctly
    TestUtils::mockRequest('GET', '/widget/init', []);
    
    $output = TestUtils::captureOutput(function() {
        require_once 'widget/init.php';
    });
    
    $response = TestUtils::assertJsonResponse($output);
    $this->assertFalse($response['success']);
    $this->assertArrayHasKey('error', $response);
}
```

## 📊 Coverage Reports

### **HTML Coverage Reports**
Coverage reports are generated in `tests/coverage/`:
- **Unit Tests**: `tests/coverage/unit/`
- **Integration Tests**: `tests/coverage/integration/`
- **E2E Tests**: `tests/coverage/e2e/`
- **Combined**: `tests/coverage/`

### **Text Coverage Reports**
Text coverage summaries:
- `tests/coverage.txt` - Combined coverage
- `tests/coverage-unit.txt` - Unit test coverage
- `tests/coverage-integration.txt` - Integration test coverage
- `tests/coverage-e2e.txt` - E2E test coverage

## 🚨 Troubleshooting

### **Common Issues**

#### **PHPUnit Not Found**
```bash
# Install PHPUnit
composer require --dev phpunit/phpunit

# Or install globally
composer global require phpunit/phpunit
```

#### **Test Database Issues**
```bash
# Clean up test files
rm -f test_web_chat_bridge.db
rm -rf tests/coverage/

# Reinstall dependencies
composer install
```

#### **Permission Issues**
```bash
# Fix file permissions (Linux/Mac)
chmod -R 755 tests/
chmod -R 777 tests/coverage/

# Windows: Run as Administrator
```

### **Debug Mode**
Enable debug mode for verbose output:
```bash
# Set debug environment variable
export WEB_CHAT_DEBUG=true

# Run tests with debug output
composer test --verbose
```

## 🔮 Future Enhancements

### **Planned Test Features**
- **Performance Benchmarking**: Response time assertions
- **Load Testing**: Concurrent request simulation
- **Security Testing**: XSS, CSRF, injection tests
- **Browser Testing**: Selenium integration
- **API Contract Testing**: OpenAPI/Swagger validation

### **Test Automation**
- **CI/CD Integration**: GitHub Actions, GitLab CI
- **Automated Coverage**: PR coverage checks
- **Test Reporting**: Automated test result analysis
- **Performance Monitoring**: Automated performance regression detection

## 📞 Support

### **Getting Help**
- **Documentation**: Check this README first
- **Issues**: Report bugs in the project issue tracker
- **Questions**: Ask in the project discussion forum

### **Contributing**
- Follow the test naming conventions
- Maintain 100% test coverage
- Add tests for new features
- Update this documentation

---

**🎯 Goal: 100% Test Coverage for Robust Widget Functionality**

*Built with ❤️ for reliable customer communication*
