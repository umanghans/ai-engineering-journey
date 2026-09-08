from pathlib import Path

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama


BASE_DIR = Path(__file__).parent
SANDBOX_DIR = (BASE_DIR / "sandbox").resolve()


@tool
def read_file(path: str) -> str:
    """
    Read the full contents of a text file inside the sandbox directory.

    Use this after locating a relevant file with search_repository when
    implementation details are needed.
    """
    requested_path = (SANDBOX_DIR / path).resolve()

    if not requested_path.is_relative_to(SANDBOX_DIR):
        return "ERROR: Access denied. Path is outside the sandbox."

    if not requested_path.exists():
        return f"ERROR: File does not exist: {path}"

    if not requested_path.is_file():
        return f"ERROR: Path is not a file: {path}"

    try:
        return requested_path.read_text()
    except Exception as exc:
        return f"ERROR: Could not read file: {exc}"


@tool
def search_repository(query: str) -> str:
    """
    Search the sandbox repository for a symbol, function, constant,
    configuration value, or other text.

    Returns matching file names, line numbers, and matching lines.
    """
    matches = []

    for file_path in SANDBOX_DIR.rglob("*"):
        if not file_path.is_file():
            continue

        try:
            text = file_path.read_text()
        except Exception:
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            if query.lower() in line.lower():
                relative_path = file_path.relative_to(SANDBOX_DIR)
                matches.append(
                    f"{relative_path}:{line_number}: {line.strip()}"
                )

    if not matches:
        return f"No matches found for: {query}"

    return "\n".join(matches)


@tool
def calculator(expression: str) -> str:
    """Perform an exact basic numerical calculation."""
    allowed = set("0123456789+-*/(). ")

    if not set(expression) <= allowed:
        return "ERROR: Unsupported characters."

    try:
        return str(
            eval(
                expression,
                {"__builtins__": {}},
                {},
            )
        )
    except Exception as exc:
        return f"ERROR: Calculation failed: {exc}"


model = ChatOllama(
    model="qwen2:7b",
    temperature=0,
)

agent = create_agent(
    model=model,
    tools=[
        read_file,
        search_repository,
        calculator,
    ],
    system_prompt="""
You are a developer assistant working with a small local code repository.

Use the available tools when the user's question depends on repository
contents or exact arithmetic.

Rules:
- Do not invent repository contents.
- Search the repository when you do not know which file contains something.
- Read the relevant file before explaining implementation details.
- If a tool returns an error, use that observation to decide what to do next.
- Never claim you inspected a file unless you actually used a repository tool.
- Answer concisely after gathering enough evidence.
""",
)


def ask_agent(prompt: str) -> str:
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        }
    )

    print("\n=== AGENT TRACE ===")

    for index, message in enumerate(result["messages"]):
        print(f"\n--- MESSAGE {index} ---")
        print(type(message).__name__)
        print(message)

    return result["messages"][-1].content


if __name__ == "__main__":
    answer = ask_agent(
        "Find the TAX_RATE in the repository and calculate the total cost "
        "for 4 items priced at $125 each, including that tax."
    )

    print("\n=== FINAL ANSWER ===")
    print(answer)