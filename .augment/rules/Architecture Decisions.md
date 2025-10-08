---
type: "always_apply"
description: "Core architectural principles and development commandments for all coding decisions, git workflows, and project structure choices. Apply when making any significant code changes, architectural decisions, or when establishing development patterns."
---

<!-- RULE DESCRIPTION: Core architectural principles and development commandments for all coding decisions, git workflows, and project structure choices. Apply when making any significant code changes, architectural decisions, or when establishing development patterns. -->

###Architecture decisions (consider implications)###

##Use Git Tools:##
- Before modifying files (understand history and context)
- When tests fail (check recent changes)
- Finding related code (git grep)
- Understanding features (follow evolution)
- Checking workflows (CI/CD issues)

##The Ten Universal Commandments##
1. Thou shalt ALWAYS use MCP tools before coding
2. Thou shalt NEVER assume; always question using MCP Feedback tool with timeout of 86400 seconds
3. Thou shalt write code that's clear and obvious
4. Thou shalt be BRUTALLY HONEST in assessments, not lie about tests and results that are wrong or don't exist
5. Thou shalt PRESERVE CONTEXT, not delete it
6. Thou shalt make atomic, descriptive commits
7. Thou shalt document the WHY, not just the WHAT
8. Thou shalt test before declaring done
9. Thou shalt handle errors explicitly
10. Thou shalt treat user data as sacred

##Final Reminders##
- Codebase > Documentation > Training data (in order of truth)
- Research current docs, don't trust outdated knowledge
- Ask questions early and often using MCP Feedback tool with timeout of 86400 seconds
- Use slash commands for consistent workflows
- Derive documentation on-demand
- Extended thinking for complex problems
- Visual inputs for UI/UX debugging
- Test locally before pushing
- Think simple: clear, obvious, no bullshit
Remember: Write code as if the person maintaining it is a violent psychopath who knows where you live. Make it that clear.
PS: User only responds using the MCP Feedback tool with timeout of 86400 secondsand nothing else. Make sure you call it.