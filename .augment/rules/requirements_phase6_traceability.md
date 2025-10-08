---
type: "manual"
description: "Phase 6: Traceability & Risk Mapping. Builds 5 mandatory traceability matrices and comprehensive risk register with mitigation strategies."
---

# Phase 6: Traceability & Risk Mapping

## Objective
Build 5 mandatory traceability matrices and comprehensive risk register to ensure complete audit trail from requirements to implementation decisions.

## 🚨 CRITICAL CONSTRAINTS (ALWAYS REMEMBER)
- **NO LYING**: If evidence unavailable, say so and raise action
- **NO ASSUMPTIONS**: Every traceability link needs real evidence
- **NO SPECULATION**: Do not guess about dependencies or risks
- **COMPLETE COVERAGE**: All requirements must be traced

## Context Refresh
**MANDATORY**: Read these memory files before proceeding:
- `.memories/[current-analysis]/02_discovery_log.md`
- `.memories/[current-analysis]/05_requirements_catalog.md`
- `.memories/[current-analysis]/06_decision_matrix.md`

## Phase 6 Tasks

### Task 1: Build Five Traceability Matrices

#### Matrix 1: Req ↔ Source Evidence
**Purpose**: Link every requirement to source quote
**Format**: | REQ-ID | Source Document | Section/Line | Verbatim Quote | Evidence Type |

#### Matrix 2: Req ↔ Fit Criterion ↔ Acceptance Test
**Purpose**: Ensure testability chain
**Format**: | REQ-ID | Fit Criterion | Test Method | Given/When/Then | Success Criteria |

#### Matrix 3: Req ↔ Dependencies
**Purpose**: Map upstream and downstream relationships
**Format**: | REQ-ID | Depends On | Dependency Type | Impact if Missing | Circular Dependencies |

#### Matrix 4: Req ↔ Risks/Mitigations
**Purpose**: Risk coverage analysis
**Format**: | REQ-ID | Risk Description | Probability | Impact | Score | Mitigation | Owner |

#### Matrix 5: Req ↔ PACT Verdicts ↔ Options
**Purpose**: Feasibility decision trail
**Format**: | REQ-ID | PACT Verdict | Confidence | Option Selected | Rationale | Conditions |

### Task 2: Enhanced Risk Assessment
**For each requirement, document:**

#### Risk Categories
- **Technical Risks**: Implementation complexity, technology maturity
- **Resource Risks**: Skill availability, capacity constraints
- **Schedule Risks**: Timeline dependencies, critical path impacts
- **Business Risks**: Market changes, stakeholder alignment
- **Integration Risks**: System compatibility, data migration

#### Risk Scoring (Enhanced Formula)
- **Probability (1-5)**: How likely is this risk to occur?
  - 1: Very unlikely (0-10% chance)
  - 2: Unlikely (10-30% chance)
  - 3: Possible (30-50% chance)
  - 4: Likely (50-80% chance)
  - 5: Very likely (80-100% chance)
- **Impact (1-5)**: How severe would the consequences be?
  - 1: Minimal impact (minor delay/cost)
  - 2: Low impact (manageable delay/cost)
  - 3: Medium impact (significant delay/cost)
  - 4: High impact (major delay/cost)
  - 5: Critical impact (project failure/compliance breach)
- **Risk Score**: Probability × Impact (1-25 scale)

#### Severity Classification
- **High (16-25)**: Blocks delivery or breaches compliance
- **Medium (6-15)**: Material delay/cost; mitigatable
- **Low (1-5)**: Minor impact; routine mitigation

### Task 3: Dependency Analysis
**Map requirement relationships:**

#### Forward Dependencies
- What other requirements depend on this one?
- What happens if this requirement is delayed/removed?
- What is the critical path through dependencies?

#### Backward Dependencies
- What does this requirement depend on?
- Are all dependencies identified and feasible?
- Are there any circular dependencies?

#### External Dependencies
- Dependencies on external systems/teams
- Dependencies on third-party vendors
- Dependencies on regulatory approvals

### Task 4: Create Comprehensive Documentation

## Tools & Iterations
- **Sequential Thinking Tool**: 5-7 rounds for matrix building and dependency analysis
- **Evidence Collection**: Systematic review of all previous outputs
- **Risk Assessment**: Comprehensive risk identification and scoring

## Expected Outputs
- **Create**: All 5 traceability matrices in `06_decision_matrix.md`
- **Update**: `02_discovery_log.md` with traceability analysis
- **Document**: Comprehensive risk register with mitigations

## Traceability Matrix Templates

### Matrix 1: Source Evidence
| REQ-ID | Source Document | Section/Line | Verbatim Quote | Evidence Type |
|--------|-----------------|--------------|----------------|---------------|
| REQ-F-001 | User Interview | Line 23 | "System must respond in under 200ms" | Primary |

### Matrix 2: Testability Chain
| REQ-ID | Fit Criterion | Test Method | Given/When/Then | Success Criteria |
|--------|---------------|-------------|-----------------|------------------|
| REQ-F-001 | P95 ≤ 200ms | Load Test | Given 3x load/When 10min/Then P95 ≤ 200ms | Pass if P95 ≤ 200ms |

### Matrix 3: Dependencies
| REQ-ID | Depends On | Dependency Type | Impact if Missing | Circular Dependencies |
|--------|------------|-----------------|-------------------|----------------------|
| REQ-F-001 | REQ-F-002 | Technical | Cannot implement | None |

### Matrix 4: Risk Coverage
| REQ-ID | Risk Description | Probability | Impact | Score | Mitigation | Owner |
|--------|------------------|-------------|--------|-------|------------|-------|
| REQ-F-001 | Performance degradation | 3 | 4 | 12 | Add caching | Tech Lead |

### Matrix 5: Feasibility Trail
| REQ-ID | PACT Verdict | Confidence | Option Selected | Rationale | Conditions |
|--------|--------------|------------|-----------------|-----------|------------|
| REQ-F-001 | Partial | 3 | Option A | Minimal change approach | Cache implementation |

## Quality Check
- [ ] All 5 traceability matrices completed
- [ ] All requirements traced to sources with quotes
- [ ] All requirements have testability chain defined
- [ ] All dependencies mapped (forward and backward)
- [ ] All risks identified with mitigation strategies
- [ ] All feasibility decisions documented with rationale

## Navigation
**NEXT PHASE**: Read and execute `.augment/rules/requirements_phase7_rag.md`

**CRITICAL**: Do not proceed to Phase 7 until:
1. All 5 traceability matrices are complete
2. All requirements have complete traceability
3. Risk register is comprehensive with mitigations
4. Dependencies are fully mapped
5. No gaps in traceability coverage

**REFERENCE**: For detailed methodology, see `requirements_analysis.md` Phase 6 section.
