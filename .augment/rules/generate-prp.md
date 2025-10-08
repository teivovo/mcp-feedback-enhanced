---
type: "manual"
description: "PRP (Purpose, Requirements, Plan) document generation for structured feature planning. Apply when planning new features, complex fixes, or major code changes that require comprehensive documentation and implementation blueprints."
---

# Generate PRP (Purpose, Requirements, Plan) Document

## Description
This command generates a comprehensive PRP document for implementing new features or fixing issues in the PointCast ACU firmware. The PRP follows a structured format that ensures all necessary context is provided for successful implementation.

## Usage
```
/generate-prp [feature_name] [complexity]
```

## Parameters
- `feature_name`: Name of the feature or fix to implement (e.g., "fleet-manager-authentication")
- `complexity`: Estimated complexity level (simple, moderate, complex)

## Template Structure

### Purpose
- **Goal**: Clear statement of what needs to be built
- **Why**: Business value, user impact, integration with existing features
- **What**: User-visible behavior and technical requirements
- **Success Criteria**: Specific measurable outcomes

### All Needed Context
- **Documentation & References**: All context needed to implement the feature
- **Current Codebase Tree**: Overview of relevant files
- **Desired Codebase Tree**: Files to be added/modified
- **Known Gotchas**: Critical implementation details and library quirks

### Implementation Blueprint
- **Data Models and Structure**: Core data models for type safety and consistency
- **Task List**: Ordered list of tasks to fulfill the PRP
- **Per-Task Pseudocode**: Critical implementation details
- **Integration Points**: Database, config, routes, etc.

### Validation Loop
- **Level 1**: Syntax & style checks
- **Level 2**: Unit tests
- **Level 3**: Integration tests
- **Final Validation Checklist**: Comprehensive verification

### Anti-Patterns to Avoid
- Common pitfalls and mistakes to avoid

## Example
See `PRPs/templates/prp_base.md` for the base template and `PRPs/EXAMPLE_multi_agent_prp.md` for a complete example.

## Notes
- Always include ALL necessary documentation and examples
- Provide executable tests/lints for validation
- Use keywords and patterns from the existing codebase
- Start simple, validate, then enhance
- Follow all global rules in CLAUDE.md
