from typing import Literal

from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from repository_worker import inspect_repository


class CalculationInputs(BaseModel):
    unit_price: float = Field(
        description="Price of one item."
    )
    quantity: int = Field(
        description="Number of items."
    )
    claimed_total: float | None = Field(
        description="Total claimed by the user, if one was provided."
    )


class CalculationTypeDecision(BaseModel):
    calculation_type: Literal[
        "GENERIC_ARITHMETIC",
        "PRICING_CHECK",
    ] = Field(
        description="The type of calculation required."
    )


class CapabilityDecision(BaseModel):
    requires_repository: bool = Field(
        description="True if answering requires inspecting repository contents."
    )
    requires_calculation: bool = Field(
        description="True if answering requires arithmetic calculation."
    )
    dangerous_action: bool = Field(
        description="True if the request asks for a destructive or high-risk action."
    )
    requires_general_knowledge: bool = Field(
        description="True if answering requires general knowledge."
    )
    reason: str = Field(
        description="Brief explanation of the required capabilities."
    )


class ArithmeticInputs(BaseModel):
    left: float
    operator: Literal["+", "-", "*", "/"]
    right: float


model = ChatOllama(
    model="qwen2:7b",
    temperature=0,
)

capability_router = model.with_structured_output(
    CapabilityDecision
)

calculation_type_router = model.with_structured_output(
    CalculationTypeDecision
)

calculation_extractor = model.with_structured_output(
    CalculationInputs
)

arithmetic_extractor = model.with_structured_output(
    ArithmeticInputs
)


SYSTEM_PROMPT = """
You identify which capabilities are required to fulfill a user's request.

A request may require MORE THAN ONE capability.

Capabilities:

REPOSITORY:
Requires inspecting source code or repository contents.

CALCULATION:
Requires arithmetic.

DANGEROUS_ACTION:
Requests a destructive or high-risk operation.

GENERAL_KNOWLEDGE:
Requires answering from general knowledge.

Do not choose only the most obvious capability.
Identify every capability required to fully complete the request.
"""


def classify_request(request: str) -> CapabilityDecision:
    """Identify all capabilities required by a request."""
    return capability_router.invoke(
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": request,
            },
        ]
    )


def classify_calculation_type(
    request: str,
) -> CalculationTypeDecision:
    """Classify the kind of calculation required."""
    return calculation_type_router.invoke(
        [
            {
                "role": "system",
                "content": """
Classify the calculation requested by the user.

GENERIC_ARITHMETIC:
A normal mathematical calculation such as addition,
subtraction, multiplication, or division.

PRICING_CHECK:
A calculation involving item prices, quantities, totals,
tax rates, or verifying a claimed price.

Choose exactly one.
""",
            },
            {
                "role": "user",
                "content": request,
            },
        ]
    )


def extract_arithmetic_inputs(
    request: str,
) -> ArithmeticInputs:
    """Extract operands without asking the model to calculate."""
    return arithmetic_extractor.invoke(
        [
            {
                "role": "system",
                "content": """
Extract the arithmetic expression from the user's request.

Do not calculate the answer.
Return only:
- left operand
- operator
- right operand
""",
            },
            {
                "role": "user",
                "content": request,
            },
        ]
    )


def extract_calculation_inputs(
    request: str,
) -> CalculationInputs:
    """Extract pricing values without performing the calculation."""
    return calculation_extractor.invoke(
        [
            {
                "role": "system",
                "content": """
Extract calculation inputs from the user's request.

Do not perform the calculation.
Only extract values explicitly provided by the user.
""",
            },
            {
                "role": "user",
                "content": request,
            },
        ]
    )


def run_repository_branch(request: str) -> dict:
    """Run the repository inspection worker."""
    print("WORKFLOW: RUN REPOSITORY BRANCH")

    result = inspect_repository(request)

    print(f"REPOSITORY FILE: {result.relevant_file}")
    print(f"TAX RATE: {result.tax_rate}")

    return {
        "relevant_file": result.relevant_file,
        "tax_rate": result.tax_rate,
        "repository_explanation": result.explanation,
    }


def run_calculation_branch(
    request: str,
    context: dict,
) -> None:
    """Route calculations to deterministic Python execution."""
    print("WORKFLOW: RUN CALCULATION BRANCH")

    calculation_type = classify_calculation_type(request)

    print(
        "CALCULATION TYPE: "
        f"{calculation_type.calculation_type}"
    )

    if calculation_type.calculation_type == "GENERIC_ARITHMETIC":
        print("WORKFLOW: RUN GENERIC ARITHMETIC BRANCH")

        inputs = extract_arithmetic_inputs(request)

        print(f"LEFT: {inputs.left}")
        print(f"OPERATOR: {inputs.operator}")
        print(f"RIGHT: {inputs.right}")

        if inputs.operator == "+":
            result = inputs.left + inputs.right
        elif inputs.operator == "-":
            result = inputs.left - inputs.right
        elif inputs.operator == "*":
            result = inputs.left * inputs.right
        elif inputs.operator == "/":
            if inputs.right == 0:
                print("ERROR: Division by zero")
                return
            result = inputs.left / inputs.right
        else:
            raise ValueError("Unsupported operator")

        print(f"RESULT: {result}")
        return

    print("WORKFLOW: RUN PRICING CHECK BRANCH")

    inputs = extract_calculation_inputs(request)

    print(f"UNIT PRICE: {inputs.unit_price}")
    print(f"QUANTITY: {inputs.quantity}")
    print(f"CLAIMED TOTAL: {inputs.claimed_total}")

    tax_rate = context.get("tax_rate", 0.0)

    subtotal = inputs.unit_price * inputs.quantity
    total = subtotal * (1 + tax_rate)

    print(f"CALCULATED TOTAL: {total}")

    if inputs.claimed_total is not None:
        is_correct = abs(
            total - inputs.claimed_total
        ) < 0.01

        print(f"CLAIMED TOTAL CORRECT: {is_correct}")


def execute_workflow(
    request: str,
    decision: CapabilityDecision,
) -> None:
    """Execute required capabilities using code-controlled orchestration."""
    if decision.dangerous_action:
        print("WORKFLOW: BLOCK / REQUIRE HUMAN APPROVAL")
        return

    context = {}

    if decision.requires_repository:
        repository_result = run_repository_branch(request)
        context.update(repository_result)

    if decision.requires_calculation:
        run_calculation_branch(request, context)

    if decision.requires_general_knowledge:
        print("WORKFLOW: RUN GENERAL KNOWLEDGE BRANCH")


if __name__ == "__main__":
    requests = [
        "What is 4387 * 927?",
        "Find where calculate_total is implemented.",
        "Explain what Redis is.",
        "Delete the production database.",
        (
            "Check the pricing implementation and tell me whether "
            "charging $530 for four $125 items is correct."
        ),
    ]

    for request in requests:
        decision = classify_request(request)

        print(f"\nREQUEST: {request}")
        print(
            f"REPOSITORY:        {decision.requires_repository}"
        )
        print(
            f"CALCULATION:       {decision.requires_calculation}"
        )
        print(
            f"DANGEROUS:         {decision.dangerous_action}"
        )
        print(
            "GENERAL KNOWLEDGE: "
            f"{decision.requires_general_knowledge}"
        )
        print(f"REASON: {decision.reason}")

        execute_workflow(request, decision)