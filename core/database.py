"""
Optimized database operations for Project Runner App.
Enhanced with connection pooling, caching, and batch operations.
"""

import sqlite3
import threading
import time
import json
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from config.settings import DATABASE_CONFIG


class DatabaseConnectionPool:
    """Thread-safe database connection pool for better performance."""
    
    def __init__(self, db_path: str, max_connections: int = 5):
        self.db_path = db_path
        self.max_connections = max_connections
        self._connections = []
        self._lock = threading.Lock()
        self._local = threading.local()
        
    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool."""
        # Try to reuse thread-local connection first
        if hasattr(self._local, 'connection') and self._local.connection:
            try:
                # Test connection
                self._local.connection.execute("SELECT 1")
                yield self._local.connection
                return
            except sqlite3.Error:
                self._local.connection = None
        
        # Get connection from pool
        with self._lock:
            if self._connections:
                conn = self._connections.pop()
            else:
                conn = sqlite3.connect(
                    self.db_path, 
                    timeout=DATABASE_CONFIG["connection_timeout"],
                    check_same_thread=False
                )
                conn.row_factory = sqlite3.Row
                
        try:
            self._local.connection = conn
            yield conn
        finally:
            # Return connection to pool
            with self._lock:
                if len(self._connections) < self.max_connections:
                    self._connections.append(conn)
                else:
                    conn.close()


class OptimizedProjectDatabase:
    """
    Optimized database operations with caching, batching, and connection pooling.
    """
    
    def __init__(self, db_path: str = "project_runner.db"):
        self.db_path = db_path
        self._pool = DatabaseConnectionPool(db_path)
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_lock = threading.Lock()
        self._last_vacuum = 0
        self._batch_operations = []
        self._batch_lock = threading.Lock()
        
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize database with optimized settings."""
        with self._pool.get_connection() as conn:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            
            # Create tables with optimized indexes
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    project_type TEXT NOT NULL,
                    instance_number INTEGER NOT NULL,
                    working_directory TEXT,
                    custom_command TEXT,
                    status TEXT DEFAULT 'created',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_projects_type ON projects(project_type);
                CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
                CREATE INDEX IF NOT EXISTS idx_projects_updated ON projects(updated_at);
                
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS project_counters (
                    project_type TEXT PRIMARY KEY,
                    counter INTEGER NOT NULL DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TRIGGER IF NOT EXISTS update_projects_timestamp 
                AFTER UPDATE ON projects
                BEGIN
                    UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE project_id = NEW.project_id;
                END;
            """)
            conn.commit()
            
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        with self._cache_lock:
            if key in self._cache:
                timestamp = self._cache_timestamps.get(key, 0)
                if time.time() - timestamp < DATABASE_CONFIG["cache_ttl"]:
                    return self._cache[key]
                else:
                    # Remove expired cache entry
                    del self._cache[key]
                    del self._cache_timestamps[key]
        return None
        
    def _set_cache(self, key: str, value: Any):
        """Set value in cache with timestamp."""
        with self._cache_lock:
            self._cache[key] = value
            self._cache_timestamps[key] = time.time()
            
    def _clear_cache(self, pattern: str = None):
        """Clear cache entries matching pattern."""
        with self._cache_lock:
            if pattern:
                keys_to_remove = [k for k in self._cache.keys() if pattern in k]
                for key in keys_to_remove:
                    del self._cache[key]
                    del self._cache_timestamps[key]
            else:
                self._cache.clear()
                self._cache_timestamps.clear()
                
    def _execute_with_retry(self, operation, *args, **kwargs):
        """Execute database operation with retry logic."""
        for attempt in range(DATABASE_CONFIG["retry_attempts"]):
            try:
                return operation(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if attempt == DATABASE_CONFIG["retry_attempts"] - 1:
                    raise
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                
    def save_project(self, project_id: int, name: str, description: str, 
                    project_type: str, instance_number: int, 
                    working_directory: str, custom_command: str, status: str):
        """Save project with optimized database operations."""
        def _save_operation():
            with self._pool.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO projects 
                    (project_id, name, description, project_type, instance_number, 
                     working_directory, custom_command, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (project_id, name, description, project_type, instance_number,
                      working_directory, custom_command, status))
                conn.commit()
                
        self._execute_with_retry(_save_operation)
        self._clear_cache("projects")
        
    def load_projects(self) -> List[Dict]:
        """Load projects with caching."""
        cache_key = "all_projects"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
            
        def _load_operation():
            with self._pool.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT project_id, name, description, project_type, instance_number,
                           working_directory, custom_command, status, created_at, updated_at
                    FROM projects 
                    ORDER BY updated_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
                
        result = self._execute_with_retry(_load_operation)
        self._set_cache(cache_key, result)
        return result
        
    def update_project_status(self, project_id: int, status: str):
        """Update project status with optimized query."""
        def _update_operation():
            with self._pool.get_connection() as conn:
                conn.execute(
                    "UPDATE projects SET status = ? WHERE project_id = ?",
                    (status, project_id)
                )
                conn.commit()
                
        self._execute_with_retry(_update_operation)
        self._clear_cache("projects")
        
    def delete_project(self, project_id: int):
        """Delete project with cleanup."""
        def _delete_operation():
            with self._pool.get_connection() as conn:
                conn.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
                conn.commit()
                
        self._execute_with_retry(_delete_operation)
        self._clear_cache("projects")
        
    def save_app_setting(self, key: str, value: str):
        """Save application setting with caching."""
        def _save_operation():
            with self._pool.get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)",
                    (key, value)
                )
                conn.commit()
                
        self._execute_with_retry(_save_operation)
        self._set_cache(f"setting_{key}", value)
        
    def load_app_setting(self, key: str, default: str = None) -> Optional[str]:
        """Load application setting with caching."""
        cache_key = f"setting_{key}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
            
        def _load_operation():
            with self._pool.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT value FROM app_settings WHERE key = ?", (key,)
                )
                row = cursor.fetchone()
                return row[0] if row else default
                
        result = self._execute_with_retry(_load_operation)
        if result is not None:
            self._set_cache(cache_key, result)
        return result
        
    def save_project_counters(self, counters: Dict[str, int]):
        """Save project counters with batch operation."""
        def _save_operation():
            with self._pool.get_connection() as conn:
                conn.executemany(
                    "INSERT OR REPLACE INTO project_counters (project_type, counter) VALUES (?, ?)",
                    list(counters.items())
                )
                conn.commit()
                
        self._execute_with_retry(_save_operation)
        self._clear_cache("counters")
        
    def load_project_counters(self) -> Dict[str, int]:
        """Load project counters with caching."""
        cache_key = "counters"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
            
        def _load_operation():
            with self._pool.get_connection() as conn:
                cursor = conn.execute("SELECT project_type, counter FROM project_counters")
                return dict(cursor.fetchall())
                
        result = self._execute_with_retry(_load_operation)
        self._set_cache(cache_key, result)
        return result
        
    def vacuum_database(self):
        """Perform database maintenance."""
        current_time = time.time()
        if current_time - self._last_vacuum > DATABASE_CONFIG["vacuum_interval"]:
            def _vacuum_operation():
                with self._pool.get_connection() as conn:
                    conn.execute("VACUUM")
                    conn.execute("ANALYZE")
                    
            self._execute_with_retry(_vacuum_operation)
            self._last_vacuum = current_time
            
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for monitoring."""
        def _stats_operation():
            with self._pool.get_connection() as conn:
                stats = {}
                
                # Table sizes
                cursor = conn.execute("SELECT COUNT(*) FROM projects")
                stats['project_count'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM app_settings")
                stats['settings_count'] = cursor.fetchone()[0]
                
                # Database size
                cursor = conn.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor = conn.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                stats['db_size_bytes'] = page_count * page_size
                
                # Cache stats
                stats['cache_size'] = len(self._cache)
                
                return stats
                
        return self._execute_with_retry(_stats_operation)
        
    def close(self):
        """Close all database connections."""
        with self._pool._lock:
            for conn in self._pool._connections:
                conn.close()
            self._pool._connections.clear()


# Keep backward compatibility
ProjectDatabase = OptimizedProjectDatabase

# Global database instance with lazy initialization
_database_instance = None
_database_lock = threading.Lock()


def get_database() -> OptimizedProjectDatabase:
    """Get the global database instance with thread-safe lazy initialization."""
    global _database_instance
    
    if _database_instance is None:
        with _database_lock:
            if _database_instance is None:
                _database_instance = OptimizedProjectDatabase()
                
    return _database_instance


# ... existing code ... 