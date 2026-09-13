# State Machine Workflow

This example demonstrates how a workflow can be modeled using explicit state, named stages, and controlled transitions.

The goal is to make orchestration visible and deterministic before introducing a graph framework such as LangGraph.

## Workflow

```text
START
  ↓
PLAN
  ↓
VALIDATE
  ↓
EXECUTE
  ↓
success? ── yes ──> DONE
  |
  no
  ↓
REFLECT
  |
  ├── retry allowed ──> EXECUTE
  └── retry limit ────> FAILED