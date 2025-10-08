---
type: "manual"
description: "Phase 8: Acceptance Test Integration. Links fit criteria to Given/When/Then acceptance tests ensuring all Must requirements are testable."
---

# Phase 8: Acceptance Test Integration

## Objective
Link fit criteria directly to Given/When/Then acceptance tests ensuring all Must requirements have clear, executable test criteria.

## 🚨 CRITICAL CONSTRAINTS (ALWAYS REMEMBER)
- **NO LYING**: If evidence unavailable, say so and raise action
- **NO ASSUMPTIONS**: Every test must be based on fit criteria
- **NO SPECULATION**: Do not guess about test methods or success criteria
- **TESTABILITY FOCUS**: All tests must be executable and measurable

## Context Refresh
**MANDATORY**: Read these memory files before proceeding:
- `.memories/[current-analysis]/05_requirements_catalog.md`
- `.memories/[current-analysis]/06_decision_matrix.md`
- Review fit criteria from all requirements

## Phase 8 Tasks

### Task 1: Testability Validation
**For each requirement, verify:**
- **Fit Criterion Check**: Contains measurable unit + threshold
- **Test Feasibility**: Can be automated or manually executed
- **Success Criteria**: Clear pass/fail determination possible
- **Evidence Chain**: Requirement → Fit Criterion → Test → Result

### Task 2: Acceptance Test Skeleton Framework
**Create Given/When/Then tests for all Must requirements:**

#### Test Template Structure
```
REQ-ID: [ID] — [Title]
Fit Criterion: [Measurable criterion with unit + threshold]
Acceptance Test:
  Given [Preconditions and test setup]
  When [Action or trigger event]
  Then [Expected measurable outcome matching fit criterion]
```

#### Test Categories
- **Functional Tests**: Verify system behaviors and operations
- **Performance Tests**: Validate non-functional requirements (speed, capacity)
- **Compliance Tests**: Ensure regulatory and constraint adherence
- **Integration Tests**: Verify system interactions and dependencies

### Task 3: Create Test Skeletons for All Must Requirements

#### Functional Test Example
```
REQ-ID: REQ-F-012 — User Authentication
Fit Criterion: User login completes within 3 seconds with valid credentials
Acceptance Test:
  Given a registered user with valid username and password
  When the user submits login credentials
  Then authentication completes within 3 seconds and user is logged in
```

#### Performance Test Example
```
REQ-ID: REQ-N-015 — API Response Time
Fit Criterion: P95 ≤ 150ms under 3× baseline traffic for 10 minutes
Acceptance Test:
  Given a 3× synthetic load (RPS N) on /v2/query endpoint
  When traffic runs continuously for 10 minutes
  Then measured P95 latency ≤ 150ms and error rate < 0.1%
```

#### Compliance Test Example
```
REQ-ID: REQ-C-021 — Data Residency
Fit Criterion: All PII stored in Singapore region only
Acceptance Test:
  Given a dataset containing PII fields
  When writing records via the data layer
  Then data files and backups are located in SG region buckets only
```

### Task 4: Test Coverage Analysis
**Ensure comprehensive coverage:**

#### Coverage Matrix
| REQ-ID | Type | Fit Criterion | Test Method | Automation Level | Dependencies |
|--------|------|---------------|-------------|------------------|--------------|
| REQ-F-001 | Functional | [Criterion] | [Method] | [Auto/Manual/Semi] | [Test deps] |

#### Coverage Validation
- [ ] All Must requirements have acceptance tests
- [ ] All fit criteria are testable
- [ ] Test methods are feasible and executable
- [ ] Dependencies between tests are identified
- [ ] Automation level is specified

### Task 5: Test Implementation Guidance
**For each test, provide:**

#### Test Environment Requirements
- Infrastructure needed for test execution
- Data requirements and test datasets
- Tool and framework dependencies

#### Test Execution Steps
- Detailed steps for manual tests
- Automation framework requirements
- Expected outputs and measurements

#### Success/Failure Criteria
- Clear pass/fail determination
- Acceptable variance ranges
- Error handling and edge cases

## Tools & Iterations
- **Sequential Thinking Tool**: 3-5 rounds for test design and validation
- **Evidence Review**: Ensure tests align with fit criteria
- **Coverage Analysis**: Systematic review of test coverage

## Expected Outputs
- **Create**: Acceptance test skeletons section in `05_requirements_catalog.md`
- **Update**: `02_discovery_log.md` with testing analysis
- **Document**: Test coverage matrix and implementation guidance

## Test Documentation Template
```
# Acceptance Test Skeletons - [Analysis Name]

## Test Coverage Summary
- Total Must Requirements: [X]
- Requirements with Tests: [Y]
- Coverage Percentage: [Z]%

## Test Categories
- Functional Tests: [X]
- Performance Tests: [Y]
- Compliance Tests: [Z]
- Integration Tests: [W]

## Test Skeletons

### REQ-[ID]: [Title]
**Type**: [Functional/Performance/Compliance/Integration]
**Fit Criterion**: [Measurable criterion]
**Test Method**: [Automated/Manual/Semi-automated]

**Acceptance Test**:
```
Given [preconditions]
When [action]
Then [expected outcome]
```

**Environment Requirements**: [Infrastructure/data/tools needed]
**Dependencies**: [Other tests or requirements]
**Implementation Notes**: [Specific guidance]
```

## Quality Check
- [ ] All Must requirements have acceptance test skeletons
- [ ] All tests link directly to fit criteria
- [ ] Given/When/Then format used consistently
- [ ] Test methods are feasible and executable
- [ ] Environment requirements specified
- [ ] Test dependencies identified
- [ ] Coverage analysis completed

## Common Testing Mistakes to Avoid
- **Vague Success Criteria**: Tests must have clear pass/fail determination
- **Untestable Fit Criteria**: All criteria must be measurable
- **Missing Environment Specs**: Specify infrastructure and data needs
- **Ignoring Dependencies**: Map test execution dependencies
- **No Automation Plan**: Specify automation level and approach

## Navigation
**NEXT PHASE**: Read and execute `.augment/rules/requirements_phase9_final.md`

**CRITICAL**: Do not proceed to Phase 9 until:
1. All Must requirements have acceptance test skeletons
2. All tests link directly to fit criteria
3. Test coverage analysis is complete
4. Environment requirements are specified
5. Test implementation guidance is provided

**REFERENCE**: For detailed methodology, see `requirements_analysis.md` Phase 8 section.
