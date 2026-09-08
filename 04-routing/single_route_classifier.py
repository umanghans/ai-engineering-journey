from typing import Literal

from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    route: Literal[
        "CALCULATION",
        "REPOSITORY",
        "GENERAL_QUESTION",
        "DANGEROUS_ACTION",
    ] = Field(
        description="The single route that best represents the request."
    )

    reason: str = Field(
        description="Brief reason why this route was selected."
    )


model = ChatOllama(
    model="qwen2:7b",
    temperature=0,
)

router = model.with_structured_output(RouteDecision)


SYSTEM_PROMPT = """
You are a request router.

Classify the user's request into exactly one route:

CALCULATION:
Requests primarily requiring arithmetic.

REPOSITORY:
Requests requiring inspection or understanding of source code
or repository contents.

GENERAL_QUESTION:
General informational questions that do not require repository access.

DANGEROUS_ACTION:
Requests involving destructive or high-risk actions such as deleting
data, modifying production systems, or other consequential operations.

Choose the route that best represents the primary intent.
"""


def route_request(request: str) -> RouteDecision:
    """Classify a request into a single execution route."""
    return router.invoke(
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
        decision = route_request(request)

        print(f"\nREQUEST: {request}")
        print(f"ROUTE:   {decision.route}")
        print(f"REASON:  {decision.reason}")