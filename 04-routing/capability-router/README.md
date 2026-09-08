# Capability-Based LLM Router

A hybrid LLM workflow that identifies all capabilities required by a request and uses deterministic application code to orchestrate the required execution branches.

This example evolves the single-route classifier into a system capable of handling requests that require multiple capabilities.

## Architecture

```text
User Request
      |
      v
Capability Classifier (LLM)
      |
      v
Structured CapabilityDecision
      |
      v
Code-Controlled Orchestration
      |
      +-- Dangerous Action?
      |       |
      |       +--> Block / Require Human Approval
      |
      +-- Repository Required?
      |       |
      |       +--> Repository Inspection Agent
      |                |
      |                +--> search_repository
      |                +--> read_file
      |                |
      |                +--> Structured RepositoryResult
      |
      +-- Calculation Required?
      |       |
      |       +--> Calculation Type Classifier
      |                |
      |                +--> Structured Input Extraction
      |                |
      |                +--> Deterministic Python Calculation
      |
      +-- General Knowledge Required?
              |
              +--> General Knowledge Branch
```

## Capability Detection

Instead of selecting exactly one route, the model returns independent capability flags:

```python
class CapabilityDecision(BaseModel):
    requires_repository: bool
    requires_calculation: bool
    dangerous_action: bool
    requires_general_knowledge: bool
    reason: str
```

This allows a single request to require multiple capabilities.

For example:

```text
Check the pricing implementation and tell me whether
charging $530 for four $125 items is correct.
```

produces a decision equivalent to:

```text
REPOSITORY:        True
CALCULATION:       True
DANGEROUS:         False
GENERAL KNOWLEDGE: False
```

The workflow can therefore inspect the repository first and pass the discovered information into the calculation branch.

## Repository Worker

`repository_worker.py` implements a specialized repository inspection agent.

The agent can:

- search repository filenames and contents
- read relevant files
- inspect implementation details
- return grounded findings as structured output

The worker operates only inside the local `sandbox/` directory.

Filesystem access is constrained by resolving requested paths and rejecting paths outside the sandbox.

## Context Between Workflow Branches

Repository inspection can produce information needed by later branches.

For the pricing example, the repository worker discovers:

```text
pricing.py
TAX_RATE = 0.06
```

The orchestrator stores the tax rate in workflow context and passes it to the calculation branch.

The resulting calculation is performed by Python:

```text
4 × $125 = $500
$500 × 1.06 = $530
```

The workflow can then verify that the user's claimed total is correct.

## Model-Controlled vs Code-Controlled Decisions

The architecture deliberately separates reasoning from execution.

### Model controlled

The LLM determines:

- which capabilities are required
- which type of calculation is requested
- structured arithmetic inputs
- structured pricing inputs
- how to inspect the repository using the available tools

### Code controlled

Python determines:

- execution order
- whether dangerous requests are blocked
- which workflow branches run
- how context moves between branches
- arithmetic execution
- pricing verification

This keeps flexible semantic decisions with the model while keeping predictable operations under application control.

## Safety Boundary

Requests classified as dangerous are intercepted before other workflow branches execute.

For example:

```text
Delete the production database.
```

results in:

```text
WORKFLOW: BLOCK / REQUIRE HUMAN APPROVAL
```

The example does not implement destructive production tools. The guard demonstrates where human approval or another runtime policy could be enforced in a production workflow.

## Sandbox

The included sandbox is a small sample repository used to test repository-aware behavior.

```text
sandbox/
├── pricing.py
└── users.py
```

It exists only as controlled example data for the repository worker.

## Current Scope

The general-knowledge branch currently demonstrates routing only and does not generate a final informational response.

The focus of this example is capability detection, multi-branch orchestration, repository inspection, deterministic execution, and runtime safety boundaries rather than implementing a general-purpose assistant.

## Model

The workflow uses a local `qwen2:7b` model through Ollama, LangChain, and LangGraph-based agents.