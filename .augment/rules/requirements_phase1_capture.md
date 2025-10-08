---
type: "manual"
description: "Phase 1: Requirement Capture & Classification. Extracts and normalizes atomic requirements using Volere methodology with evidence-based documentation."
---

# Phase 1: Requirement Capture & Classification

## Objective
Extract and normalize atomic requirements from user input using Volere methodology. Convert all requirement candidates into structured, testable statements with evidence backing.

## 🚨 CRITICAL CONSTRAINTS (ALWAYS REMEMBER)
- **NO LYING**: If evidence unavailable, say so and raise action
- **NO ASSUMPTIONS**: Every assertion needs real evidence
- **NO SPECULATION**: Do not guess about needs or feasibility
- **ATOMIC REQUIREMENTS ONLY**: Single purpose, single outcome, ≤25 words

## Context Refresh
**MANDATORY**: Read these memory files before proceeding:
- `.memories/[current-analysis]/01_initial_understanding.md`
- `.memories/[current-analysis]/02_discovery_log.md`
- `.memories/[current-analysis]/03_clarification_requests.md`

## Phase 1 Tasks

### Task 0: Cognitive Bias Checklist (Run BEFORE Analysis)
**MANDATORY**: Check for these biases before starting requirement extraction:
- [ ] **Solution Bias**: Am I assuming a solution before understanding the problem?
- [ ] **Scope Creep Bias**: Am I expanding requirements beyond actual needs?
- [ ] **Technical Bias**: Am I favoring technically interesting over business-valuable requirements?
- [ ] **Confirmation Bias**: Am I looking for requirements that support my preferred approach?
- [ ] **Anchoring Bias**: Am I over-weighting the first requirements received?
- [ ] **Availability Bias**: Am I favoring easily recalled similar projects?
- [ ] **Clarity Bias**: Am I assuming I understand when requirements are actually ambiguous?

### Task 1: Extract Requirement Candidates
1. **Parse User Input**: Extract all potential requirements from clarified user input
2. **Include Sources**: Note where each requirement originated (user statement, clarification, etc.)
3. **Capture Everything**: Don't filter yet - capture all potential requirements

### Task 2: Apply Atomic Requirements Framework
**For each requirement candidate, ensure:**
- **Single Purpose**: Addresses exactly one concern
- **Single Outcome**: Has exactly one measurable result
- **≤25 Words**: Main description is concise and clear
- **Testable**: Can be measured or verified
- **Unambiguous**: No "or/and" without quantifiers

**Deterministic Parsing Rules:**
- If requirement contains multiple concerns → Split into separate atomic requirements
- If fit criterion lacks measurable unit + threshold → Flag as evidence gap
- If source lacks stable locator → Require specific anchor before proceeding
- If description >25 words → Simplify or split into multiple requirements
- If requirement contains "or/and" without quantifiers → Split into separate requirements

**If requirement violates rules:**
- **Split**: Separate into multiple atomic requirements
- **Clarify**: Remove ambiguous language
- **Simplify**: Reduce to core essence
- **Flag**: Mark evidence gaps for clarification

### Task 3: Classify Requirements (Volere Standard)
**Assign each requirement to one category:**
- **Functional**: What the system must do (behaviors, operations, functions)
- **Non-Functional**: How the system must perform (performance, usability, reliability)
- **Constraints**: Fixed conditions that limit design choices (standards, hardware, deadlines)

### Task 4: Complete Enhanced Volere Templates
**For each atomic requirement, populate:**

```
Requirement ID: REQ-[F/N/C]-[001]
Type: [Functional/Non-Functional/Constraint]
Description: [≤25 words, single purpose, single outcome]
Rationale: [Business reason/benefit with stakeholder owner]
Source: [User statement/clarification with reference]
Fit Criterion: [Measurable acceptance with unit + threshold]
Priority: [To be assigned in Phase 2]
Dependencies: [Other requirements this depends on]
Conflicts: [Requirements this conflicts with]
Assumptions: [If any, with validation plan]
Open Questions: [Clarifications needed with owner/due date]
Evidence: [Verbatim quote: "source shows 'exact text'"]
```

### Task 5: Quality Validation
**For each requirement, verify:**
- [ ] Atomic (single purpose, single outcome)
- [ ] ≤25 words description
- [ ] Testable fit criterion with measurable unit
- [ ] Evidence quote from source
- [ ] Proper classification (F/N/C)
- [ ] No ambiguous language

## Tools & Iterations

### Sequential Thinking Analysis (15+ Rounds with Dynamic Branching)
**CRITICAL**: Branch thinking immediately when multiple requirement domains emerge.

**Dynamic Branching Triggers**:
- Multiple stakeholder groups identified → Branch to investigate each group's needs
- Technical constraints discovered → Branch to assess feasibility implications
- Conflicting requirements found → Branch to resolve conflicts
- New requirement domains emerge → Branch to explore thoroughly
- **Ambiguity detected** → Branch to explore all possible interpretations
- **User clarification received** → Branch to reassess previous assumptions
- **Context changes** → Branch to evaluate impact on existing requirements

**Round Structure for Phase 1 (Minimum 5-7, extend as needed)**:
- **Rounds 1-2**: Requirement extraction from clarified user input
- **Rounds 3-4**: Atomic requirements framework application
- **Rounds 5-6**: Volere template completion and quality validation
- **Rounds 7+**: Continue until all requirements are atomic and complete

**Each Round Must Update Working Memory**:
- Update `02_discovery_log.md` with new findings
- Cross-reference with `01_initial_understanding.md` for deviations
- Document any new clarification needs in `03_clarification_requests.md`
- Track branching decisions and their outcomes

### Other Tools
- **Evidence Collection**: Quote exact user statements and clarifications
- **Quality Validation**: Apply atomic requirements framework rigorously

## Expected Outputs
- **Update**: `02_discovery_log.md` with requirement extraction process
- **Create**: Initial requirements catalog in `05_requirements_catalog.md`
- **Document**: All atomic requirements with complete Volere templates

## Requirement Row Template (Copy-Paste)
| REQ-ID | Type | Description | Rationale | Source | Fit Criterion | Dependencies | Evidence Quote |
|--------|------|-------------|-----------|--------|---------------|--------------|----------------|
| REQ-F-001 | Functional | [≤25 words] | [Business benefit] | [User statement] | [Measurable with unit] | [REQ-IDs] | "User said 'exact text'" |

## Quality Check Examples

### ✅ Good Atomic Requirement
```
REQ-F-001: System shall respond to user queries within 200ms
- Single purpose: Response time
- Single outcome: ≤200ms response
- Testable: Can measure response time
- ≤25 words: 9 words
```

### ❌ Bad Non-Atomic Requirement
```
"System should be fast and user-friendly with good performance"
- Multiple purposes: Speed + UX + Performance
- No measurable outcome
- Ambiguous language
- Needs splitting into 3+ atomic requirements
```

## Deterministic Parsing Rules
- **Multiple Concerns**: Split into separate requirements
- **No Fit Criterion**: Flag as evidence gap requiring clarification
- **Ambiguous Language**: Clarify with user via MCP Feedback
- **>25 Words**: Simplify or split

## Navigation
**NEXT PHASE**: Read and execute `.augment/rules/requirements_phase2_prioritization.md`

**CRITICAL**: Do not proceed to Phase 2 until:
1. All requirements are atomic (single purpose, single outcome)
2. All requirements have complete Volere templates
3. All requirements have evidence quotes from sources
4. Requirements catalog is populated in `05_requirements_catalog.md`

**REFERENCE**: For detailed methodology, see `requirements_analysis.md` Phase 1 section and atomic requirements framework.
