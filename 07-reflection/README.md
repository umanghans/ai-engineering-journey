# LLM Reflection with Runtime-Controlled Retry

A reflection workflow that evaluates execution failures, produces a structured diagnosis, and recommends what should happen next.

This example demonstrates a core agentic AI pattern:

```text
Execute → Observe → Reflect → Decide
```

The LLM analyzes the execution result, but deterministic runtime code retains control over whether the recommended action is actually allowed.

## Architecture

```text
                  Task + Execution Result
                           |
                           v
                    Reflection Model
                           |
                           v
                  Structured Reflection
                   /       |        \
                  /        |         \
           Diagnosis   Next Action   Reason
                          |
                          v
                    Runtime Policy
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
     Allow Retry      Block Retry     Other Action
                                      /    |     \
                                 Inspect  Change  Stop
```

The workflow separates two responsibilities:

```text
LLM
"What should happen next?"

        vs.

Runtime
"Is that action actually allowed?"
```

## Structured Reflection

The reflection model returns a Pydantic object rather than unrestricted text.

```python
class Reflection(BaseModel):
    diagnosis: str

    next_action: Literal[
        "RETRY",
        "INSPECT_FAILURE",
        "CHANGE_APPROACH",
        "STOP",
    ]

    reason: str
```

This constrains the model to a small set of actions that the runtime understands.

## Reflection Actions

The model can recommend four possible actions.

### RETRY

Repeat the same operation without changing the implementation.

This is appropriate when a failure appears transient.

For example:

```text
Connection reset
Temporary network failure
Service temporarily unavailable
```

### INSPECT_FAILURE

Gather additional information before deciding what to change.

This is useful when the available evidence is insufficient to diagnose the problem.

### CHANGE_APPROACH

The current implementation or strategy likely needs modification.

This is appropriate when execution provides concrete evidence that the current approach is incorrect.

### STOP

No further useful action should be taken.

This provides an explicit termination path rather than allowing an agent to continue indefinitely.

## Reflection Uses Observed Evidence

The reflection prompt receives:

```text
Original Task
      +
Execution Result
      +
Retry State
```

The model is explicitly instructed to base its diagnosis only on this information.

It should not claim that it fixed code, executed additional operations, or observed information that was never provided.

This keeps reflection grounded in actual execution feedback.

## Runtime-Controlled Retry

The most important boundary in this example is that the LLM does **not** control the retry loop directly.

The model can recommend:

```text
RETRY
```

but deterministic Python code decides whether another attempt is permitted.

```python
if retry_count >= MAX_RETRIES:
    print(
        "RUNTIME DECISION: RETRY BLOCKED "
        "(maximum retries reached)"
    )
```

This prevents the model from overriding retry limits.

The architecture therefore becomes:

```text
Model Recommendation
        |
        v
      RETRY
        |
        v
Deterministic Runtime Policy
        |
     +--+--+
     |     |
   Allow  Block
```

## Bounded Agent Behavior

Without runtime limits, a reflective agent could repeatedly decide to retry:

```text
Failure
  ↓
Reflect
  ↓
Retry
  ↓
Failure
  ↓
Reflect
  ↓
Retry
  ↓
...
```

This can create an uncontrolled loop.

The example introduces:

```python
MAX_RETRIES = 2
```

so the runtime maintains a hard upper bound regardless of what the model recommends.

This illustrates a broader production principle:

```text
LLM decisions should operate inside deterministic boundaries.
```

## Test Scenario

The example evaluates two different failure modes for the same software-engineering task.

### Attempt 1 — Ambiguous Failure

The test runner reports:

```text
ConnectionError: connection reset by peer.
No assertions were executed.
```

The reflection model recommends:

```text
INSPECT_FAILURE
```

The available evidence does not establish that the implementation itself is wrong, so gathering more information is more appropriate than modifying the code.

### Attempt 2 — Concrete Behavioral Failure

The test reports:

```text
Expected: 3 payment attempts
Actual: 1 payment attempt
```

The reflection model recommends:

```text
CHANGE_APPROACH
```

Unlike the first failure, this result contains direct evidence that the retry behavior does not match the expected behavior.

The two cases demonstrate that reflection can distinguish between different kinds of execution feedback rather than treating every failure as a reason to retry.

## Model Decision vs. Runtime Decision

Both decisions are printed separately:

```text
MODEL DECISION: CHANGE_APPROACH
RUNTIME DECISION: CHANGE_APPROACH
```

This distinction is intentional.

In a larger agent system, the model may propose an action that runtime policy rejects.

For example:

```text
MODEL DECISION: RETRY

          ↓

retry_count >= MAX_RETRIES

          ↓

RUNTIME DECISION: RETRY BLOCKED
```

The model therefore acts as a reasoning component rather than the final authority over execution.

## Relationship to Planning

Planning and reflection solve different parts of an agent workflow.

```text
                 User Task
                     |
                     v
                  Planner
                     |
                     v
                   Plan
                     |
                     v
                  Execute
                     |
                     v
                  Result
                     |
                     v
                 Reflect
                     |
                     v
              Next Decision
```

The planner determines what should happen before execution.

The reflector reasons about what happened **after** execution.

Together, these patterns form part of the foundation for iterative agent workflows.

## Current Scope

This example focuses specifically on:

- structured reflection
- failure diagnosis
- bounded retry recommendations
- deterministic runtime policy
- distinguishing ambiguous failures from concrete behavioral failures

It does not modify code or execute the recommended follow-up actions.

A larger workflow could connect the reflection result back into planning or execution.

## Model

This example uses:

```text
qwen3:8b
```

locally through Ollama and LangChain.

For this experiment, reasoning mode is disabled in the `ChatOllama` configuration because that setting was required for stable structured-output behavior in this specific reflection workflow.

The runtime safety policy remains independent of the model configuration.