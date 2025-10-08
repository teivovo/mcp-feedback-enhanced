---
type: "manual"
description: "Phase 4: Options Analysis. Develops A/B/C alternatives for requirements with Partial/No PACT feasibility, including cost/timeline/risk analysis."
---

# Phase 4: Options Analysis

## Objective
Develop Option A/B/C alternatives for any requirement with PACT verdict = Partial or No, including cost/timeline/risk analysis and impact assessment on fit criteria.

## 🚨 CRITICAL CONSTRAINTS (ALWAYS REMEMBER)
- **NO LYING**: If evidence unavailable, say so and raise action
- **NO ASSUMPTIONS**: Every option needs evidence-based analysis
- **NO SPECULATION**: Do not guess about costs, timelines, or feasibility
- **NO GOLD-PLATING**: Focus on viable alternatives, not wish lists

## Context Refresh
**MANDATORY**: Read these memory files before proceeding:
- `.memories/[current-analysis]/02_discovery_log.md`
- `.memories/[current-analysis]/05_requirements_catalog.md`
- Review PACT assessments from Phase 3

## Phase 4 Tasks

### Task 1: Identify Requirements Needing Options
**Filter requirements where:**
- PACT Overall Verdict = Partial OR No
- Priority = Must OR Should (focus on important requirements)
- High risk score (≥16 on 1-25 scale)

### Task 2: Option Generation Framework
**For each requirement needing options, develop:**

#### Option A: Minimal Change Approach
- **Purpose**: Achieve core intent with minimal modifications
- **Approach**: Smallest viable change to meet requirement
- **Trade-offs**: May compromise on performance or features

#### Option B: Alternative Approach
- **Purpose**: Different technical/business approach with different trade-offs
- **Approach**: Alternative implementation or scope modification
- **Trade-offs**: Different cost/benefit profile

#### Option C: Scope Reduction/Phased Implementation
- **Purpose**: Reduce scope or implement in phases
- **Approach**: Deliver partial functionality or defer complex parts
- **Trade-offs**: Reduced immediate value but lower risk

#### Option D: Out-of-Scope (Won't Have)
- **Purpose**: Explicitly exclude with future consideration
- **Approach**: Remove from current scope entirely
- **Trade-offs**: No immediate value but eliminates risk/cost

### Task 3: Required Analysis per Option
**For each option, document:**

#### Change Summary
- What deviates from original requirement
- What functionality is modified or removed
- What new dependencies are introduced

#### Fit Criterion Impact
- How success measurement changes
- What acceptance criteria are modified
- Whether original business value is preserved

#### Cost/Timeline Estimate
- Order-of-magnitude effort (days/weeks/months)
- Resource requirements (people, skills, tools)
- Dependencies on other work or teams

#### Risk Profile
- Top 3 risks with likelihood (1-5) and impact (1-5)
- Risk score calculation (probability × impact)
- Specific mitigation strategies

#### Dependency Changes
- New dependencies introduced
- Dependencies removed or modified
- Impact on other requirements

#### Stakeholder Impact
- Who is affected by this option
- How their experience changes
- Required stakeholder approval

### Task 4: Option Decision Criteria
**Evaluate each option against:**
- **Feasibility**: Can this actually be implemented?
- **Value**: Does this deliver meaningful business benefit?
- **Cost**: Is the effort justified by the outcome?
- **Risk**: Are risks acceptable and mitigatable?
- **Alignment**: Does this support overall project goals?

### Task 5: Create Options Analysis Documentation

## Tools & Iterations
- **Sequential Thinking Tool**: 5-7 rounds for option development and analysis
- **Evidence Collection**: Cost estimates, technical feasibility, stakeholder impact
- **Risk Assessment**: Systematic risk analysis for each option

## Expected Outputs
- **Update**: `02_discovery_log.md` with options analysis process
- **Create**: Options analysis section in `05_requirements_catalog.md`
- **Document**: Complete option analysis for all Partial/No feasibility requirements

## Options Analysis Template (Copy-Paste)
| REQ-ID | Option | Summary | Fit Impact | Cost/Timeline (OOM) | Top 3 Risks | Mitigations | Decision |
|--------|--------|---------|------------|---------------------|-------------|-------------|----------|
| REQ-F-001 | A | [Change description] | [Impact on fit criterion] | [Order of magnitude] | [Risk 1, 2, 3] | [Specific actions] | Go/No-Go |

## Detailed Option Analysis Template
```
REQ-ID: [ID] - [Original Requirement]
Original PACT Verdict: [Partial/No] - [Key constraints]

## Option A: [Name]
Change Summary: [What changes from original]
Fit Criterion Impact: [How success criteria change]
Cost/Timeline: [Order of magnitude estimate]
Resource Requirements: [People, skills, tools needed]
Top 3 Risks:
1. [Risk] - Probability: [1-5], Impact: [1-5], Score: [1-25]
2. [Risk] - Probability: [1-5], Impact: [1-5], Score: [1-25]
3. [Risk] - Probability: [1-5], Impact: [1-5], Score: [1-25]
Mitigations: [Specific actions to reduce risks]
Stakeholder Impact: [Who affected and how]
Dependencies: [New/changed dependencies]
Evidence: [Sources supporting this analysis]

## Option B: [Name]
[Same structure as Option A]

## Option C: [Name]
[Same structure as Option A]

## Recommendation
Preferred Option: [A/B/C/D]
Rationale: [Evidence-based reasoning]
Conditions: [Any conditions for success]
```

## Quality Check
- [ ] All Partial/No feasibility requirements have options analysis
- [ ] All options have cost/timeline estimates (order of magnitude)
- [ ] All options have risk analysis with mitigation strategies
- [ ] Fit criterion impact documented for each option
- [ ] Stakeholder impact assessed for each option
- [ ] Evidence supports all option analysis
- [ ] Recommendation provided with rationale

## Common Options Analysis Mistakes
- **Only Technical Options**: Consider business/scope alternatives too
- **Unrealistic Estimates**: Use evidence-based cost/timeline estimates
- **Ignoring Stakeholder Impact**: Consider who is affected by changes
- **Missing Risk Mitigation**: Every risk needs specific mitigation strategy
- **No Clear Recommendation**: Must provide preferred option with rationale

## Navigation
**NEXT PHASE**: Read and execute `.augment/rules/requirements_phase5_gates.md`

**CRITICAL**: Do not proceed to Phase 5 until:
1. All Partial/No feasibility requirements have options analysis
2. All options have complete analysis (cost, risk, impact)
3. Evidence supports all option assessments
4. Clear recommendations provided for each requirement
5. Stakeholder impact documented for all options

**REFERENCE**: For detailed methodology, see `requirements_analysis.md` Phase 4 section and options analysis framework.
