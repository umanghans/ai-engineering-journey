from typing import Literal

from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    action: Literal[
        "SEARCH_REPOSITORY",
        "READ_FILE",
        "EDIT_FILE",
        "RUN_TESTS",
        "INSPECT_TEST_FAILURE",
        "GENERATE_DIFF",
        "REQUEST_HUMAN_APPROVAL",
    ] = Field(
        description="Permitted action for this step."
    )

    target: str | None = Field(
        default=None,
        description=(
            "Target of the action if known, such as a filename, "
            "search query, or test target."
        ),
    )

    reason: str = Field(
        description="Why this step is necessary."
    )


class ExecutionPlan(BaseModel):
    steps: list[PlanStep] = Field(
        description="Ordered steps required to accomplish the task."
    )


model = ChatOllama(
    model="qwen2:7b",
    temperature=0,
    num_predict=600,
)

planner = model.with_structured_output(ExecutionPlan)


def create_plan(task: str) -> ExecutionPlan:
    """Create an initial structured execution plan."""
    return planner.invoke(
        [
            {
                "role": "system",
                "content": """
You are a software-engineering task planner.

Create a concise ordered plan using ONLY the actions allowed
by the provided structured output schema.

You are planning, not executing.

Rules:
- Respect dependencies between steps.
- Do not claim you inspected files or ran tests.
- Do not assume repository facts that have not been observed.
- If an exact target is unknown, use a search step first.
- Include verification after code changes.
- Do not deploy, push, merge, or perform production actions.
- Use REQUEST_HUMAN_APPROVAL before any consequential action
  that genuinely requires human authorization.
""",
            },
            {
                "role": "user",
                "content": task,
            },
        ]
    )


def validate_plan(
    plan: ExecutionPlan,
    observed_files: set[str] | None = None,
) -> list[str]:
    """Apply deterministic validation rules to a generated plan."""
    errors: list[str] = []
    observed_files = observed_files or set()

    for index, step in enumerate(plan.steps, start=1):
        if step.action == "EDIT_FILE":
            if not step.target or not step.target.endswith(".py"):
                errors.append(
                    f"Step {index}: EDIT_FILE requires a concrete .py target."
                )
            elif step.target not in observed_files:
                errors.append(
                    f"Step {index}: EDIT_FILE target '{step.target}' has not "
                    "been observed in repository state."
                )

        if step.action == "READ_FILE":
            if not step.target:
                errors.append(
                    f"Step {index}: READ_FILE requires a concrete target."
                )
            elif step.target not in observed_files:
                errors.append(
                    f"Step {index}: READ_FILE target '{step.target}' has not "
                    "been observed in repository state."
                )

        if step.action == "INSPECT_TEST_FAILURE":
            previous_actions = [
                previous_step.action
                for previous_step in plan.steps[: index - 1]
            ]

            if "RUN_TESTS" not in previous_actions:
                errors.append(
                    f"Step {index}: cannot inspect test failure "
                    "before RUN_TESTS."
                )

        forbidden_words = [
            "deploy",
            "merge",
            "push",
            "production",
        ]

        combined_text = (
            f"{step.target or ''} {step.reason}"
        ).lower()

        for word in forbidden_words:
            if word in combined_text:
                errors.append(
                    f"Step {index}: contains unsupported action '{word}'."
                )

    return errors


def replan_with_feedback(
    task: str,
    previous_plan: ExecutionPlan,
    feedback: str,
) -> ExecutionPlan:
    """Generate a better plan using qualitative feedback."""
    prompt = f"""
You previously generated this execution plan:

{previous_plan.model_dump_json(indent=2)}

QUALITY FEEDBACK:

{feedback}

Generate an improved execution plan for the ORIGINAL REQUEST:

{task}

Rules:
- Address the quality feedback.
- Do not explain the previous plan.
- Do not invent repository facts that have not been observed.
- Return only the new structured plan.
"""

    return planner.invoke(prompt)


def repair_invalid_plan(
    task: str,
    invalid_plan: ExecutionPlan,
    validation_errors: list[str],
) -> ExecutionPlan:
    """Repair a plan that failed deterministic validation."""
    validation_feedback = "\n".join(
        f"- {error}" for error in validation_errors
    )

    prompt = f"""
The following execution plan failed deterministic validation:

{invalid_plan.model_dump_json(indent=2)}

VALIDATION ERRORS:

{validation_feedback}

Original task:

{task}

Generate a corrected execution plan.

Important:
- Fix the validation errors.
- Do not invent repository facts that have not been observed.
- If a concrete filename is not yet known, do not pretend that it is known.
- Preserve useful parts of the previous plan where possible.
"""

    return planner.invoke(prompt)


def print_plan(
    title: str,
    plan: ExecutionPlan,
    errors: list[str],
) -> None:
    """Print a plan and its deterministic validation result."""
    print(f"\n=== {title} ===")

    for number, step in enumerate(plan.steps, start=1):
        print(f"\nSTEP {number}")
        print(f"ACTION: {step.action}")
        print(f"TARGET: {step.target}")
        print(f"REASON: {step.reason}")

    if errors:
        print("\n=== PLAN REJECTED ===")

        for error in errors:
            print(f"- {error}")
    else:
        print("\n=== PLAN ACCEPTED ===")


if __name__ == "__main__":
    observed_files: set[str] = set()

    task = (
        "Add retry logic to the external payment API "
        "and make sure existing behavior isn't broken."
    )

    quality_feedback = """
The previous plan passed hard validation, but it is low quality.

Problems:
- It requests human approval far too often.
- It does not actually perform the requested code change.
- It never reads the relevant implementation.
- It never edits a file.
- It never runs tests.
- It never generates a diff.

Improve the plan so that it makes concrete progress toward completing the task.

Human approval should only be requested when an operation genuinely
requires approval. Do not use approval as a substitute for taking
ordinary development actions.
"""

    initial_plan = create_plan(task)

    initial_errors = validate_plan(
        initial_plan,
        observed_files=observed_files,
    )

    print_plan(
        "INITIAL PLAN",
        initial_plan,
        initial_errors,
    )

    improved_plan = replan_with_feedback(
        task=task,
        previous_plan=initial_plan,
        feedback=quality_feedback,
    )

    improved_errors = validate_plan(
        improved_plan,
        observed_files=observed_files,
    )

    print_plan(
        "REPLANNED",
        improved_plan,
        improved_errors,
    )

    if improved_errors:
        repaired_plan = repair_invalid_plan(
            task=task,
            invalid_plan=improved_plan,
            validation_errors=improved_errors,
        )

        repaired_errors = validate_plan(
            repaired_plan,
            observed_files=observed_files,
        )

        print_plan(
            "REPAIRED PLAN",
            repaired_plan,
            repaired_errors,
        )