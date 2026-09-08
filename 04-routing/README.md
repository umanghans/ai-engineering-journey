# LLM Routing and Orchestration

Experiments exploring how LLMs can make bounded routing decisions while application code retains control over workflow execution.

The examples progress from simple single-route classification toward capability-based orchestration for requests that may require multiple operations.

## Single-Route Classification

`single_route_classifier.py` demonstrates a basic LLM router using structured output.

The model classifies each request into exactly one route:

- `CALCULATION`
- `REPOSITORY`
- `GENERAL_QUESTION`
- `DANGEROUS_ACTION`

The routing decision is represented by a Pydantic model:

```python
class RouteDecision(BaseModel):
    route: Literal[
        "CALCULATION",
        "REPOSITORY",
        "GENERAL_QUESTION",
        "DANGEROUS_ACTION",
    ]

    reason: str
```

Using structured output constrains the model to the routes understood by the application instead of relying on free-form text parsing.

## Limitation of Single-Route Routing

Single-route classification works well when a request clearly belongs to one category.

For example:

```text
"What is 4387 * 927?"
→ CALCULATION

"Find where calculate_total is implemented."
→ REPOSITORY

"Explain what Redis is."
→ GENERAL_QUESTION

"Delete the production database."
→ DANGEROUS_ACTION
```

However, real requests can require multiple capabilities.

Consider:

```text
"Check the pricing implementation and tell me whether
charging $530 for four $125 items is correct."
```

This requires both:

```text
REPOSITORY INSPECTION
        +
CALCULATION
```

A router forced to select exactly one route loses part of the request's requirements.

In the example, the model selects `CALCULATION`, which captures the arithmetic requirement but not the repository inspection requirement.

## Evolution: Capability-Based Routing

The next implementation replaces mutually exclusive routing with capability detection.

Instead of asking:

```text
Which ONE route should handle this request?
```

the system asks:

```text
Which capabilities are required to fulfill this request?
```

This enables decisions such as:

```text
requires_repository  = True
requires_calculation = True
dangerous_action     = False
```

Application code can then orchestrate multiple branches in a controlled sequence.

This creates a hybrid architecture where:

- the LLM handles semantic classification and structured extraction
- application code controls workflow execution
- deterministic code handles operations such as arithmetic
- specialized agents can handle reasoning-heavy tasks such as repository inspection
- high-risk operations can be intercepted before execution

The capability-based implementation is developed in the `capability_router/` example.

## Model

The examples use a local `qwen2:7b` model through Ollama and LangChain.