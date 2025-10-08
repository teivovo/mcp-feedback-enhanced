---
type: "manual"
description: "Phase 3: PACT Feasibility Assessment. Evaluates People, Activities, Context, Technology feasibility for all requirements with confidence scoring and evidence."
---

# Phase 3: PACT Feasibility Assessment

## Objective
Evaluate feasibility of all requirements across four PACT dimensions (People, Activities, Context, Technology) with confidence scoring and evidence-based assessment.

## 🚨 CRITICAL CONSTRAINTS (ALWAYS REMEMBER)
- **NO LYING**: If evidence unavailable, say so and raise action
- **NO ASSUMPTIONS**: Every feasibility verdict needs real evidence
- **NO SPECULATION**: Do not guess about capabilities or constraints
- **NO HAPPY-PATH BIAS**: Consider failure modes and operational costs

## Context Refresh
**MANDATORY**: Read these memory files before proceeding:
- `.memories/[current-analysis]/02_discovery_log.md`
- `.memories/[current-analysis]/05_requirements_catalog.md`

## Phase 3 Tasks

### Task 1: PACT Framework Application
**For each requirement, assess feasibility across four dimensions:**

#### People Feasibility
- **Skills Available**: Do we have required expertise?
- **Capacity Available**: Do we have sufficient human resources?
- **Roles Defined**: Are responsibilities clear and assigned?
- **Training Needs**: What skill gaps need addressing?
- **Evidence Sources**: Team skill matrix, resource allocation, training records

#### Activities Feasibility
- **Workflow Support**: Do current processes support this requirement?
- **Integration Points**: How does this fit with existing activities?
- **Process Changes**: What workflow modifications are needed?
- **Timeline Compatibility**: Does this fit within project schedule?
- **Evidence Sources**: Process documentation, workflow analysis, project timeline

#### Context Feasibility
- **Environmental Constraints**: Does operating environment permit this?
- **Regulatory Compliance**: Are there legal/regulatory barriers?
- **Organizational Culture**: Does this align with organizational values?
- **Market Conditions**: Do external factors support this requirement?
- **Evidence Sources**: Environmental analysis, compliance documentation, market research

#### Technology Feasibility
- **Technical Capability**: Can current technology stack support this?
- **Performance Requirements**: Can system meet performance criteria?
- **Integration Compatibility**: Does this work with existing systems?
- **Scalability**: Can this scale to required levels?
- **Evidence Sources**: Technical documentation, performance benchmarks, architecture analysis

### Task 2: PACT Scoring with Confidence
**For each requirement and PACT dimension, assign:**

#### Feasibility Score (Numerical + Letter)
- **Feasible (3, Y)**: Strong evidence supports feasibility
- **Partially Feasible (2, P)**: Some constraints but manageable with effort
- **Not Feasible (1, N)**: Significant barriers, requires major changes
- **Unknown (0, U)**: Insufficient evidence to determine feasibility

#### Confidence Score (1-5 Scale)
- **5**: Multiple primary evidences; constraints satisfied
- **4**: Strong evidence; minor gaps
- **3**: Mixed; needs one clarification or PoC
- **2**: Major unknown(s); PoC required
- **1**: Not feasible without re-scope

#### Overall PACT Verdict Calculation
- **Average Score**: Sum of all 4 PACT dimensions ÷ 4
- **Overall Verdict**:
  - **Feasible**: Average ≥ 2.5 with no dimension = 0
  - **Partial**: Average 1.5-2.4 or any dimension = 0 but others ≥ 2
  - **Not Feasible**: Average < 1.5 or multiple dimensions = 1

### Task 3: Evidence Collection per Dimension
**For each PACT assessment:**
1. **Collect Specific Evidence**: Use codebase retrieval, web search, documentation
2. **Quote Sources**: Provide verbatim evidence with references
3. **Identify Gaps**: Flag missing evidence with owner and due date
4. **Document Assumptions**: Mark any assumptions requiring validation

### Task 4: Risk Identification
**For each requirement, identify risks:**
- **Technical Risks**: Implementation complexity, technology maturity
- **Resource Risks**: Skill availability, capacity constraints
- **Schedule Risks**: Timeline dependencies, critical path impacts
- **Business Risks**: Market changes, stakeholder alignment
- **Integration Risks**: System compatibility, data migration

### Task 5: Create PACT Feasibility Workbook
**Document in structured format:**

## Tools & Iterations
- **Sequential Thinking Tool**: 7-10 rounds for comprehensive PACT analysis
- **Evidence Collection Tools**: Codebase retrieval, web search, documentation review
- **Risk Assessment**: Systematic risk identification and scoring

## Expected Outputs
- **Update**: `02_discovery_log.md` with PACT assessment process
- **Create**: PACT feasibility workbook section in `05_requirements_catalog.md`
- **Document**: Evidence inventory with sources and confidence scores

## PACT Verdict Template (Copy-Paste)
| REQ-ID | People (Y/P/N, Conf 1-5) | Activities (Y/P/N, Conf 1-5) | Context (Y/P/N, Conf 1-5) | Technology (Y/P/N, Conf 1-5) | Overall Verdict | Key Risks | Mitigations |
|--------|---------------------------|-------------------------------|----------------------------|------------------------------|-----------------|-----------|-------------|
| REQ-F-001 | Y, 4 | P, 3 | Y, 5 | P, 2 | Partial | [Top 3 risks] | [Specific actions] |

## Evidence Documentation Template
```
REQ-ID: [ID]
PACT Dimension: [People/Activities/Context/Technology]
Verdict: [Y/P/N] (Confidence: [1-5])
Evidence: [Source] shows "[verbatim quote]" (link/ref)
Gaps: [Missing evidence] - requires [specific artifact]; owner: [name]; due: [date]
Risks: [Identified risks with likelihood and impact]
Mitigations: [Specific actions to address risks]
```

## Feasibility Confidence Examples
**Technology Feasibility Example:**
```
REQ-F-012: API Response Time ≤150ms
Technology Verdict: Partial (Confidence: 3)
Evidence: Load tests from 2025-08-30 show 210ms P95 under 3× load
Gap: Need current system capacity analysis
Risk: Performance degradation under load
Mitigation: Add read cache, optimize queries
```

## Quality Check
- [ ] All requirements have PACT assessment completed
- [ ] All verdicts have confidence scores with evidence
- [ ] Missing evidence flagged with owner and due date
- [ ] Key risks identified for each requirement
- [ ] Mitigation strategies documented for high risks
- [ ] Overall feasibility verdict assigned

## Common PACT Assessment Mistakes
- **Optimistic Bias**: Assuming best-case scenarios without evidence
- **Single Evidence Source**: Need multiple sources for high confidence
- **Ignoring Constraints**: Consider real-world limitations and dependencies
- **Missing Integration Costs**: Account for system integration complexity
- **Underestimating Operational Impact**: Consider ongoing maintenance and support

## Navigation
**NEXT PHASE**: Read and execute `.augment/rules/requirements_phase4_options.md`

**CRITICAL**: Do not proceed to Phase 4 until:
1. All requirements have complete PACT assessment
2. All verdicts have confidence scores and evidence
3. Missing evidence is flagged with owners and due dates
4. Key risks are identified and documented
5. Requirements with Partial/No feasibility are clearly marked

**REFERENCE**: For detailed methodology, see `requirements_analysis.md` Phase 3 section and PACT framework.
