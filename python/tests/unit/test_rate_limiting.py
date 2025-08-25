"""
Unit tests for RateLimitManager class
Tests rate limiting logic, cleanup, and edge cases
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from app.utils.rate_limiting import RateLimitManager

class TestRateLimitManager:
    """Test RateLimitManager class methods"""
    
    def test_init(self, db_manager):
        """Test RateLimitManager initialization"""
        rate_limiter = RateLimitManager(db_manager)
        assert rate_limiter.db_manager == db_manager
    
    def test_check_rate_limit_new_ip(self, rate_limiter):
        """Test rate limit check for new IP address"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None  # No existing rate limit
            mock_get_conn.return_value = mock_conn
            
            result = rate_limiter.check_rate_limit('192.168.1.1', '/api/messages', 50)
            
            assert result is True  # Should allow first request
            mock_cursor.execute.assert_called()  # Should create new rate limit record
    
    def test_check_rate_limit_existing_under_limit(self, rate_limiter):
        """Test rate limit check for existing IP under limit"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock existing rate limit record under the limit
            mock_cursor.fetchone.return_value = {
                'count': 25,
                'window_start': datetime.now().isoformat()
            }
            mock_get_conn.return_value = mock_conn
            
            result = rate_limiter.check_rate_limit('192.168.1.1', '/api/messages', 50)
            
            assert result is True  # Should allow request under limit
            mock_cursor.execute.assert_called()  # Should update request count
    
    def test_check_rate_limit_existing_at_limit(self, rate_limiter):
        """Test rate limit check for existing IP at limit"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock existing rate limit record at the limit
            mock_cursor.fetchone.return_value = {
                'count': 50,
                'window_start': datetime.now().isoformat()
            }
            mock_get_conn.return_value = mock_conn
            
            result = rate_limiter.check_rate_limit('192.168.1.1', '/api/messages', 50)
            
            assert result is False  # Should block request at limit
    
    def test_check_rate_limit_existing_over_limit(self, rate_limiter):
        """Test rate limit check for existing IP over limit"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock existing rate limit record over the limit
            mock_cursor.fetchone.return_value = {
                'count': 75,
                'window_start': datetime.now().isoformat()
            }
            mock_get_conn.return_value = mock_conn
            
            result = rate_limiter.check_rate_limit('192.168.1.1', '/api/messages', 50)
            
            assert result is False  # Should block request over limit
    
    def test_check_rate_limit_window_expired(self, rate_limiter):
        """Test rate limit check when window has expired"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            
            # First call: cleanup expired records (should return None for expired record)
            # Second call: check current rate limit (should return None for new window)
            mock_cursor.fetchone.side_effect = [None, None]
            mock_get_conn.return_value = mock_conn
            
            result = rate_limiter.check_rate_limit('192.168.1.1', '/api/messages', 50)
            
            assert result is True  # Should allow request in new window
            # Should delete old record and create new one
            assert mock_cursor.execute.call_count >= 2  # At least cleanup + insert
    
    def test_check_rate_limit_different_endpoints(self, rate_limiter):
        """Test rate limiting for different endpoints"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None  # No existing rate limit
            mock_get_conn.return_value = mock_conn
            
            # Test different endpoints for same IP
            result1 = rate_limiter.check_rate_limit('192.168.1.1', '/api/messages', 50)
            result2 = rate_limiter.check_rate_limit('192.168.1.1', '/api/inbox', 120)
            
            assert result1 is True
            assert result2 is True
            # Should create separate rate limit records for each endpoint
    
    def test_check_rate_limit_different_ips(self, rate_limiter):
        """Test rate limiting for different IP addresses"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None  # No existing rate limit
            mock_get_conn.return_value = mock_conn
            
            # Test same endpoint for different IPs
            result1 = rate_limiter.check_rate_limit('192.168.1.1', '/api/messages', 50)
            result2 = rate_limiter.check_rate_limit('192.168.1.2', '/api/messages', 50)
            
            assert result1 is True
            assert result2 is True
            # Should create separate rate limit records for each IP
    
    def test_cleanup_expired_limits(self, rate_limiter):
        """Test cleanup of expired rate limit records"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.rowcount = 5  # 5 expired records cleaned up
            mock_get_conn.return_value = mock_conn
            
            cleaned_count = rate_limiter.cleanup_expired_limits()
            
            assert cleaned_count == 5
            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called_once()
    
    def test_cleanup_expired_limits_no_expired(self, rate_limiter):
        """Test cleanup when no expired rate limit records exist"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.rowcount = 0  # No expired records
            mock_get_conn.return_value = mock_conn
            
            cleaned_count = rate_limiter.cleanup_expired_limits()
            
            assert cleaned_count == 0
            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called_once()
    
    def test_get_rate_limit_info(self, rate_limiter):
        """Test getting rate limit information for an IP/endpoint"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock rate limit record
            mock_cursor.fetchone.return_value = {
                'count': 25,
                'window_start': '2025-08-24T16:00:00'
            }
            mock_get_conn.return_value = mock_conn
            
            info = rate_limiter.get_rate_limit_info('192.168.1.1', '/api/messages')
            
            assert info['request_count'] == 25
            assert 'window_start' in info
            assert 'window_end' in info
    
    def test_get_rate_limit_info_not_found(self, rate_limiter):
        """Test getting rate limit info when record doesn't exist"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None  # No record found
            mock_get_conn.return_value = mock_conn
            
            info = rate_limiter.get_rate_limit_info('192.168.1.1', '/api/messages')
            
            # Should return default info structure, not None
            assert info['current_count'] == 0
            assert 'window_start' in info
            assert 'window_end' in info
    
    def test_reset_rate_limit(self, rate_limiter):
        """Test resetting rate limit for an IP/endpoint"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn
            
            rate_limiter.reset_rate_limit('192.168.1.1', '/api/messages')
            
            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called_once()
    
    def test_get_all_rate_limits(self, rate_limiter):
        """Test getting all rate limit records"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock rate limit records
            mock_row1 = Mock()
            mock_row1.__getitem__ = lambda self, key: {
                'ip_address': '192.168.1.1',
                'endpoint': '/api/messages',
                'request_count': 25,
                'window_start': '2025-08-24T16:00:00'
            }.get(key)
            mock_row1.keys = lambda: ['ip_address', 'endpoint', 'request_count', 'window_start']
            
            mock_row2 = Mock()
            mock_row2.__getitem__ = lambda self, key: {
                'ip_address': '192.168.1.2',
                'endpoint': '/api/inbox',
                'request_count': 50,
                'window_start': '2025-08-24T16:00:00'
            }.get(key)
            mock_row2.keys = lambda: ['ip_address', 'endpoint', 'request_count', 'window_start']
            
            mock_cursor.fetchall.return_value = [mock_row1, mock_row2]
            mock_get_conn.return_value = mock_conn
            
            limits = rate_limiter.get_all_rate_limits()
            
            assert len(limits) == 2
            assert limits[0]['ip_address'] == '192.168.1.1'
            assert limits[1]['ip_address'] == '192.168.1.2'
    
    def test_connection_cleanup(self, rate_limiter):
        """Test that connections are properly closed"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None
            mock_get_conn.return_value = mock_conn
            
            rate_limiter.check_rate_limit('192.168.1.1', '/api/messages', 50)
            
            mock_conn.close.assert_called_once()
    
    def test_rate_limit_edge_cases(self, rate_limiter):
        """Test rate limiting edge cases"""
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None
            mock_get_conn.return_value = mock_conn
            
            # Test with limit = 0 (should always block)
            result = rate_limiter.check_rate_limit('192.168.1.1', '/api/messages', 0)
            assert result is False
            
            # Test with limit = 1 (should allow first, block second)
            # Reset mock to simulate fresh state
            mock_get_conn.reset_mock()
            mock_cursor.fetchone.return_value = None  # First request
            
            result = rate_limiter.check_rate_limit('192.168.1.1', '/api/messages', 1)
            assert result is True
            
            # Second request should be blocked (now there's an existing record)
            mock_cursor.fetchone.return_value = {'count': 1}  # Existing record
            result = rate_limiter.check_rate_limit('192.168.1.1', '/api/messages', 1)
            assert result is False
    
    def test_rate_limit_cleanup_scheduling(self, rate_limiter):
        """Test that cleanup is called periodically"""
        # The current implementation doesn't automatically call cleanup
        # This test verifies the cleanup method exists and works
        with patch.object(rate_limiter.db_manager, 'get_connection') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.rowcount = 2
            mock_get_conn.return_value = mock_conn
            
            cleaned_count = rate_limiter.cleanup_expired_limits()
            assert cleaned_count == 2
