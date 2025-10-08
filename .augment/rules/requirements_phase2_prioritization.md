---
type: "manual"
description: "Phase 2: MoSCoW Prioritization. Assigns Must/Should/Could/Won't priorities with evidence-based business justification and stakeholder validation."
---

# Phase 2: MoSCoW Prioritization

## Objective
Assign Must/Should/Could/Won't priorities to all requirements using explicit criteria with evidence-based business justification and stakeholder validation.

## 🚨 CRITICAL CONSTRAINTS (ALWAYS REMEMBER)
- **NO LYING**: If evidence unavailable, say so and raise action
- **NO ASSUMPTIONS**: Every priority needs business justification
- **NO SPECULATION**: Do not guess about business value or stakeholder priorities
- **NO SINGLE-STAKEHOLDER DOMINANCE**: Validate priorities across stakeholder groups

## Context Refresh
**MANDATORY**: Read these memory files before proceeding:
- `.memories/[current-analysis]/01_initial_understanding.md`
- `.memories/[current-analysis]/02_discovery_log.md`
- `.memories/[current-analysis]/05_requirements_catalog.md`

## Phase 2 Tasks

### Task 1: Apply MoSCoW Classification Rules
**For each requirement, assign priority using explicit criteria:**

#### Must Have (Critical)
- **Criteria**: System cannot function without this requirement
- **Examples**: Legal/regulatory compliance, core business functionality, essential for MVP
- **Evidence Required**: Business case, regulatory documentation, or technical dependency proof
- **Test**: "If we don't deliver this, does the project fail?"

#### Should Have (Important)
- **Criteria**: Significant business value but system can function without it
- **Examples**: Enhances user experience, operational efficiency, planned for current release
- **Evidence Required**: Business value quantification or user impact analysis
- **Test**: "Would stakeholders be disappointed but project still viable?"

#### Could Have (Nice to Have)
- **Criteria**: Adds value but minimal impact if excluded
- **Examples**: Enhancement that improves satisfaction, can be deferred easily
- **Evidence Required**: User feedback or competitive analysis
- **Test**: "Would this be a pleasant surprise if delivered?"

#### Won't Have (Out of Scope)
- **Criteria**: Explicitly excluded from current scope
- **Examples**: Future consideration, conflicts with higher priorities, resource constraints
- **Evidence Required**: Explicit stakeholder decision or resource constraint documentation
- **Test**: "Is this explicitly out of scope for this release?"

### Task 2: Business Value Analysis
**For each Must/Should requirement:**
1. **Quantify Impact**: What business value does this deliver?
2. **Identify Stakeholder Owner**: Who champions this requirement?
3. **Document Rationale**: Why is this priority justified?
4. **Evidence Source**: What evidence supports this priority?

### Task 3: Stakeholder Validation
**Validate priorities across stakeholder groups:**
1. **Business Stakeholders**: Do priorities align with business goals?
2. **Technical Stakeholders**: Are technical dependencies considered?
3. **User Representatives**: Do priorities reflect user needs?
4. **Compliance/Legal**: Are regulatory requirements properly prioritized?

### Task 4: Priority Conflict Resolution
**If conflicts arise:**
1. **Document Conflict**: What requirements or stakeholders conflict?
2. **Gather Evidence**: What evidence supports each position?
3. **Facilitate Resolution**: Use MCP Feedback to clarify with user/stakeholders
4. **Document Decision**: Record final priority with rationale

### Task 5: Update Requirements Catalog
**For each requirement, add:**
- **MoSCoW Priority**: Must/Should/Could/Won't
- **Priority Justification**: Evidence-based rationale
- **Stakeholder Owner**: Who champions this requirement
- **Business Value**: Quantified impact where possible

## Tools & Iterations
- **Sequential Thinking Tool**: 3-5 rounds for priority analysis and conflict resolution
- **MCP Feedback Tool**: For stakeholder validation and conflict resolution
- **Evidence Collection**: Business cases, stakeholder input, regulatory requirements

## Expected Outputs
- **Update**: `02_discovery_log.md` with prioritization process and decisions
- **Update**: `05_requirements_catalog.md` with MoSCoW priorities and justifications
- **Document**: Priority conflicts and resolutions

## MoSCoW Priority Template
```
REQ-ID: [ID]
Priority: [Must/Should/Could/Won't]
Justification: [Evidence-based rationale]
Stakeholder Owner: [Name/Role]
Business Value: [Quantified impact]
Evidence: [Source supporting this priority]
```

## Priority Summary Template
**Create summary in `02_discovery_log.md`:**
```
## MoSCoW Priority Summary
- Must Have: [X] requirements - [Brief description of critical needs]
- Should Have: [Y] requirements - [Brief description of important needs]
- Could Have: [Z] requirements - [Brief description of nice-to-haves]
- Won't Have: [W] requirements - [Brief description of out-of-scope items]

## Top 5 Must Requirements (by business value)
1. [REQ-ID]: [Description] - [Business value]
2. [REQ-ID]: [Description] - [Business value]
...
```

## Quality Check
- [ ] All requirements have MoSCoW priority assigned
- [ ] All Must/Should requirements have business justification
- [ ] All priorities have stakeholder owner identified
- [ ] Priority conflicts documented and resolved
- [ ] Evidence supports all priority decisions
- [ ] Priority summary completed

## Common Prioritization Mistakes to Avoid
- **Everything is Must**: Apply strict criteria - not everything can be critical
- **No Business Justification**: Every Must/Should needs evidence-based rationale
- **Technical Bias**: Don't prioritize based on technical interest alone
- **Stakeholder Dominance**: Balance input from all stakeholder groups
- **Scope Creep**: Don't upgrade priorities without business justification

## Navigation
**NEXT PHASE**: Read and execute `.augment/rules/requirements_phase3_feasibility.md`

**CRITICAL**: Do not proceed to Phase 3 until:
1. All requirements have MoSCoW priority assigned
2. All Must/Should requirements have business justification with evidence
3. Priority conflicts are resolved and documented
4. Priority summary is completed
5. Stakeholder owners are identified for key requirements

**REFERENCE**: For detailed methodology, see `requirements_analysis.md` Phase 2 section and MoSCoW framework.
