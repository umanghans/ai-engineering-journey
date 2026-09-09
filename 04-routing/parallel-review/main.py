from concurrent.futures import ThreadPoolExecutor

from langchain_ollama import ChatOllama


model = ChatOllama(
    model="qwen3:8b",
    temperature=0,
)


CODE = """
def calculate_discount(price, discount):
    return price - discount
"""


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


def review_code(role: str, instructions: str) -> str:
    """Run one specialized code review."""
    response = model.invoke(
        [
            {
                "role": "system",
                "content": (
                    f"You are a {role} code reviewer. "
                    f"{instructions} "
                    "Focus only on your assigned responsibility."
                ),
            },
            {
                "role": "user",
                "content": f"Review this code:\n\n{CODE}",
            },
        ]
    )

    return response.content


def run_parallel_reviews() -> dict[str, str]:
    """Run independent specialized reviewers concurrently."""
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

        return {
            name: future.result()
            for name, future in futures.items()
        }


def synthesize_reviews(reviews: dict[str, str]) -> str:
    """Evaluate and synthesize the specialized reviews."""
    combined_reviews = "\n\n".join(
        f"=== {name.upper()} REVIEW ===\n{review}"
        for name, review in reviews.items()
    )

    response = model.invoke(
        [
            {
                "role": "system",
                "content": """
You are a senior code reviewer.

You will receive:
1. The original code.
2. Reviews from multiple specialized reviewers.

Produce one concise final review.

Rules:
- Identify important findings supported by the reviews.
- Evaluate each finding against the original code before including it.
- Reject findings that describe behavior the code already handles correctly.
- Distinguish actual defects from optional business rules or design preferences.
- Remove duplicate or overlapping findings.
- Point out conflicting or questionable reviewer claims.
- Prioritize concrete correctness issues over speculative improvements.
- Do not invent issues that were not raised by the reviewers.
""",
            },
            {
                "role": "user",
                "content": (
                    f"ORIGINAL CODE:\n\n{CODE}\n\n"
                    f"SPECIALIZED REVIEWS:\n\n{combined_reviews}"
                ),
            },
        ]
    )

    return response.content


if __name__ == "__main__":
    reviews = run_parallel_reviews()

    for reviewer, review in reviews.items():
        print(f"\n=== {reviewer.upper()} ===")
        print(review)

    final_review = synthesize_reviews(reviews)

    print("\n=== FINAL SYNTHESIZED REVIEW ===")
    print(final_review)