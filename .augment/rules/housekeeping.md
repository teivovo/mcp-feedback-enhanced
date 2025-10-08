---
type: "agent_requested"
description: "Comprehensive project housekeeping and organization procedures. Apply when project maintenance, cleanup, or organization is needed. Must use sequential thinking, shrimp task manager, and feedback tools."
---
<!-- RULE DESCRIPTION: Comprehensive project housekeeping and organization procedures. Apply when project maintenance, cleanup, or organization is needed. Must use sequential thinking, shrimp task manager, and feedback tools. -->

# Project Housekeeping Rules

## Rule Type: `auto`

## Overview
This rule defines comprehensive housekeeping procedures to maintain project organization, update documentation, manage logs, and ensure all project artifacts are properly organized and up-to-date.

## Critical Note - Take your time to do this. It is prohibited to edit any code or move any files that may break functionality during this operation.

## Mandatory Tool Usage
**CRITICAL**: All housekeeping operations MUST use:
1. **Sequential Thinking** - Plan and analyze housekeeping tasks systematically
2. **Shrimp Task Manager** - Break down and track housekeeping activities
3. **MCP Feedback Tool** - Report progress and get user confirmation for major changes

## Housekeeping Areas

### 1. Log Management
**Objective**: Organize and archive all log files properly

**Actions Required**:
- Move old compilation logs from `Motherboard/buffers/` to `logs/archive/compilation/`
- Archive serial monitor logs to `logs/archive/serial/`
- Organize performance analysis logs in `logs/archive/performance/`
- Maintain only recent logs (last 7 days) in active directories
- Create dated archive folders (YYYY-MM-DD format)

### 2. Documentation Organization
**Objective**: Ensure all documentation is current, properly located, and organized

**Actions Required**:
- Move technical documentation to `docs/` folder structure
- Update outdated documentation with current technical details
- Remove obsolete or superseded documentation
- Organize documentation by category:
  - `docs/technical/` - Technical specifications and analysis
  - `docs/api/` - API documentation and integration guides
  - `docs/hardware/` - Hardware setup and configuration
  - `docs/troubleshooting/` - Error resolution and debugging guides
- Ensure all documentation has proper headers and metadata
- Update version information and last-modified dates

### 3. Jira Task Management
**Objective**: Review and update all Jira tasks with current status and information

**Actions Required**:
- Review all open tasks and suggest status updates
- Close completed tasks with proper documentation links
- Update task descriptions with latest technical details
- Link tasks to relevant code changes and commits
- Add implementation details and testing results
- Update story points if scope changed
- Ensure all tasks have proper Epic linkage
- Add "KM" labels for knowledge management
- Present task list with status recommendations to user

### 4. Ruleset Maintenance
**Objective**: Keep all rulesets current with latest procedures and technical information

**Actions Required**:
- Review existing rulesets for outdated information
- Update technical procedures based on recent changes
- Add new rules for discovered best practices
- Update rule descriptions and application scenarios
- Ensure rule index is current and accurate
- Validate rule syntax and formatting

### 5. Script Organization
**Objective**: Organize supporting scripts in proper folder structure

**Actions Required**:
- Move compilation scripts to `scripts/compilation/`
- Move testing scripts to `scripts/testing/`
- Move utility scripts to `scripts/utilities/`
- Move deployment scripts to `scripts/deployment/`
- Ensure all scripts have proper headers and documentation
- Update script paths in documentation
- Verify script functionality after moving

### 6. General Project Organization
**Objective**: Marie Kondo the project folder without disrupting working code

**Actions Required**:
- Organize temporary files and remove unnecessary ones
- Clean up root directory of non-essential files
- Ensure proper folder structure is maintained
- Remove duplicate files and outdated versions
- Organize configuration files properly
- Maintain clean separation between source code and artifacts

**Safety Rules**:
- NEVER move or delete source code files
- NEVER modify working configuration files
- ALWAYS backup before major reorganization
- GET USER CONFIRMATION for any destructive operations

## Execution Workflow

### Phase 1: Planning (Sequential Thinking)
1. Analyze current project state
2. Identify all areas needing housekeeping
3. Plan safe execution order
4. Identify potential risks and mitigation strategies

### Phase 2: Task Management (Shrimp Task Manager)
1. Break down housekeeping into specific tasks
2. Set priorities and dependencies
3. Track progress through each area
4. Update task status as work progresses

### Phase 3: Execution and Reporting (MCP Feedback)
1. Execute housekeeping tasks systematically
2. Report progress and findings to user
3. Get confirmation for major changes
4. Present final status and recommendations

### Phase 4: Jira Integration
1. Review all open Jira tasks
2. Present task list with status recommendations
3. Update tasks based on user decisions
4. Close completed tasks with proper documentation

## Quality Assurance

### Before Execution
- Backup critical files and configurations
- Verify no active development work will be disrupted
- Confirm user availability for decision-making

### During Execution
- Document all changes made
- Maintain audit trail of moved/modified files
- Test critical functionality after changes
- Report any issues immediately

### After Execution
- Verify all systems still function correctly
- Update documentation with new organization
- Provide summary of all changes made
- Get user confirmation of satisfactory completion
- Call the Shrimp Update Project Rules tool

## Emergency Procedures
If any housekeeping operation causes issues:
1. STOP immediately
2. Document the problem
3. Restore from backup if necessary
4. Report to user via MCP Feedback
5. Get guidance before proceeding

## Success Criteria
- All logs properly archived and organized
- Documentation current and properly located
- Jira tasks updated with accurate status
- Scripts organized in logical folder structure
- Project folder clean and well-organized
- No disruption to working code or functionality
- Call feedback tool when housekeeping is complete
- User satisfied with organization and cleanliness
