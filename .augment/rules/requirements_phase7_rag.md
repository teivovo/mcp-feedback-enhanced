---
type: "manual"
description: "Phase 7: RAG Dashboard & Executive Communication. Creates Red/Amber/Green status framework and one-page executive summary for decision-making."
---

# Phase 7: RAG Dashboard & Executive Communication

## Objective
Create Red/Amber/Green status framework for all Must requirements and generate one-page executive summary for leadership decision-making.

## 🚨 CRITICAL CONSTRAINTS (ALWAYS REMEMBER)
- **NO LYING**: If evidence unavailable, say so and raise action
- **NO ASSUMPTIONS**: Every RAG status needs evidence-based justification
- **NO SPECULATION**: Do not guess about status or implications
- **EXECUTIVE FOCUS**: Keep summary concise and decision-oriented

## Context Refresh
**MANDATORY**: Read these memory files before proceeding:
- `.memories/[current-analysis]/02_discovery_log.md`
- `.memories/[current-analysis]/05_requirements_catalog.md`
- `.memories/[current-analysis]/06_decision_matrix.md`

## Phase 7 Tasks

### Task 1: Apply RAG Classification Rules
**For all Must requirements, assign status:**

#### 🟢 Green: Ready to Proceed
- **Criteria**: Must requirement with PACT=Yes and Low risk (≤9)
- **Evidence**: Strong feasibility assessment with confidence ≥4
- **Implication**: Can proceed with implementation as specified

#### 🟡 Amber: Conditional Proceed
- **Criteria**: Must requirement with Partial feasibility and accepted Option
- **Evidence**: Viable option identified with acceptable trade-offs
- **Implication**: Can proceed with approved option/mitigation

#### 🔴 Red: Blocked/High Risk
- **Criteria**: Must requirement with No feasibility or unmitigated High risk (≥16)
- **Evidence**: Significant barriers or unacceptable risks
- **Implication**: Requires major changes or scope reduction

### Task 2: Create RAG Dashboard
**Document in structured format:**

#### RAG Summary Table
| REQ-ID | Description | Priority | RAG Status | Key Issue | Mitigation/Option | Owner | Due Date |
|--------|-------------|----------|------------|-----------|-------------------|-------|----------|
| REQ-F-001 | [≤25 words] | Must | 🔴 Red | Technology constraint | Option A: Alternative approach | [Name] | [Date] |

#### RAG Statistics
- **🟢 Green**: [X] Must requirements ([Y]% of total)
- **🟡 Amber**: [X] Must requirements ([Y]% of total)
- **🔴 Red**: [X] Must requirements ([Y]% of total)

### Task 3: Executive Summary Framework
**Create one-page summary including:**

#### Scope Overview
- Total requirements by type (Functional/Non-Functional/Constraints)
- Total requirements by priority (Must/Should/Could/Won't)
- Key stakeholders and their primary concerns

#### RAG Summary
- Count and percentage of Red/Amber/Green status
- Critical path items requiring immediate attention
- Overall project health assessment

#### Key Decisions Needed
- Top 3 decisions requiring leadership input
- Options requiring stakeholder approval
- Resource allocation decisions

#### Resource Impact
- High-level cost implications (order of magnitude)
- Timeline impact of current status
- Skill/capacity requirements

#### Risk Highlights
- Top 3 risks requiring executive attention
- Risks that could impact project success
- Mitigation strategies requiring investment

#### Recommendation
- **Go**: Proceed with current scope and approach
- **Go-with-Options**: Proceed with specified options/changes
- **No-Go**: Significant issues require major replanning

### Task 4: Create Decision-Ready Package

## Tools & Iterations
- **Sequential Thinking Tool**: 3-5 rounds for RAG analysis and executive summary
- **Evidence Synthesis**: Consolidate findings from all previous phases
- **Communication Focus**: Ensure executive-level clarity and actionability

## Expected Outputs
- **Create**: RAG dashboard in `06_decision_matrix.md`
- **Create**: Executive summary in `04_final_comparison.md`
- **Update**: `02_discovery_log.md` with RAG analysis process

## RAG Dashboard Template
```
# RAG Dashboard - [Analysis Name]
Date: [YYYY-MM-DD]

## RAG Summary
- 🟢 Green: [X] Must requirements ([Y]%)
- 🟡 Amber: [X] Must requirements ([Y]%)
- 🔴 Red: [X] Must requirements ([Y]%)

## Critical Items Requiring Attention
[List of Red and high-priority Amber items]

## Resource Requirements
[High-level summary of needs]

## Timeline Impact
[Key timeline implications]

## Recommendation
[Go/Go-with-Options/No-Go with rationale]
```

## Executive Summary Template
```
# Executive Summary - [Analysis Name]
Date: [YYYY-MM-DD]

## Project Overview
Scope: [Brief description]
Stakeholders: [Key parties]
Timeline: [Key dates]

## Requirements Summary
- Total: [X] requirements ([F] Functional, [N] Non-Functional, [C] Constraints)
- Must Have: [X] requirements
- Should Have: [Y] requirements
- Could Have: [Z] requirements

## Status Summary (Must Requirements Only)
- 🟢 Green (Ready): [X] requirements ([Y]%)
- 🟡 Amber (Conditional): [X] requirements ([Y]%)
- 🔴 Red (Blocked): [X] requirements ([Y]%)

## Key Decisions Needed
1. [Decision 1] - [Impact] - [Due Date]
2. [Decision 2] - [Impact] - [Due Date]
3. [Decision 3] - [Impact] - [Due Date]

## Resource Impact
- Cost: [Order of magnitude]
- Timeline: [Key implications]
- Skills: [Critical needs]

## Top 3 Risks
1. [Risk] - [Impact] - [Mitigation]
2. [Risk] - [Impact] - [Mitigation]
3. [Risk] - [Impact] - [Mitigation]

## Recommendation
[Go/Go-with-Options/No-Go]

Rationale: [Evidence-based reasoning]
Conditions: [Any conditions for success]
Next Steps: [Immediate actions required]
```

## Quality Check
- [ ] All Must requirements have RAG status assigned
- [ ] RAG status supported by evidence from previous phases
- [ ] Executive summary is one page and decision-focused
- [ ] Key decisions clearly identified with owners and dates
- [ ] Resource and timeline implications quantified
- [ ] Clear recommendation with rationale provided

## Navigation
**NEXT PHASE**: Read and execute `.augment/rules/requirements_phase8_testing.md`

**CRITICAL**: Do not proceed to Phase 8 until:
1. All Must requirements have RAG status assigned
2. RAG dashboard is complete with evidence
3. Executive summary is concise and decision-ready
4. Key decisions are identified with owners
5. Clear recommendation is provided with rationale

**REFERENCE**: For detailed methodology, see `requirements_analysis.md` Phase 7 section.
