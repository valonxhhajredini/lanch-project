# Database Persistence Feature 🗄️

## Overview

Project Runner App V8 now includes **SQLite database persistence** to automatically save and restore your project state between sessions. This means your projects, settings, and preferences are preserved when you close and reopen the application.

## Features

### 🔄 **Automatic Project Persistence**
- **Project Data**: Names, descriptions, types, and instance numbers
- **Working Directories**: Last used directory for each project
- **Custom Commands**: Saved command entries for each project
- **Project Status**: Current status (created, running, stopped, etc.)
- **Project Counters**: Maintains proper numbering for new projects

### ⚙️ **Application Settings**
- **Theme Preference**: Light/dark theme selection
- **Window Geometry**: Size and position of the main window
- **Last Selected Project**: Automatically reopens your last active project

### 📊 **Database Management**
- **Automatic Backup**: Safe database operations with error handling
- **Statistics**: Track project counts and database usage
- **Migration Support**: Future-proof database schema

## How It Works

### 🚀 **On Application Start**
1. **Database Initialization**: Creates SQLite database if it doesn't exist
2. **Theme Restoration**: Loads your preferred theme (light/dark)
3. **Project Loading**: Restores all saved projects to the sidebar
4. **State Restoration**: Reopens your last selected project
5. **Window Positioning**: Restores window size and position

### 💾 **During Usage**
- **Real-time Saving**: Project changes are saved immediately
- **Status Updates**: Project status changes are persisted
- **Setting Changes**: Theme switches and preferences are saved instantly

### 🔒 **On Application Close**
1. **State Saving**: All current project data is saved
2. **Counter Preservation**: Project numbering is maintained
3. **Window Geometry**: Current window size/position is saved
4. **Process Cleanup**: Running processes are safely terminated

## Database Schema

### 📋 **Projects Table**
```sql
CREATE TABLE projects (
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
);
```

### ⚙️ **App Settings Table**
```sql
CREATE TABLE app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 🔢 **Project Counters Table**
```sql
CREATE TABLE project_counters (
    project_type TEXT PRIMARY KEY,
    counter INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Database Location

- **Default Location**: `project_runner.db` in the application directory
- **Portable**: Database file can be moved with the application
- **Backup-Friendly**: Standard SQLite format for easy backup

## Benefits

### 🎯 **User Experience**
- **Seamless Workflow**: Pick up exactly where you left off
- **No Data Loss**: Projects are never lost between sessions
- **Consistent State**: All settings and preferences preserved
- **Fast Startup**: Quick restoration of previous session

### 🛡️ **Reliability**
- **Error Handling**: Graceful fallback if database issues occur
- **Data Integrity**: Transactional operations ensure consistency
- **Backup Support**: Easy database backup and restore
- **Migration Ready**: Schema versioning for future updates

### 🔧 **Developer Benefits**
- **Clean Architecture**: Separated database logic in `core/database.py`
- **Type Safety**: Full type hints for all database operations
- **Testable**: Comprehensive test coverage for database operations
- **Extensible**: Easy to add new persistence features

## Usage Examples

### 📝 **Creating Projects**
1. Create projects normally through the UI
2. Projects are automatically saved to database
3. Working directories and commands are preserved
4. Project counters maintain proper numbering

### 🔄 **Session Restoration**
1. Close the application with projects open
2. Reopen the application
3. All projects appear in the sidebar
4. Last selected project is automatically opened
5. Working directories and commands are restored

### 🎨 **Theme Persistence**
1. Switch between light and dark themes
2. Theme preference is saved immediately
3. Application reopens with your preferred theme

## Technical Implementation

### 🏗️ **Architecture**
- **Database Module**: `core/database.py` - All SQLite operations
- **Main Window Integration**: Automatic save/load in `gui/main_window.py`
- **Global Instance**: Singleton pattern for database access
- **Error Handling**: Graceful degradation if database unavailable

### 🔧 **Key Methods**
- `save_project()`: Save/update project data
- `load_projects()`: Restore all projects
- `save_app_setting()`: Save application preferences
- `load_app_setting()`: Restore application preferences
- `get_database_stats()`: Monitor database usage

### 🧪 **Testing**
- **Unit Tests**: Comprehensive database operation testing
- **Integration Tests**: Full application persistence testing
- **Error Scenarios**: Database corruption and recovery testing

## Future Enhancements

### 🚀 **Planned Features**
- **Project Export/Import**: Share projects between installations
- **Database Encryption**: Optional encryption for sensitive projects
- **Cloud Sync**: Synchronize projects across devices
- **Project Templates**: Save and reuse project configurations
- **History Tracking**: Track project changes over time

### 📈 **Performance Optimizations**
- **Lazy Loading**: Load projects on-demand for large databases
- **Indexing**: Optimize queries for faster startup
- **Compression**: Reduce database size for large projects
- **Caching**: In-memory caching for frequently accessed data

## Troubleshooting

### 🔧 **Common Issues**

**Database File Locked**
- Close all application instances
- Check for background processes
- Restart the application

**Corrupted Database**
- Application will create a new database
- Previous projects will be lost
- Keep regular backups of `project_runner.db`

**Migration Errors**
- Check file permissions
- Ensure sufficient disk space
- Contact support with error details

### 🆘 **Recovery Options**
- **Fresh Start**: Delete `project_runner.db` to start clean
- **Backup Restore**: Replace with a known good backup
- **Manual Recovery**: Use SQLite tools to repair database

## Conclusion

The database persistence feature transforms Project Runner from a session-based tool to a **persistent project management solution**. Your work is automatically preserved, settings are remembered, and you can focus on development instead of recreating your workspace every time.

**Key Benefits:**
- ✅ **Zero Configuration**: Works automatically out of the box
- ✅ **Reliable**: Robust error handling and data integrity
- ✅ **Fast**: Quick startup and responsive operations
- ✅ **Extensible**: Ready for future enhancements

*Project Runner App V8 - Now with persistent project state!* 🎉