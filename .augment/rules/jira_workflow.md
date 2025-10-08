---
type: "always_apply"
description: "Mandatory guidelines for all development work including automatic Jira integration, tool selection, project standards, issue management, and API best practices. Automatically applies to all development tasks unless explicitly disabled."
---
# Jira Workflow Rules for PointCast Project

## Tool Selection Guidelines

### 🚀 **PRIMARY TOOL: Composio JIRA** (Use for 95% of cases)

**When to Use Composio JIRA:**
- ✅ **Daily Jira Operations** - Creating, updating, searching, commenting on issues
- ✅ **Bulk Operations** - Creating multiple issues (up to 50 at once)
- ✅ **User-Friendly Workflows** - When you need clean, readable responses
- ✅ **Advanced Features** - Sprint management, issue linking, user lookup
- ✅ **Production Automation** - Better error handling and validation
- ✅ **Markdown Support** - Rich text formatting in descriptions/comments
- ✅ **Smart User Assignment** - Using email addresses or display names
- ✅ **Sprint Management** - Moving issues to sprints, listing sprints
- ✅ **Issue Relationships** - Linking related issues with different types

**Key Composio Tools:**
- `JIRA_CREATE_ISSUE` - Create single issues with rich features
- `JIRA_BULK_CREATE_ISSUE` - Create multiple issues efficiently
- `JIRA_SEARCH_FOR_ISSUES_USING_JQL_GET` - Advanced search with clean results
- `JIRA_EDIT_ISSUE` - Update issues with smart field handling
- `JIRA_ADD_COMMENT` - Add comments with markdown support
- `JIRA_MOVE_ISSUE_TO_SPRINT` - Sprint management
- `JIRA_LINK_ISSUES` - Create issue relationships
- `JIRA_FIND_USERS` - User lookup and management
- `JIRA_TRANSITION_ISSUE` - Change issue status/workflow

### 🔧 **SECONDARY TOOL: Native Jira** (Use for specific cases)

**When to Use Native Jira Tool:**
- ✅ **Custom API Endpoints** - Accessing endpoints not covered by Composio
- ✅ **Raw API Access** - When you need complete field control
- ✅ **Custom Fields** - Direct manipulation of customfield_* fields
- ✅ **Debugging** - When you need raw API responses for troubleshooting
- ✅ **Edge Cases** - Unusual operations requiring full API flexibility
- ✅ **Legacy Integrations** - Maintaining existing workflows

**Decision Rule:** Always try Composio first, fall back to Native for edge cases.

## Project Information
- **Project Key**: PC
- **Project Name**: PointCast
- **Project ID**: 10007
- **Account ID**: 5f6b19f9d33d7600774a5c00 (Kelvin Law)

## Mandatory Ticket Requirements

### 1. Basic Fields (ALWAYS REQUIRED)
- **Summary**: Clear, descriptive title
- **Description**: Detailed problem description with technical details
- **Issue Type**: Bug, Story, Task, Epic, Subtask
- **Assignee**: Always assign to Kelvin Law (accountId: 5f6b19f9d33d7600774a5c00)
- **Priority**: Highest, High, Medium, Low, Lowest (use appropriate level)

### 2. Sprint and Planning (ALWAYS REQUIRED)
- **Sprint**: Always assign to "Sprint 1 (July 23 - Aug 11, 2025)"
- **Story Points**: Always assign story points (1-13 scale)
  - 1-2: Simple fixes, minor changes
  - 3-5: Standard features, moderate complexity
  - 8: Complex features, significant changes
  - 13: Major architectural changes

### 3. Epic Linking (ALWAYS REQUIRED)
- **Every ticket MUST be linked to an Epic**
- **If no suitable Epic exists, CREATE ONE**
- **Common Epic Categories**:
  - System Stability & Performance
  - Hardware Integration & Control
  - Network & Communication
  - User Interface & Experience
  - Security & Authentication

### 4. Labels (ALWAYS REQUIRED)
- **Technical Labels**: Based on technology/component
- **KM Label**: ALWAYS add "KM" for knowledge management
- **Priority Labels**: crash, critical, enhancement, etc.
- **Component Labels**: esp32, arduino, networking, ui, etc.

### 5. Implementation Details (ALWAYS REQUIRED)
- **Branch**: Which git branch the work is on
- **Commit Hash**: Full commit hash and message
- **Files Modified**: List of changed files with line numbers
- **Testing Instructions**: How to verify the fix/feature

## Issue Type Guidelines

### Bug Tickets
- **Priority**: High or Highest for crashes/critical issues
- **Labels**: crash, bug, stability, component-name, KM
- **Description Must Include**:
  - Error messages/stack traces
  - Steps to reproduce
  - Expected vs actual behavior
  - Root cause analysis
  - Fix implementation details

### Story/Feature Tickets
- **Priority**: Medium or High
- **Labels**: feature, enhancement, component-name, KM
- **Description Must Include**:
  - User story format
  - Acceptance criteria
  - Technical requirements
  - Implementation approach

### Task Tickets
- **Priority**: Medium
- **Labels**: task, maintenance, component-name, KM
- **Description Must Include**:
  - Clear task description
  - Deliverables
  - Success criteria

## Status Workflow
1. **To Do**: Initial state
2. **In Progress**: Work started
3. **TESTING**: Ready for validation
4. **Done**: Completed and verified

## Epic Management

### When to Create New Epic
- No existing Epic covers the work area
- New major feature or system component
- Significant architectural changes
- New integration or platform support

### Epic Naming Convention
- Format: "[Area] - [Purpose] - [Scope]"
- Examples:
  - "System Stability & Performance - Memory Management & Crash Prevention"
  - "Hardware Integration - Polariser Control & Calibration"
  - "Network Communication - Modem Integration & API Optimization"

## Comment Standards

### Implementation Comments
- Include branch and commit information
- List modified files with line numbers
- Provide testing instructions
- Document any breaking changes

### Status Update Comments
- Clear progress updates
- Any blockers or issues encountered
- Next steps or dependencies

## Metadata Audit Requirements

### For Completed Tickets
- Verify Epic linkage
- Ensure proper labels (including KM)
- Add commit information if missing
- Update story points if not assigned
- Verify sprint assignment

### For In-Progress Tickets
- Ensure all mandatory fields are populated
- Verify Epic linkage
- Check label completeness
- Confirm assignee and sprint

## Common Epics Reference

### PC-6: System Stability & Performance
- Memory management
- Crash prevention
- Performance optimization
- Boot loop fixes
- Watchdog timeouts

### Hardware Integration Epics
- Motor control and movement
- Sensor integration
- Polariser control
- Antenna positioning

### Network & Communication Epics
- Modem integration (Newtec, iDirect)
- API optimization
- SSL/TLS implementation
- Connectivity management

### User Interface Epics
- Web interface development
- Mobile responsiveness
- User experience improvements
- Dashboard functionality

## Automation Rules

### Auto-Assignment
- All tickets auto-assigned to Kelvin Law
- Sprint auto-assigned to current sprint

### Label Automation
- KM label automatically added
- Component labels based on affected files
- Priority labels based on issue type

### Epic Creation Triggers
- When no suitable Epic exists
- For new major feature areas
- For architectural changes

## Quality Checklist

Before closing any ticket, verify:
- [ ] Epic linked
- [ ] All required labels present (including KM)
- [ ] Story points assigned
- [ ] Sprint assigned
- [ ] Commit information documented
- [ ] Testing instructions provided
- [ ] Implementation details complete
- [ ] No co-author mentions in descriptions/comments

## Error Prevention

### Common Mistakes to Avoid
- Missing Epic linkage
- Forgetting KM label
- No story points assigned
- Missing commit information
- Incomplete testing instructions
- Co-author mentions in content

### Validation Steps
1. Check all mandatory fields
2. Verify Epic exists and is linked
3. Confirm label completeness
4. Validate commit documentation
5. Review testing instructions
