# Web Chat Bridge Flask API - Testing Framework

## 🎯 **100% Coverage Testing Suite**

This testing framework provides comprehensive coverage across **Unit**, **Integration**, and **End-to-End** tests, ensuring the Flask port is 100% identical to the PHP version.

## 📁 **Test Structure**

```
tests/
├── conftest.py              # Test configuration and fixtures
├── unit/                    # Unit tests with mocked dependencies
│   ├── test_database.py     # DatabaseManager tests
│   ├── test_rate_limiting.py # RateLimitManager tests
│   └── test_api_routes.py   # API route handler tests
├── integration/             # Integration tests with real database
│   └── test_api_integration.py # Complete API workflow tests
├── e2e/                    # End-to-end user workflow tests
│   └── test_e2e_workflows.py # Complete user journey tests
└── README.md               # This file
```

## 🧪 **Test Types**

### **Unit Tests** (`tests/unit/`)
- **Purpose**: Test individual functions and classes in isolation
- **Coverage**: All methods, edge cases, error conditions
- **Dependencies**: Mocked (no real database/network calls)
- **Speed**: Fast execution
- **Examples**:
  - Database connection handling
  - Input validation functions
  - Authentication logic
  - Rate limiting algorithms

### **Integration Tests** (`tests/integration/`)
- **Purpose**: Test complete API workflows with real database
- **Coverage**: End-to-end API functionality
- **Dependencies**: Test database, real Flask app
- **Speed**: Medium execution
- **Examples**:
  - Complete message submission workflow
  - Admin configuration management
  - Rate limiting in real API calls
  - Error handling and recovery

### **End-to-End Tests** (`tests/e2e/`)
- **Purpose**: Test complete user workflows from start to finish
- **Coverage**: Full user journeys, admin operations
- **Dependencies**: Complete test environment
- **Speed**: Slower execution
- **Examples**:
  - Complete chat workflow (user → admin → user)
  - Multiple concurrent users
  - Performance under load
  - Data persistence across restarts

## 🚀 **Running Tests**

### **Quick Start**
```bash
cd python
python run_tests.py
```

### **Individual Test Types**
```bash
# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only
python -m pytest tests/integration/ -v

# E2E tests only
python -m pytest tests/e2e/ -v

# All tests with coverage
python -m pytest tests/ -v --cov=app --cov-report=html
```

### **Coverage Reports**
```bash
# Generate HTML coverage report
python -m pytest tests/ --cov=app --cov-report=html:htmlcov

# Generate XML coverage report (for CI/CD)
python -m pytest tests/ --cov=app --cov-report=xml

# View coverage in terminal
python -m coverage report
```

## 📊 **Coverage Requirements**

### **100% Coverage Targets**
- **Unit Tests**: All functions, methods, edge cases
- **Integration Tests**: All API endpoints, database operations
- **E2E Tests**: All user workflows, admin operations

### **Coverage Reports Generated**
- `htmlcov/unit/` - Unit test coverage
- `htmlcov/integration/` - Integration test coverage  
- `htmlcov/e2e/` - E2E test coverage
- `htmlcov/overall/` - Combined coverage
- `coverage.xml` - XML format for CI/CD

## 🔧 **Test Configuration**

### **pytest.ini**
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=100
```

### **Test Markers**
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.database` - Database tests

## 🗄️ **Test Database**

### **Features**
- **Isolated**: Each test gets fresh database
- **Realistic**: Matches production schema exactly
- **Fast**: In-memory SQLite for speed
- **Clean**: Automatic cleanup after each test

### **Sample Data**
- Test API keys and admin keys
- Sample sessions and messages
- Configuration values
- Rate limit records

## 🧩 **Test Fixtures**

### **Available Fixtures**
- `test_db` - Fresh test database
- `db_manager` - DatabaseManager instance
- `rate_limiter` - RateLimitManager instance
- `client` - Flask test client
- `auth_headers` - Authentication headers
- `sample_messages` - Sample message data
- `sample_responses` - Sample response data

### **Usage Example**
```python
def test_example(db_manager, client, auth_headers):
    """Example test using fixtures"""
    # Use test database
    # Use Flask test client
    # Use authentication headers
    pass
```

## 📋 **Test Categories**

### **API Endpoint Tests**
- ✅ Message submission (`POST /api/v1/?action=messages`)
- ✅ Inbox retrieval (`GET /api/v1/?action=inbox`)
- ✅ Outbox submission (`POST /api/v1/?action=outbox`)
- ✅ Response retrieval (`GET /api/v1/?action=responses`)
- ✅ Session monitoring (`GET /api/v1/?action=sessions`)
- ✅ Configuration management (`GET/POST /api/v1/?action=config`)
- ✅ Cleanup operations (`POST /api/v1/?action=cleanup`)

### **Authentication Tests**
- ✅ API key validation
- ✅ Admin key validation
- ✅ Unauthorized access handling
- ✅ Invalid token handling

### **Validation Tests**
- ✅ Session ID format validation
- ✅ Message content validation
- ✅ Required field validation
- ✅ Input sanitization

### **Rate Limiting Tests**
- ✅ Request counting
- ✅ Window-based limiting
- ✅ Different endpoint limits
- ✅ Cleanup of expired records

### **Database Tests**
- ✅ Connection management
- ✅ Transaction handling
- ✅ Data persistence
- ✅ Error recovery

### **Error Handling Tests**
- ✅ Invalid inputs
- ✅ Missing fields
- ✅ Database errors
- ✅ Network errors
- ✅ Recovery scenarios

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Import Errors**
```bash
# Ensure you're in the python/ directory
cd python

# Install dependencies
pip install -r requirements.txt

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

#### **Database Errors**
```bash
# Clean up test databases
rm -f test_*.db

# Re-run tests
python -m pytest tests/ -v
```

#### **Coverage Issues**
```bash
# Clear coverage data
coverage erase

# Re-run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### **Debug Mode**
```bash
# Run with debug output
python -m pytest tests/ -v -s --tb=long

# Run specific test
python -m pytest tests/unit/test_database.py::TestDatabaseManager::test_session_exists_true -v -s
```

## 📈 **Performance Benchmarks**

### **Test Execution Times**
- **Unit Tests**: < 5 seconds
- **Integration Tests**: < 15 seconds  
- **E2E Tests**: < 30 seconds
- **Full Suite**: < 1 minute

### **Coverage Targets**
- **Unit Tests**: 100%
- **Integration Tests**: 100%
- **E2E Tests**: 100%
- **Overall Coverage**: 100%

## 🔄 **Continuous Integration**

### **GitHub Actions**
```yaml
- name: Run Tests
  run: |
    cd python
    python run_tests.py
```

### **Coverage Badge**
- **Status**: ![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
- **Target**: Maintain 100% coverage
- **Reports**: Generated on every test run

## 📚 **Additional Resources**

### **Documentation**
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.3.x/testing/)

### **Best Practices**
- Write descriptive test names
- Use meaningful assertions
- Test edge cases and error conditions
- Keep tests independent and isolated
- Use appropriate test markers

## 🎉 **Success Criteria**

### **Test Suite Passes When**
- ✅ All unit tests pass (100% coverage)
- ✅ All integration tests pass (100% coverage)
- ✅ All E2E tests pass (100% coverage)
- ✅ Coverage reports generate successfully
- ✅ No test warnings or errors
- ✅ Performance benchmarks met

### **Ready for Production When**
- ✅ 100% test coverage achieved
- ✅ All test types passing
- ✅ Performance requirements met
- ✅ Error handling verified
- ✅ Security tests passing
- ✅ Documentation complete

---

**🚀 Ready to achieve 100% coverage across all test types!**
