---
type: "manual"
description: "Phase 5: Decision Gates. Applies 4-gate framework for go/no-go decisions with clear pass/fail criteria and evidence requirements."
---

# Phase 5: Decision Gates

## Objective
Apply 4-gate decision framework to determine go/no-go status for the requirements package with clear pass/fail criteria and evidence-based decisions.

## 🚨 CRITICAL CONSTRAINTS (ALWAYS REMEMBER)
- **NO LYING**: If evidence unavailable, say so and raise action
- **NO ASSUMPTIONS**: Every gate decision needs real evidence
- **NO SPECULATION**: Do not guess about readiness or viability
- **NO SHORTCUTS**: All gates must pass before proceeding

## Context Refresh
**MANDATORY**: Read these memory files before proceeding:
- `.memories/[current-analysis]/02_discovery_log.md`
- `.memories/[current-analysis]/05_requirements_catalog.md`
- Review all previous phase outputs

## Phase 5 Tasks

### Task 1: Gate 1 - Requirement Readiness
**Criteria**: No open clarifications; all fit criteria testable

#### Assessment Checklist
- [ ] All requirements have complete Volere templates
- [ ] All fit criteria are measurable with units and thresholds
- [ ] No open questions or clarifications pending
- [ ] All requirements are atomic (single purpose, single outcome)
- [ ] Evidence quotes support all requirements

#### Evidence Required
- Complete requirement templates with evidence quotes
- Testable fit criteria for all requirements
- Resolution of all clarification requests

#### Decision Options
- **Pass**: Ready for feasibility assessment
- **Fail**: Needs clarification - return to Phase 1

### Task 2: Gate 2 - Feasibility Assessment
**Criteria**: All Must requirements have PACT=Yes or approved option

#### Assessment Checklist
- [ ] All Must requirements have PACT assessment completed
- [ ] Must requirements with Partial/No feasibility have approved options
- [ ] Confidence scores ≥3 for all Must requirement assessments
- [ ] Evidence supports all feasibility verdicts
- [ ] Options analysis completed for non-feasible Must requirements

#### Evidence Required
- PACT analysis with confidence scores ≥3
- Options analysis for all Partial/No feasibility Must requirements
- Evidence supporting all feasibility assessments

#### Decision Options
- **Pass**: Feasible as specified
- **Conditional**: Feasible with approved options
- **Fail**: Requires options analysis or scope reduction

### Task 3: Gate 3 - Risk Acceptability
**Criteria**: No unmitigated high-risk Must requirements

#### Assessment Checklist
- [ ] Risk register completed for all requirements
- [ ] High-risk requirements (score ≥16) have mitigation plans
- [ ] Mitigation strategies are specific and actionable
- [ ] Risk owners assigned for high-risk items
- [ ] Residual risk levels are acceptable

#### Evidence Required
- Risk register with probability × impact scoring
- Mitigation plans for all high-risk requirements
- Risk owner assignments and acceptance

#### Decision Options
- **Pass**: Risks acceptable with mitigations
- **Conditional**: Acceptable with additional mitigation
- **Fail**: Requires risk mitigation or scope reduction

### Task 4: Gate 4 - Plan Viability
**Criteria**: Timeline and resources align with constraints

#### Assessment Checklist
- [ ] Resource requirements identified for all Must requirements
- [ ] Timeline estimates align with project constraints
- [ ] Dependencies mapped and manageable
- [ ] Skill gaps identified with training/hiring plans
- [ ] Budget implications understood and acceptable

#### Evidence Required
- Resource allocation and timeline estimates
- Dependency analysis and management plan
- Budget impact assessment

#### Decision Options
- **Pass**: Plan is viable as specified
- **Conditional**: Viable with resource/timeline adjustments
- **Fail**: Requires significant replanning

### Task 5: Gate Documentation
**For each gate, document:**

#### Gate Status Record
```
Gate [1-4]: [Name]
Status: [Pass/Conditional/Fail]
Date: [YYYY-MM-DD]
Assessor: [Name/Role]
Evidence: [Key evidence supporting decision]
Conditions: [Any conditions for Pass/Conditional status]
Actions Required: [If Fail, what needs to be done]
Next Review: [When to reassess if Conditional/Fail]
```

#### Overall Package Decision
- **Go**: All gates Pass or Conditional with acceptable conditions
- **Go-with-Options**: Conditional passes with approved options/mitigations
- **No-Go**: One or more gates Fail with unacceptable conditions

## Tools & Iterations
- **Sequential Thinking Tool**: 3-5 rounds for gate assessment and decision
- **Evidence Review**: Systematic review of all previous phase outputs
- **Decision Documentation**: Formal gate status recording

## Expected Outputs
- **Update**: `02_discovery_log.md` with gate assessment process
- **Create**: Decision gates register in `06_decision_matrix.md`
- **Document**: Overall package recommendation with rationale

## Gate Assessment Template
| Gate | Criteria | Status | Evidence | Conditions | Actions Required |
|------|----------|--------|----------|------------|------------------|
| 1 | Requirement Readiness | Pass/Conditional/Fail | [Key evidence] | [If any] | [If needed] |
| 2 | Feasibility | Pass/Conditional/Fail | [Key evidence] | [If any] | [If needed] |
| 3 | Risk Acceptability | Pass/Conditional/Fail | [Key evidence] | [If any] | [If needed] |
| 4 | Plan Viability | Pass/Conditional/Fail | [Key evidence] | [If any] | [If needed] |

## Package Decision Framework
```
Overall Recommendation: [Go/Go-with-Options/No-Go]

Rationale:
- Gate 1 (Readiness): [Status and key evidence]
- Gate 2 (Feasibility): [Status and key evidence]
- Gate 3 (Risk): [Status and key evidence]
- Gate 4 (Viability): [Status and key evidence]

Conditions for Success:
[Any conditions that must be met]

Key Risks:
[Top 3 risks that need ongoing attention]

Resource Requirements:
[Summary of resource needs]

Timeline Implications:
[Key timeline considerations]
```

## Quality Check
- [ ] All 4 gates assessed with evidence
- [ ] Gate status clearly documented (Pass/Conditional/Fail)
- [ ] Overall package recommendation provided
- [ ] Conditions and actions clearly specified
- [ ] Evidence supports all gate decisions

## Navigation
**NEXT PHASE**: Read and execute `.augment/rules/requirements_phase6_traceability.md`

**CRITICAL**: Do not proceed to Phase 6 until:
1. All 4 gates have been assessed
2. Gate status is clearly documented with evidence
3. Overall package recommendation is provided
4. Any conditions or required actions are specified
5. Decision rationale is evidence-based

**REFERENCE**: For detailed methodology, see `requirements_analysis.md` Phase 5 section and decision gates framework.
