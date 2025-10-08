---
type: "manual"
description: "PRP (Purpose, Requirements, Plan) document execution workflow. Apply when implementing structured features or fixes that have been pre-planned in PRP documents, requiring systematic implementation with validation loops."
---

# Execute PRP (Purpose, Requirements, Plan) Document

## Description
This command executes a PRP document to implement the specified feature or fix. It follows the structured implementation plan and validation loops defined in the PRP.

## Usage
```
/execute-prp [prp_file_path]
```

## Parameters
- `prp_file_path`: Path to the PRP document to execute (e.g., "PRPs/fleet_manager_enhancement.md")

## Execution Process

### 1. Context Loading
- Load all referenced documentation and examples
- Verify current codebase state matches PRP assumptions
- Identify any changes since PRP creation

### 2. Implementation Phase
- Execute tasks in the order specified in the PRP
- Follow pseudocode and implementation guidelines
- Maintain existing code patterns and conventions
- Apply integration points as specified

### 3. Validation Phase
- **Level 1**: Run syntax and style checks
  - Arduino CLI compilation with `--warnings all`
  - Code formatting verification
- **Level 2**: Execute unit tests
  - Run existing test suites
  - Execute new tests defined in PRP
- **Level 3**: Integration testing
  - Hardware-in-the-loop testing where applicable
  - System integration verification

### 4. Documentation Update
- Update relevant documentation files
- Add implementation notes to memories/
- Update CHANGELOG.md if applicable

## Safety Checks
- Always backup current working state before major changes
- Use git commits at logical checkpoints
- Verify compilation success before proceeding to next task
- Test on hardware when possible

## Error Handling
- If compilation fails, analyze errors and fix before proceeding
- If tests fail, understand root cause and fix code (never mock to pass)
- If integration issues arise, review PRP assumptions and adjust

## Post-Execution
- Verify all success criteria from PRP are met
- Update task status in project management system
- Document any deviations from original PRP
- Suggest follow-up PRPs if needed

## Notes
- Never skip validation steps
- Always follow existing codebase patterns
- Use MCP feedback for user communication with 86400 second timeout
- Maintain compliance with memories/user_preferences.md
