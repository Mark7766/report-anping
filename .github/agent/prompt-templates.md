<!-- ai-coding-ok: v3.0.0 -->
# 🧩 report-anping — Prompt Template Library

> Standard prompt templates the AI agent uses in different scenarios.
> Humans can also copy these to talk to Copilot Chat efficiently.

---

## 📋 Requirements Analysis Template

```
Please analyze the following requirement as a product manager:

Requirement: {{requirements}}
Business context: Hermes Skill — 微信对话驱动地震安评报告生成服务，极简主义，个人/小团队工具

Please output:
1. User story (As a <role>, I want ... so that ...)
2. Acceptance criteria (as a checkbox list)
3. Edge cases
4. Priority suggestion (P0/P1/P2)
5. Does it align with the project's design principles? If not, how to simplify?
```

---

## 🏛️ Architecture Design Template

```
Please design a technical solution for the following feature as an architect:

Feature: {{feature-description}}

Constraints:
- Python 3.11, FastAPI, SQLite, SQLAlchemy (sync), uv, ruff
- Single function ≤ 50 lines, single file ≤ 500 lines, line width 120 chars
- No heavy dependencies; no hardcoded secrets; no print() for logging
- All handlers must return HermesResponse; async-first for I/O

Please first read the following context files:
- .github/agent/memory/project-memory.md
- .github/agent/memory/decisions-log.md

Please output:
1. Module breakdown and responsibilities
2. Data model design
3. API design (if needed)
4. Relationship to existing modules
5. Risk assessment
```

---

## 💻 Implementation Template

```
Please implement the following feature:

Feature: {{feature-description}}
Relevant files: {{relevant-file-paths}}

Requirements:
1. Follow the standards in .github/agent/coding-standards.md
2. Include full type annotations and docstrings
3. Include unit tests
4. After completion, update .github/agent/memory/task-history.md
```

---

## 🐛 Bug Fix Template

```
Please fix the following bug:

Bug: {{bug-description}}
Reproduction steps: {{reproduction-steps}}
Expected behavior: {{expected-behavior}}
Actual behavior: {{actual-behavior}}
Error log: {{error-log}}

Please follow these steps:
1. First write a failing test that reproduces the bug
2. Analyze the root cause
3. Fix the code
4. Make sure the test passes
5. Check whether similar issues exist
```

---

## 🔍 Code Review Template

```
Please code-review the following code/change:

File: {{file-path-or-change-description}}

Review across these dimensions:
1. Correctness: is the logic correct? Are edge cases handled?
2. Security: any leak risks?
3. Simplicity: is it over-engineered? Can it be simpler?
4. Readability: are names and structure clear?
5. Testability: is it easy to test?
6. Standards compliance: does it match coding-standards.md?

Please provide concrete improvement suggestions.
```

---

## 📊 Test Writing Template

```
Please write tests for the following:

Module under test: {{module-path}}
Functionality: {{feature-description}}

Requirements:
1. Use pytest
2. Test naming: test_<method>_<scenario>_<expected>
3. Use the AAA pattern (Arrange-Act-Assert)
4. Cover: happy path / boundary values / invalid inputs / error handling
5. For time-related tests, use freezegun to pin time
```
