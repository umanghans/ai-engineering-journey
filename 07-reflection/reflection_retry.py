from typing import Literal

from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field


class Reflection(BaseModel):
    diagnosis: str = Field(
        description="Likely reason the previous attempt failed."
    )

    next_action: Literal[
        "RETRY",
        "INSPECT_FAILURE",
        "CHANGE_APPROACH",
        "STOP",
    ] = Field(
        description="What should happen next."
    )

    reason: str = Field(
        description="Why this next action is appropriate."
    )


MAX_RETRIES = 2


model = ChatOllama(
    model="qwen3:8b",
    temperature=0,
    num_predict=200,
    reasoning=False,
)

reflector = model.with_structured_output(Reflection)


def reflect(
    task: str,
    execution_result: str,
    retry_count: int,
) -> Reflection:
    """Reflect on an execution result and recommend the next action."""
    prompt = f"""
You are reflecting on the result of an attempted software-engineering task.

ORIGINAL TASK:
{task}

EXECUTION RESULT:
{execution_result}

RETRY STATE:
Retries already attempted: {retry_count}
Maximum retries allowed: {MAX_RETRIES}

Decide what should happen next.

Rules:
- Do not claim to have fixed anything.
- Base your diagnosis only on the information provided.
- RETRY means repeat the same action without changing anything.
- INSPECT_FAILURE means gather more information about the failure.
- CHANGE_APPROACH means the current implementation or strategy likely
  needs modification.
- STOP means no further useful action should be taken.
- For failures that may be transient, RETRY may be appropriate.
"""

    return reflector.invoke(prompt)


def apply_runtime_policy(
    reflection: Reflection,
    retry_count: int,
) -> int:
    """
    Apply deterministic runtime rules to the model's recommendation.

    The model may recommend RETRY, but the runtime controls whether
    another retry is actually permitted.
    """
    if reflection.next_action != "RETRY":
        print(
            f"RUNTIME DECISION: {reflection.next_action}"
        )
        return retry_count

    if retry_count >= MAX_RETRIES:
        print(
            "RUNTIME DECISION: RETRY BLOCKED "
            "(maximum retries reached)"
        )
        return retry_count

    retry_count += 1

    print(
        f"RUNTIME DECISION: RETRY ALLOWED "
        f"({retry_count}/{MAX_RETRIES})"
    )

    return retry_count


def print_reflection(reflection: Reflection) -> None:
    """Print the model's diagnosis and recommended next action."""
    print(f"DIAGNOSIS: {reflection.diagnosis}")
    print(f"MODEL DECISION: {reflection.next_action}")
    print(f"REASON: {reflection.reason}")


if __name__ == "__main__":
    task = "Add retry logic to the external payment API."

    execution_results = [
        """
RUN_TESTS failed.

ConnectionError: connection reset by peer.
No assertions were executed.
""",
        """
RUN_TESTS failed.

Test: test_payment_retry
Expected: 3 payment attempts
Actual: 1 payment attempt

AssertionError: expected call_count == 3, got 1
""",
    ]

    retry_count = 0

    for attempt_number, execution_result in enumerate(
        execution_results,
        start=1,
    ):
        print(f"\n=== ATTEMPT {attempt_number} ===")
        print(execution_result.strip())

        print("\nReflecting...")

        reflection = reflect(
            task=task,
            execution_result=execution_result,
            retry_count=retry_count,
        )

        print_reflection(reflection)

        retry_count = apply_runtime_policy(
            reflection=reflection,
            retry_count=retry_count,
        )

    print(f"\nFINAL RETRY COUNT: {retry_count}")