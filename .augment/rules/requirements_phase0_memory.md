---
type: "manual"
description: "Phase 0: Working Memory Initialization for requirements analysis. Establishes persistent memory system and iterative clarification protocol for handling unstructured user requirements."
---

# Phase 0: Working Memory Initialization

## Objective
Establish persistent working memory system in `.memories` folder and implement iterative clarification protocol to handle unstructured, ambiguous user requirements effectively.

## 🚨 CRITICAL CONSTRAINTS (ALWAYS REMEMBER)
- **NO LYING**: If evidence unavailable, say so and raise action
- **NO ASSUMPTIONS**: Every assertion needs real evidence
- **NO SPECULATION**: Do not guess about needs or feasibility
- **NO IMAGINATION**: Do not infer missing details; identify and log gaps

## Context Refresh
**FIRST TIME SETUP**: No previous context to refresh - this is the initialization phase.

## Phase 0 Tasks

### Task 1: Memory Index Management
1. **Check/Create**: `.memories/index.md` exists and is accessible
2. **Add Entry**: Create new analysis entry with format:
   ```
   [YYYY-MM-DD-HHMMSS] - [analysis-name] - ACTIVE - [Brief Description]
   Folder: ./.memories/[YYYY-MM-DD-HHMMSS]-[analysis-name]/
   Purpose: [What this analysis is for]
   Stakeholders: [Who is involved]
   ```

### Task 2: Analysis Run Folder Creation
1. **Create Folder**: `.memories/[YYYY-MM-DD-HHMMSS]-[analysis-name]/`
2. **Create 6 Required Files**:
   - `01_initial_understanding.md` - First interpretation of user requirements
   - `02_discovery_log.md` - Ongoing discoveries, clarifications, amendments
   - `03_clarification_requests.md` - All questions asked to user with responses
   - `04_final_comparison.md` - Deviation analysis and over-engineering check
   - `05_requirements_catalog.md` - Final structured requirements
   - `06_decision_matrix.md` - Final feasibility and priority decisions

### Task 3: Initial Understanding Documentation
1. **Document First Interpretation**: Write user's requirements as you understand them in `01_initial_understanding.md`
2. **Include**:
   - What the user seems to want
   - Key stakeholders mentioned
   - Apparent scope and constraints
   - Initial assumptions (mark clearly as assumptions)
   - Obvious ambiguities or gaps

### Task 4: Ambiguity Identification
1. **Identify Unclear Elements**: List all ambiguous, conflicting, or missing elements
2. **Generate Clarification Questions**: Use framework:
   - **Scope Boundaries**: "What is explicitly IN scope vs OUT of scope?"
   - **Success Criteria**: "How will you know this requirement is successfully met?"
   - **Priority Rationale**: "Why is this requirement important to the business/user?"
   - **Constraint Validation**: "What limitations or constraints must we work within?"
   - **Stakeholder Confirmation**: "Who else needs to approve or validate this requirement?"
   - **Use Case Scenarios**: "Can you walk me through how this would actually be used?"

### Task 5: User Clarification (If Needed)
**IF requirements are unclear or ambiguous:**
1. **Document Questions**: Record all clarification questions in `03_clarification_requests.md`
2. **Use MCP Feedback Tool**: Ask user for clarifications with specific, targeted questions
3. **Update Discovery Log**: Record user responses in `02_discovery_log.md`
4. **Iterate**: Repeat until requirements are sufficiently clear

## Tools & Iterations
- **Sequential Thinking Tool**: 3-5 rounds for initial understanding and ambiguity identification
- **MCP Feedback Tool**: For user clarification (MANDATORY if ambiguities exist)
- **File Management**: Create and populate all 6 memory files

## Expected Outputs
- **Update**: `.memories/index.md` with new analysis entry
- **Create**: Analysis folder with 6 required files
- **Document**: Initial understanding with ambiguities identified
- **Clarify**: User requirements if ambiguous (via MCP Feedback)

## Working Memory File Templates

### 01_initial_understanding.md Template
```markdown
# Initial Understanding - [Analysis Name]
Date: [YYYY-MM-DD]

## User Request Summary
[What the user asked for in their own words]

## My Initial Interpretation
[How I understand the request]

## Apparent Stakeholders
[Who seems to be involved]

## Apparent Scope
[What seems to be included/excluded]

## Initial Assumptions (TO BE VALIDATED)
[What I'm assuming - mark clearly]

## Identified Ambiguities
[What needs clarification]

## Next Steps
[What clarification is needed]
```

### 02_discovery_log.md Template
```markdown
# Discovery Log - [Analysis Name]
Date: [YYYY-MM-DD]

## Discovery Timeline
[Chronological log of discoveries and clarifications]

### [Timestamp] - Initial Analysis
[First findings]

### [Timestamp] - User Clarification
[User responses to questions]

### [Timestamp] - Updated Understanding
[How understanding evolved]
```

## Quality Check
- [ ] Memory index updated with new entry
- [ ] Analysis folder created with all 6 files
- [ ] Initial understanding documented with evidence
- [ ] Ambiguities identified and clarification questions prepared
- [ ] User clarification obtained if needed (via MCP Feedback)

## Navigation
**NEXT PHASE**: Read and execute `.augment/rules/requirements_phase1_capture.md`

**CRITICAL**: Do not proceed to Phase 1 until:
1. All 6 memory files are created and populated
2. User requirements are sufficiently clear (no major ambiguities)
3. Initial understanding is documented with evidence

**REFERENCE**: For detailed methodology, see `requirements_analysis.md` Phase 0 section.
