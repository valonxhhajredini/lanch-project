# Multi-Instance Project Manager - Task Definition (Updated Design)

## Overview
Transform the current tabbed interface into a sidebar-based project manager with visual status indicators.

## User Story
As a developer, I want to:
1. See all my project instances in a sidebar list
2. Visual status indicators (green=running, red=stopped, yellow=starting)
3. Click on projects in the sidebar to switch between them
4. Create new instances with a prominent "+" button
5. Have a clean, dashboard-like interface

## Current State (V6)
- Tabbed interface with "+ Create New" tab
- Each tab contains project configuration and output
- Independent process management per tab

## Target State (V7 - Sidebar Design)
- **Left Sidebar**: Project list with status indicators
- **Main Area**: Selected project's configuration and output
- **Status Colors**: 
  - 🟢 Green: Project running
  - 🔴 Red: Project stopped
  - 🟡 Yellow: Project starting/stopping
  - ⚪ Gray: Project created but never run

## Technical Requirements

### UI Structure
```
Main Window
├── Left Sidebar (200px width)
│   ├── "Create New Project" Button
│   ├── Project List
│   │   ├── [🟢] Laravel Project 1
│   │   ├── [🔴] Angular App 1  
│   │   ├── [🟡] Custom Script 1
│   │   └── [⚪] Laravel Project 2
│   └── Status Legend
└── Main Content Area
    ├── Project Configuration (top)
    ├── Output Display (middle)
    └── Control Buttons (bottom)
```

### Features
1. **Sidebar Project List**
   - Clickable project items
   - Color-coded status indicators
   - Project type icons
   - Delete/rename context menu

2. **Status Indicators**
   - Real-time status updates
   - Color coding for quick visual feedback
   - Status text (Running, Stopped, Starting, etc.)

3. **Main Content Area**
   - Shows selected project's interface
   - Welcome screen when no project selected
   - Same functionality as current tabs

### Implementation Plan
1. Replace ttk.Notebook with custom sidebar + main area layout
2. Create ProjectSidebar widget with status indicators
3. Create ProjectListItem widget for individual projects
4. Implement status management and color updates
5. Add project selection and switching logic
6. Enhance with icons and better visual design

## Acceptance Criteria
- [x] User can create multiple project instances
- [x] Each instance runs independently  
- [ ] Sidebar shows all projects with status indicators
- [ ] Color-coded status (green=running, red=stopped, etc.)
- [ ] Click to switch between projects
- [x] Can run multiple projects simultaneously
- [ ] Clean project management (create/delete)
- [x] Proper process cleanup on project deletion
- [x] Intuitive user interface

## Implementation Status: 🔄 IN PROGRESS (V7 - Sidebar Design)

### What's Working (V6)
- ✅ Multi-instance support
- ✅ Independent process management
- ✅ Real-time output streaming
- ✅ Port management per instance

### V7 Goals - Sidebar Design
- [ ] Left sidebar with project list
- [ ] Color-coded status indicators
- [ ] Project selection and switching
- [ ] Enhanced visual design
- [ ] Better user experience

### Future Enhancements
- [ ] Project type icons (Laravel, Angular, Custom)
- [ ] Right-click context menu (rename, delete, duplicate)
- [ ] Drag and drop project reordering
- [ ] Project templates and quick setup
- [ ] Save/restore workspace sessions 