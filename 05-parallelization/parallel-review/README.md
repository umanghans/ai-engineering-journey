# Parallel LLM Code Review

A parallel LLM workflow that runs multiple specialized code reviewers concurrently and synthesizes their findings into a single final review.

This example demonstrates the **fan-out / fan-in orchestration pattern** for tasks where several independent LLM operations can run simultaneously.

## Architecture

```text
                         Source Code
                              |
                         FAN OUT
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
        Correctness        Security      Maintainability
          Reviewer         Reviewer         Reviewer
              |               |               |
              +---------------+---------------+
                              |
                           FAN IN
                              |
                              v
                    Specialized Reviews
                              |
                              v
                      Synthesis Model
                    /                 \
             Original Code       Review Results
                    \                 /
                     \               /
                              |
                              v
                         Final Review
```

## Parallel Execution

Each reviewer receives the same source code but has a different responsibility:

- **Correctness** — incorrect behavior, edge cases, and ambiguous implementation
- **Security** — security risks and unsafe behavior
- **Maintainability** — readability, API design, typing, and maintainability

Because these reviews are independent, they are executed concurrently using Python's `ThreadPoolExecutor`.

```python
with ThreadPoolExecutor(
    max_workers=len(REVIEWERS)
) as executor:
    futures = {
        name: executor.submit(
            review_code,
            name,
            instructions,
        )
        for name, instructions in REVIEWERS.items()
    }
```

This avoids unnecessarily executing independent LLM calls sequentially.

## Fan-Out / Fan-In

The workflow follows a common parallel orchestration pattern:

```text
                 Input
                   |
                FAN OUT
             /      |      \
            v       v       v
         Worker   Worker   Worker
            \       |       /
             \      |      /
                FAN IN
                   |
                   v
              Aggregation
```

The workflow **fans out** the source code to specialized reviewers and then **fans in** their results for synthesis.

## Specialized Reviewers

Specialization is created through system instructions rather than separate models.

For example:

```python
REVIEWERS = {
    "correctness": (
        "Look for incorrect behavior, edge cases, "
        "and ambiguous implementation."
    ),
    "security": (
        "Look only for security risks and unsafe behavior."
    ),
    "maintainability": (
        "Look for readability, API design, typing, "
        "and maintainability problems."
    ),
}
```

Each model call is therefore responsible for a narrower part of the overall problem.

## Synthesis and Adjudication

Simply combining several LLM responses does not guarantee a better result.

Individual reviewers may produce:

- incorrect observations
- speculative improvements
- overlapping findings
- conflicting recommendations

The synthesis stage therefore receives both the **original source code** and the **specialized reviews**.

```text
Original Code ──────────┐
                        ├──> Synthesis Model ──> Final Review
Specialized Reviews ────┘
```

This gives the synthesizer evidence it can use to evaluate reviewer claims rather than blindly concatenating their responses.

The synthesis prompt asks the model to:

- evaluate findings against the original code
- reject findings describing behavior already handled correctly
- distinguish defects from optional design choices
- remove duplicate findings
- identify questionable or conflicting claims
- prioritize concrete issues

## Observed Behavior

During testing, some specialized reviewers produced weak findings about zero-price and zero-discount behavior.

When the synthesizer received only the reviewer outputs, it largely preserved those findings.

After the original source code was also provided to the synthesis stage, the final review successfully removed several weak and duplicated observations and consolidated the results into a smaller set of findings.

This demonstrates an important orchestration principle:

```text
Aggregation != Verification
```

Giving the aggregation stage access to the original evidence can improve its ability to judge intermediate LLM outputs.

However, the synthesis model is still an LLM and should not be treated as a deterministic verifier.

## Reliability

For higher-confidence code review systems, LLM review could be combined with deterministic tools such as:

- unit tests
- static analysis
- type checking
- security scanners
- structured validation
- human approval for consequential changes

Parallel LLM reviewers are useful for increasing perspective and coverage, but deterministic evidence remains valuable when correctness matters.

## Model

This example uses the local:

```text
qwen3:8b
```

model through Ollama and LangChain.

The model runs locally; no hosted LLM API is required for this example.