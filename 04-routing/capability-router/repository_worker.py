from pathlib import Path

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field


SANDBOX = (Path(__file__).parent / "sandbox").resolve()


@tool
def search_repository(query: str) -> str:
    """
    Search repository filenames and file contents.

    Multiple search words are treated independently.
    Spaces and underscores are considered equivalent.
    Returns matches containing any meaningful search term.
    """
    matches = []

    terms = [
        term.strip("*").lower()
        for term in query.replace("_", " ").split()
        if term.strip("*")
    ]

    for path in SANDBOX.rglob("*"):
        if not path.is_file():
            continue

        relative_path = path.relative_to(SANDBOX)
        normalized_path = str(relative_path).lower().replace("_", " ")

        if any(term in normalized_path for term in terms):
            matches.append(
                f"{relative_path}: filename/path match"
            )

        try:
            content = path.read_text()
        except (UnicodeDecodeError, PermissionError):
            continue

        for line_number, line in enumerate(
            content.splitlines(),
            start=1,
        ):
            normalized_line = line.lower().replace("_", " ")

            if any(term in normalized_line for term in terms):
                matches.append(
                    f"{relative_path}:{line_number}: {line.strip()}"
                )

    if not matches:
        return "No matches found."

    return "\n".join(matches)


@tool
def read_file(path: str) -> str:
    """Read the complete contents of a repository file."""
    requested_path = (SANDBOX / path).resolve()

    if not requested_path.is_relative_to(SANDBOX):
        return "ERROR: Access denied."

    if not requested_path.is_file():
        return f"ERROR: File does not exist: {path}"

    try:
        return requested_path.read_text()
    except Exception as exc:
        return f"ERROR: Could not read file: {exc}"


class RepositoryResult(BaseModel):
    relevant_file: str = Field(
        description="Repository file containing the relevant implementation."
    )

    tax_rate: float | None = Field(
        description="Tax rate found in the implementation, if relevant."
    )

    explanation: str = Field(
        description="Brief explanation of what was found."
    )


model = ChatOllama(
    model="qwen2:7b",
    temperature=0,
)

repository_agent = create_agent(
    model=model,
    tools=[
        search_repository,
        read_file,
    ],
    system_prompt="""
You are a repository inspection worker.

Your job is to inspect repository contents and return grounded information.

Rules:
- Never invent repository contents.
- Use search_repository to locate relevant code.
- Read the complete relevant file before describing its implementation.
- Extract the tax rate if it is relevant to the request.
- Return only information supported by repository inspection.
""",
)


structured_model = model.with_structured_output(RepositoryResult)


def inspect_repository(request: str) -> RepositoryResult:
    """Inspect the repository and return structured findings."""
    result = repository_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": request,
                }
            ]
        }
    )

    final_message = result["messages"][-1].content

    return structured_model.invoke(
        [
            {
                "role": "system",
                "content": """
Convert the repository inspection result into the required structured format.

Do not invent information.
Use only information present in the inspection result.
""",
            },
            {
                "role": "user",
                "content": final_message,
            },
        ]
    )


if __name__ == "__main__":
    result = inspect_repository(
        "Check the pricing implementation and determine the tax rate."
    )

    print(result.model_dump())