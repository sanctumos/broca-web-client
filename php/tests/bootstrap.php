<?php
/**
 * Test Bootstrap File
 * Sets up the testing environment for PHP widget tests
 */

// Set error reporting for testing
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Set testing environment
$_ENV['APP_ENV'] = 'testing';
$_ENV['WEB_CHAT_DEBUG'] = 'true';

// Mock $_SERVER variables for testing
$_SERVER['HTTP_HOST'] = 'localhost';
$_SERVER['SERVER_PORT'] = '80';
$_SERVER['REQUEST_METHOD'] = 'GET';
$_SERVER['REQUEST_URI'] = '/';
$_SERVER['HTTP_USER_AGENT'] = 'PHPUnit Test';
$_SERVER['REMOTE_ADDR'] = '127.0.0.1';

// Include the autoloader if using Composer
if (file_exists(__DIR__ . '/../vendor/autoload.php')) {
    require_once __DIR__ . '/../vendor/autoload.php';
}

// Set up test database path
$_ENV['TEST_DATABASE_PATH'] = __DIR__ . '/../test_web_chat_bridge.db';

// Include test utilities
require_once __DIR__ . '/TestUtils.php';

// Set up test environment
TestUtils::setupTestEnvironment();
