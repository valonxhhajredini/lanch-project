# Multi-Instance Project Manager - Task Definition

## Overview
Transform the current single-project runner into a multi-instance project manager with tabbed interface.

## User Story
As a developer, I want to:
1. Create multiple project instances in one application window
2. Run different projects (Laravel, Angular, Custom) simultaneously
3. Manage each project independently with its own output and controls
4. Switch between projects using tabs
5. Have a clean interface to create new instances

## Current State
- Single project runner with one output window
- Project type selection changes the command for current instance
- One set of controls (Run/Stop) for one project

## Target State
- Multi-tabbed interface with project instances
- "Create New Instance" landing page/tab
- Each tab contains:
  - Project type selection (Laravel/Angular/Custom)
  - Directory selector
  - Command entry (auto-filled based on project type)
  - Output display
  - Run/Stop controls
- Independent process management per tab

## Technical Requirements

### UI Structure
```
Main Window
├── Tab Bar
│   ├── "+" (Create New Instance)
│   ├── "Laravel Project" (Instance 1)
│   ├── "Angular App" (Instance 2)
│   └── "Custom Script" (Instance 3)
└── Tab Content Area
    ├── Project Configuration (top)
    ├── Output Display (middle)
    └── Control Buttons (bottom)
```

### Features
1. **Create New Instance Tab**
   - Welcome message
   - Project type selection
   - "Create Instance" button
   - Auto-generates tab name based on project type

2. **Project Instance Tabs**
   - Closeable tabs (except create new)
   - Independent process handlers
   - Unique tab names (Laravel Project 1, Laravel Project 2, etc.)
   - Tab context menu (rename, close)

3. **Process Management**
   - Each tab has its own ProcessHandler
   - Independent port management
   - Simultaneous project execution
   - Proper cleanup on tab close

### Implementation Plan
1. Create tabbed interface using ttk.Notebook
2. Refactor MainWindow to manage multiple instances
3. Create InstanceTab class for individual project tabs
4. Implement CreateInstanceTab for new project creation
5. Update process management for multi-instance support
6. Add tab management (create, close, rename)

## Acceptance Criteria
- [ ] User can create multiple project instances
- [ ] Each instance runs independently
- [ ] Tabs show project type and status
- [ ] Can run multiple projects simultaneously
- [ ] Clean tab management (create/close)
- [ ] Proper process cleanup on tab close
- [ ] Intuitive user interface 