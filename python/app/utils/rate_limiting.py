import sqlite3
from datetime import datetime, timedelta
from typing import Optional

class RateLimitManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def check_rate_limit(self, ip_address: str, endpoint: str, limit: int) -> bool:
        """Check if request is within rate limit - IDENTICAL to PHP"""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            
            # Calculate window start (1 hour ago) - IDENTICAL to PHP
            window_start = datetime.now() - timedelta(hours=1)
            window_start_str = window_start.strftime('%Y-%m-%d %H:%M:%S')
            
            # Clean up old rate limit entries - IDENTICAL to PHP
            cursor.execute("""
                DELETE FROM rate_limits 
                WHERE window_start < ?
            """, (window_start_str,))
            
            # Check current rate limit for this IP + endpoint - IDENTICAL to PHP
            cursor.execute("""
                SELECT count FROM rate_limits 
                WHERE ip_address = ? AND endpoint = ? AND window_start >= ?
            """, (ip_address, endpoint, window_start_str))
            
            result = cursor.fetchone()
            current_count = result['count'] if result else 0
            
            if current_count >= limit:
                return False  # Rate limit exceeded
            
            # Update or insert rate limit entry - IDENTICAL to PHP
            if result:
                cursor.execute("""
                    UPDATE rate_limits 
                    SET count = count + 1
                    WHERE ip_address = ? AND endpoint = ? AND window_start >= ?
                """, (ip_address, endpoint, window_start_str))
            else:
                cursor.execute("""
                    INSERT INTO rate_limits (ip_address, endpoint, count, window_start)
                    VALUES (?, ?, 1, ?)
                """, (ip_address, endpoint, window_start_str))
            
            conn.commit()
            return True  # Within rate limit
            
        finally:
            conn.close()
    
    def get_rate_limit_info(self, ip_address: str, endpoint: str) -> dict:
        """Get rate limit information for debugging"""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get current window info
            window_start = datetime.now() - timedelta(hours=1)
            window_start_str = window_start.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                SELECT count, window_start FROM rate_limits 
                WHERE ip_address = ? AND endpoint = ? AND window_start >= ?
            """, (ip_address, endpoint, window_start_str))
            
            result = cursor.fetchone()
            if result:
                return {
                    'request_count': result['count'],
                    'current_count': result['count'],
                    'window_start': result['window_start'],
                    'window_end': (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                return {
                    'request_count': 0,
                    'current_count': 0,
                    'window_start': window_start_str,
                    'window_end': (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
                }
        finally:
            conn.close()
    
    def cleanup_expired_limits(self) -> int:
        """Clean up expired rate limit entries"""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            window_start = datetime.now() - timedelta(hours=1)
            window_start_str = window_start.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                DELETE FROM rate_limits 
                WHERE window_start < ?
            """, (window_start_str,))
            
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def reset_rate_limit(self, ip_address: str, endpoint: str) -> bool:
        """Reset rate limit for a specific IP and endpoint"""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM rate_limits 
                WHERE ip_address = ? AND endpoint = ?
            """, (ip_address, endpoint))
            
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_all_rate_limits(self) -> list:
        """Get all current rate limit entries"""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ip_address, endpoint, request_count, window_start, created_at, updated_at
                FROM rate_limits
                ORDER BY window_start DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
