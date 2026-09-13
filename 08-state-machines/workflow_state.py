from dataclasses import dataclass
from typing import Literal


Status = Literal[
    "START",
    "PLANNING",
    "VALIDATING",
    "EXECUTING",
    "REFLECTING",
    "DONE",
    "FAILED",
]

ExecutionResult = Literal[
    "TEST_FAILED",
    "TEST_PASSED",
]


@dataclass
class WorkflowState:
    task: str
    status: Status = "START"
    retry_count: int = 0
    max_retries: int = 2
    last_result: ExecutionResult | None = None


def plan_node(state: WorkflowState) -> WorkflowState:
    """Transition the workflow into the planning stage."""
    print("\n[NODE] PLAN")

    state.status = "PLANNING"

    print(f"Task: {state.task}")

    return state


def validate_node(state: WorkflowState) -> WorkflowState:
    """Validate the planned workflow before execution."""
    print("\n[NODE] VALIDATE")

    state.status = "VALIDATING"

    print("Plan validation passed.")

    return state


def execute_node(state: WorkflowState) -> WorkflowState:
    """
    Simulate task execution.

    The first attempt fails and the next attempt succeeds so the
    workflow demonstrates reflection and retry transitions.
    """
    print("\n[NODE] EXECUTE")

    state.status = "EXECUTING"

    if state.retry_count == 0:
        state.last_result = "TEST_FAILED"
    else:
        state.last_result = "TEST_PASSED"

    print(f"Execution result: {state.last_result}")

    return state


def reflect_node(state: WorkflowState) -> WorkflowState:
    """Inspect a failed execution and decide whether to retry."""
    print("\n[NODE] REFLECT")

    state.status = "REFLECTING"

    print(f"Reflecting on: {state.last_result}")

    if state.retry_count >= state.max_retries:
        print("Decision: STOP")
        state.status = "FAILED"
        return state

    state.retry_count += 1

    print(
        f"Decision: RETRY "
        f"({state.retry_count}/{state.max_retries})"
    )

    return state


def run_workflow(state: WorkflowState) -> WorkflowState:
    """Run the workflow until it reaches a terminal state."""
    state = plan_node(state)
    state = validate_node(state)

    while state.status not in {"DONE", "FAILED"}:
        state = execute_node(state)

        if state.last_result == "TEST_PASSED":
            print("\nTRANSITION: EXECUTE -> DONE")
            state.status = "DONE"
            break

        print("\nTRANSITION: EXECUTE -> REFLECT")

        state = reflect_node(state)

        if state.status == "FAILED":
            print("TRANSITION: REFLECT -> FAILED")
            break

        print("TRANSITION: REFLECT -> EXECUTE")

    return state


if __name__ == "__main__":
    workflow_state = WorkflowState(
        task="Add retry logic to the payment API."
    )

    print("INITIAL STATE")
    print(workflow_state)

    workflow_state = run_workflow(workflow_state)

    print("\nFINAL STATE")
    print(workflow_state)