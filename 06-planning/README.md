# LLM Planning with Validation and Replanning

A structured software-engineering planner that generates ordered execution plans, validates them with deterministic rules, and attempts to improve or repair plans when problems are discovered.

This example explores an important agentic AI distinction:

```text
Planning != Execution
```

An LLM can propose actions, but proposed actions do not mean those actions have actually occurred or that their results are known.

## Architecture

```text
                         User Task
                             |
                             v
                       LLM Planner
                             |
                             v
                    Structured Plan
                             |
                             v
                Deterministic Validation
                             |
                  +----------+----------+
                  |                     |
                Valid                 Invalid
                  |                     |
                  v                     v
          Quality Evaluation       Repair Prompt
                  |                     |
                  v                     v
              Replanning          Repaired Plan
                  |                     |
                  +----------+----------+
                             |
                             v
                Deterministic Validation
```

The LLM is responsible for proposing plans.

Python code remains responsible for enforcing hard constraints.

## Structured Planning

Plans use Pydantic models rather than unrestricted text.

Each step contains:

- an allowed action
- an optional target
- a reason for the action

The planner can only choose from a constrained action vocabulary:

```text
SEARCH_REPOSITORY
READ_FILE
EDIT_FILE
RUN_TESTS
INSPECT_TEST_FAILURE
GENERATE_DIFF
REQUEST_HUMAN_APPROVAL
```

For example:

```python
class PlanStep(BaseModel):
    action: Literal[
        "SEARCH_REPOSITORY",
        "READ_FILE",
        "EDIT_FILE",
        "RUN_TESTS",
        "INSPECT_TEST_FAILURE",
        "GENERATE_DIFF",
        "REQUEST_HUMAN_APPROVAL",
    ]

    target: str | None
    reason: str
```

This prevents the planner from freely inventing arbitrary action types.

## Deterministic Validation

Structured output guarantees the **shape** of a plan, but it does not guarantee that the plan is valid.

A separate Python validator therefore checks constraints that should not depend on LLM judgment.

Examples include:

- `EDIT_FILE` requires a concrete Python file
- files must already exist in observed repository state before they can be read or edited
- test failures cannot be inspected before tests are run
- unsupported operations such as deployment, merging, or pushing are rejected

This creates a boundary between:

```text
LLM
"What should we do?"

        vs.

Deterministic Code
"Is this plan allowed?"
```

## Quality-Driven Replanning

A plan can satisfy every hard validation rule and still be a bad plan.

During testing, the initial planner generated a plan dominated by unnecessary human-approval requests. It technically passed deterministic validation but made little progress toward the requested code change.

The workflow therefore provides qualitative feedback to the planner and asks it to generate an improved plan.

```text
Initial Plan
     |
     v
Passes Hard Validation
     |
     v
Poor Planning Quality
     |
     v
Quality Feedback
     |
     v
Replanning
```

This demonstrates that **hard validation and plan quality are separate concerns**.

## Repairing Invalid Plans

The replanned version made more concrete progress by proposing actions such as:

```text
EDIT_FILE
RUN_TESTS
GENERATE_DIFF
```

However, it attempted to edit a file without knowing the filename.

The deterministic validator rejected the plan:

```text
EDIT_FILE requires a concrete .py target.
```

The rejected plan and validation errors were then passed back to the LLM for repair.

This creates a simple feedback loop:

```text
Generate
   |
   v
Validate
   |
   +---- valid ----> continue
   |
   +---- invalid
           |
           v
         Repair
           |
           v
        Validate
```

## Preventing Hallucinated Repository State

Testing the repair loop revealed another important failure mode.

After being told that `EDIT_FILE` required a concrete filename, the model generated:

```text
external_payment_api.py
```

The filename looked reasonable, but no repository search had actually been executed.

The model had satisfied the **syntactic requirement** while inventing a repository fact.

To prevent this, the validator tracks files that have actually been observed:

```python
observed_files: set[str] = set()
```

An edit target must exist in this observed state before the plan can be accepted.

The repaired plan was therefore rejected with:

```text
EDIT_FILE target 'external_payment_api.py'
has not been observed in repository state.
```

This demonstrates why agent systems should not rely solely on instructions such as:

```text
"Do not invent repository facts."
```

Important constraints should be enforced by code when possible.

## Planning vs. Execution

A particularly important lesson from this example is that placing:

```text
SEARCH_REPOSITORY
```

earlier in a plan does not mean the repository has actually been searched.

A planner can propose:

```text
1. SEARCH_REPOSITORY
2. READ_FILE
3. EDIT_FILE
```

but it cannot know the result of Step 1 while generating the entire plan unless that information was already available.

A true planner/executor system would instead operate iteratively:

```text
Plan
  |
  v
SEARCH_REPOSITORY
  |
  v
Executor performs search
  |
  v
Repository state updated
  |
  v
Planner receives observations
  |
  v
Plan next actions
```

This example intentionally stops before implementing that executor loop.

## What the Example Demonstrates

The workflow separates several responsibilities:

```text
Structured Output
        |
        +--> constrains plan format

LLM Planner
        |
        +--> proposes actions

Quality Feedback
        |
        +--> improves weak plans

Deterministic Validator
        |
        +--> enforces hard constraints

Observed State
        |
        +--> prevents invented repository facts

Repair Loop
        |
        +--> gives rejected plans another attempt
```

Together, these mechanisms provide stronger control than relying on prompting alone.

## Current Scope

This example implements the **planning, validation, replanning, and repair** portions of a planner/executor architecture.

It does not yet execute repository searches, read files, modify code, or run tests.

Those operations would belong to an executor that updates workflow state with real observations before additional planning occurs.

## Model

This example uses:

```text
qwen2:7b
```

locally through Ollama and LangChain.

The model generates structured execution plans while deterministic Python logic controls whether those plans are accepted.