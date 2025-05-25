"""
Database module for persisting project state using SQLite.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class ProjectDatabase:
    """SQLite database manager for project persistence."""
    
    def __init__(self, db_path: str = "project_runner.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    project_type TEXT NOT NULL,
                    instance_number INTEGER NOT NULL,
                    working_directory TEXT,
                    custom_command TEXT,
                    status TEXT DEFAULT 'created',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Application settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Project counters table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_counters (
                    project_type TEXT PRIMARY KEY,
                    counter INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def save_project(self, project_id: int, name: str, description: str, 
                    project_type: str, instance_number: int, 
                    working_directory: str = None, custom_command: str = None,
                    status: str = 'created') -> bool:
        """Save or update a project in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if project exists
                cursor.execute("SELECT id FROM projects WHERE project_id = ?", (project_id,))
                exists = cursor.fetchone()
                
                if exists:
                    # Update existing project
                    cursor.execute("""
                        UPDATE projects 
                        SET name = ?, description = ?, project_type = ?, 
                            instance_number = ?, working_directory = ?, 
                            custom_command = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE project_id = ?
                    """, (name, description, project_type, instance_number, 
                         working_directory, custom_command, status, project_id))
                else:
                    # Insert new project
                    cursor.execute("""
                        INSERT INTO projects 
                        (project_id, name, description, project_type, instance_number, 
                         working_directory, custom_command, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (project_id, name, description, project_type, instance_number,
                         working_directory, custom_command, status))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            print(f"Database error saving project: {e}")
            return False
    
    def load_projects(self) -> List[Dict]:
        """Load all projects from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT project_id, name, description, project_type, instance_number,
                           working_directory, custom_command, status, created_at, updated_at
                    FROM projects 
                    ORDER BY created_at ASC
                """)
                
                projects = []
                for row in cursor.fetchall():
                    projects.append({
                        'project_id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'project_type': row[3],
                        'instance_number': row[4],
                        'working_directory': row[5],
                        'custom_command': row[6],
                        'status': row[7],
                        'created_at': row[8],
                        'updated_at': row[9]
                    })
                
                return projects
                
        except sqlite3.Error as e:
            print(f"Database error loading projects: {e}")
            return []
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            print(f"Database error deleting project: {e}")
            return False
    
    def update_project_status(self, project_id: int, status: str) -> bool:
        """Update project status in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE projects 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE project_id = ?
                """, (status, project_id))
                conn.commit()
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            print(f"Database error updating project status: {e}")
            return False
    
    def save_project_counters(self, counters: Dict[str, int]) -> bool:
        """Save project type counters to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for project_type, counter in counters.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO project_counters 
                        (project_type, counter, updated_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                    """, (project_type, counter))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            print(f"Database error saving counters: {e}")
            return False
    
    def load_project_counters(self) -> Dict[str, int]:
        """Load project type counters from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT project_type, counter FROM project_counters")
                
                counters = {}
                for row in cursor.fetchall():
                    counters[row[0]] = row[1]
                
                return counters
                
        except sqlite3.Error as e:
            print(f"Database error loading counters: {e}")
            return {}
    
    def save_app_setting(self, key: str, value: str) -> bool:
        """Save an application setting."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO app_settings 
                    (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, value))
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            print(f"Database error saving setting: {e}")
            return False
    
    def load_app_setting(self, key: str, default: str = None) -> Optional[str]:
        """Load an application setting."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
                result = cursor.fetchone()
                return result[0] if result else default
                
        except sqlite3.Error as e:
            print(f"Database error loading setting: {e}")
            return default
    
    def get_next_project_id(self) -> int:
        """Get the next available project ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(project_id) FROM projects")
                result = cursor.fetchone()
                return (result[0] or 0) + 1
                
        except sqlite3.Error as e:
            print(f"Database error getting next project ID: {e}")
            return 1
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Error creating database backup: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count projects by type
                cursor.execute("""
                    SELECT project_type, COUNT(*) 
                    FROM projects 
                    GROUP BY project_type
                """)
                project_counts = dict(cursor.fetchall())
                
                # Total projects
                cursor.execute("SELECT COUNT(*) FROM projects")
                total_projects = cursor.fetchone()[0]
                
                # Database size
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                return {
                    'total_projects': total_projects,
                    'project_counts': project_counts,
                    'database_size_bytes': db_size
                }
                
        except sqlite3.Error as e:
            print(f"Database error getting stats: {e}")
            return {}


# Global database instance
_db_instance = None

def get_database() -> ProjectDatabase:
    """Get the global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = ProjectDatabase()
    return _db_instance 