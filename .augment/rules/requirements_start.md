---
type: "agent_requested"
description: "Starting point for modular requirements analysis. Provides overview and critical constraints before directing to Phase 0. Uses Volere + MoSCoW + PACT methodology through focused phase-specific sub-rules optimized for smaller models."
---

# Requirements Analysis - Starting Point

## Description
**STARTING POINT** for comprehensive requirements analysis using Volere + MoSCoW + PACT methodology. This rule provides overview and critical constraints, then directs you to begin the analysis process through 10 focused phases, each with dedicated sub-rules optimized for smaller model compatibility.

## 🚨 CRITICAL EVIDENCE REQUIREMENT WARNING 🚨
**ABSOLUTE REQUIREMENT: EVERY ASSERTION MUST BE BACKED BY REAL EVIDENCE**

- **NO IMAGINATION**: Do not infer missing details; identify and log gaps
- **NO LYING**: If a source is unavailable, say so and raise an action
- **NO ASSUMPTIONS**: Do not assume requirements without evidence
- **NO SPECULATION**: Do not guess about stakeholder needs or technical feasibility

## Objective
Transform ambiguous requests into **clear, testable requirements** with **priorities**, **fit criteria**, and **feasibility verdicts** (per PACT). Deliver a **decision-ready** package including risks, options, estimates, and a recommendation.

## Critical Bias Warning
**⚠️ MANDATORY BIAS CHECKS** throughout all phases:
- **Solution Bias**: Assuming solutions before understanding problems
- **Gold-Plating Bias**: Adding "nice-to-haves" without business justification
- **Happy-Path Bias**: Ignoring failure modes and operational costs
- **Tech Anchoring**: Forcing favorite tools irrespective of fit
- **Stakeholder Dominance**: One loud voice ≠ collective agreement
- **Scope Creep Bias**: Expanding beyond actual needs

## Analysis Process Overview

### Phase 0: Working Memory Initialization
**Purpose**: Establish persistent memory system and clarification protocol
**Sub-rule**: `requirements_phase0_memory.md`

### Phase 1: Requirement Capture & Classification
**Purpose**: Extract and normalize atomic requirements with evidence
**Sub-rule**: `requirements_phase1_capture.md`

### Phase 2: MoSCoW Prioritization
**Purpose**: Assign Must/Should/Could/Won't with business justification
**Sub-rule**: `requirements_phase2_prioritization.md`

### Phase 3: PACT Feasibility Assessment
**Purpose**: Evaluate People, Activities, Context, Technology feasibility
**Sub-rule**: `requirements_phase3_feasibility.md`

### Phase 4: Options Analysis
**Purpose**: Develop A/B/C alternatives for non-feasible requirements
**Sub-rule**: `requirements_phase4_options.md`

### Phase 5: Decision Gates
**Purpose**: Apply 4-gate framework for go/no-go decisions
**Sub-rule**: `requirements_phase5_gates.md`

### Phase 6: Traceability & Risk Mapping
**Purpose**: Build 5 traceability matrices and risk assessments
**Sub-rule**: `requirements_phase6_traceability.md`

### Phase 7: RAG Dashboard & Executive Communication
**Purpose**: Create Red/Amber/Green status and executive summary
**Sub-rule**: `requirements_phase7_rag.md`

### Phase 8: Acceptance Test Integration
**Purpose**: Link fit criteria to Given/When/Then acceptance tests
**Sub-rule**: `requirements_phase8_testing.md`

### Phase 9: Final Decision Matrix & Deliverables
**Purpose**: Complete decision matrix and comprehensive documentation package
**Sub-rule**: `requirements_phase9_final.md`

## Tool Requirements (MANDATORY)
- **Sequential Thinking Tool**: For complex analysis and branching
- **Shrimp Task Manager Tools**: For systematic investigation
- **MCP Feedback Tool**: For user communication (PROHIBITED not to call)
- **Working Memory Management**: Persistent .memories folder system
- **Evidence Collection Tools**: Codebase retrieval, web search

## Critical Constraints (APPLY TO ALL PHASES)
- **NO SOLUTION DESIGN**: Focus on requirements, not implementation
- **NO GOLD-PLATING**: Only justified requirements
- **NO ASSUMPTION-BASED CONCLUSIONS**: Evidence required for all claims
- **NO SINGLE-STAKEHOLDER DOMINANCE**: Validate across groups
- **NO HAPPY-PATH ONLY**: Consider failures and operational costs

## Quality Gates (MANDATORY THROUGHOUT)
- **Requirement Quality**: Atomic, unambiguous, testable
- **Evidence Integrity**: Quoted sources with stable anchors
- **Feasibility Coverage**: Must requirements feasible or have options
- **Risk Management**: High risks with concrete mitigations
- **Traceability**: Complete requirement mapping

## Expected Final Deliverables
1. **Working Memory Archive** (.memories folder with 6 files)
2. **Executive Summary** (one-page RAG dashboard)
3. **Requirements Catalog** (enhanced Volere templates)
4. **PACT Feasibility Workbook** (confidence scoring)
5. **Options Analysis** (A/B/C for non-feasible requirements)
6. **Decision Gates Register** (4 gates with approvers)
7. **Risk Analysis Matrix** (probability × impact with mitigations)
8. **Traceability Matrices** (5 types)
9. **RAG Dashboard** (Red/Amber/Green status)
10. **Acceptance Test Skeletons** (Given/When/Then)
11. **Decision Matrix** (final recommendations)
12. **Evidence Inventory** (source quotes and gaps)

## BEGIN ANALYSIS PROCESS
**NEXT STEP**: Read and execute `.augment/rules/requirements_phase0_memory.md` to start the analysis

**IMPORTANT NOTES:**
- Each phase will direct you to the next phase automatically
- Follow the navigation instructions exactly - do NOT skip phases
- Each phase builds on the previous phase's work stored in `.memories` folder
- The comprehensive reference methodology is in `requirements_analysis.md`

**PROCESS FLOW:**
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8 → Phase 9 → Complete

**FINAL DELIVERABLE**: Phase 9 will deliver complete analysis report to user via MCP Feedback tool

**NOW GO TO PHASE 0**: Read and execute `.augment/rules/requirements_phase0_memory.md`
