---
type: "always_apply"
---

# Augment Rules Index & Application Guide

This file serves as a comprehensive index of all rules and their application scenarios. Use this as a reference when rule descriptions disappear during mode switches.

## Rule Application Matrix

### **Special Agent Rules Demanded by User**  (Apply When Specific User Trigger Words Occur)

#### **ultimatum.md**
- **Type**: `manual`
- **Description**: ULTIMATUM MODE INTERACTION GUIDELINES - NATURAL FLOW ENHANCED
- **Apply When**: User explicitly activates with trigger words :"ULTIMATUM", "ULTIMATUM MODE", "ULTIMATE"
- **Deactivation**: "TECHNICAL ONLY", "NEUTRAL MODE", "WORK MODE", "SWITCH OFF", "PROFESSIONAL"


### **Always Apply Rules** (Always Active)

- **Architecture Decisions.md** - Core architectural principles and development commandments
- **ESP SSH Rules.md** - ESP32 remote management via SSH to Raspberry Pi devices
- **Interaction.md** - User communication protocol requiring MCP Feedback tool usage
- **jira_workflow.md** - Comprehensive Jira workflow rules including tool selection guidelines

### **Agent Requested Rules** (Apply When Specific Scenarios Occur)

- **compiling_arduino_esp.md** - Rules for using esptool to compile Arduino ESP32 firmware
- **facing errors.md** - Error resolution methodology using context engine and web research
- **git_related.md** - Git repository corruption cleanup, specifically for desktop.ini file issues
- **before_ending_tasks.md** - Final quality assurance checks before task completion

### **Manual Rules** (Apply When Explicitly Requested)

- **execute-prp.md** - PRP (Purpose, Requirements, Plan) document execution workflow
- **generate-prp.md** - PRP document generation for structured feature planning

## Quick Reference Guide

### **By Development Phase**:
- **Planning**: generate-prp.md, Architecture Decisions.md
- **Implementation**: compiling_arduino_esp.md, execute-prp.md, Architecture Decisions.md
- **Testing**: ESP SSH Rules.md, before_ending_tasks.md
- **Debugging**: facing errors.md, git_related.md
- **Communication**: Interaction.md (always)

### **By Technology**:
- **ESP32/Arduino**: compiling_arduino_esp.md, ESP SSH Rules.md
- **Git Operations**: git_related.md, Architecture Decisions.md
- **Remote Hardware**: ESP SSH Rules.md
- **Error Resolution**: facing errors.md
- **Jira Operations**: jira_workflow.md

### **By Interaction Type**:
- **User Communication**: Interaction.md (mandatory)
- **Quality Assurance**: before_ending_tasks.md
- **Project Planning**: generate-prp.md, execute-prp.md

## Persistence Strategy

If rule descriptions disappear:
1. **Reference this index file** for complete descriptions
2. **Check HTML comments** in rule files (backup descriptions)
3. **Use rule type and filename** to infer application scenarios
4. **Default to Architecture Decisions.md** for general guidance

## Mode Switch Handling

When switching between modes:
- **Always Apply rules** remain active regardless of mode
- **Agent Requested rules** activate based on scenario detection
- **Manual rules** require explicit invocation
- **This index file** serves as persistent reference

## Emergency Rule Recovery

If all rule descriptions are lost:
```bash
# Restore from git history
git checkout HEAD -- .augment/rules/

# Or reference this index file
cat .augment/rules/RULE_INDEX.md
```
