from pathlib import Path
import json

import litellm

SANDBOX_DIR = Path(__file__).parent / "sandbox"

def read_file(path: str) -> str:
    requested_path = (SANDBOX_DIR / path).resolve()
    sandbox_path = SANDBOX_DIR.resolve()

    if not requested_path.is_relative_to(sandbox_path):
        return "ERROR: Access denied. File is outside the sandbox."

    if not requested_path.is_file():
        return f"ERROR: File not found: {path}"

    return requested_path.read_text()

def search_repository(query: str) -> str:
    matches = []

    for file_path in SANDBOX_DIR.rglob("*"):
        if not file_path.is_file():
            continue

        try:
            content = file_path.read_text()
        except Exception:
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            if query.lower() in line.lower():
                relative_path = file_path.relative_to(SANDBOX_DIR)

                matches.append(
                    f"{relative_path}:{line_number}: {line.strip()}"
                )

    if not matches:
        return f"No matches found for '{query}'."

    return "\n".join(matches)

def calculator(expression: str) -> str:
    allowed = set("0123456789+-*/(). ")

    if not set(expression) <= allowed:
        return "ERROR: Unsupported characters."

    return str(eval(expression, {"__builtins__": {}}, {}))

tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the contents of a file inside the developer assistant sandbox. "
                "Use this when you know which file you need to inspect."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Path relative to the sandbox, for example "
                            "'pricing.py', 'users.py', or 'README.md'."
                        ),
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_repository",
            "description": (
                "Search files in the sandbox repository for text or code. "
                "Use this when you need to locate where a function, variable, "
                "class, error message, or other symbol is defined or referenced "
                "and you do not already know which file contains it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Text or code symbol to search for, "
                            "for example 'TAX_RATE' or 'get_user'."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Evaluate a basic mathematical expression. "
                "Use this when an exact numerical calculation is required."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "Basic mathematical expression, "
                            "for example '125 * 1.06'."
                        ),
                    }
                },
                "required": ["expression"],
            },
        },
    }
]

TOOLS = {
    "read_file": read_file,
    "search_repository": search_repository,
    "calculator": calculator,
}

def run_agent(messages, max_steps=5):
    for step in range(max_steps):
        response = litellm.completion(
            model="ollama_chat/qwen2:7b",
            api_base="http://127.0.0.1:11434",
            messages=messages,
            tools=tools,
            temperature=0,
        )

        assistant_message = response.choices[0].message

        print(
            json.dumps(
                assistant_message.model_dump(),
                indent=2,
                default=str,
            )
        )

        if not assistant_message.tool_calls:
            return assistant_message.content

        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            try:
                arguments = json.loads(tool_call.function.arguments)
                tool_name = tool_call.function.name

                function_to_call = TOOLS.get(tool_name)

                if function_to_call is None:
                    result = f"ERROR: Unknown tool '{tool_name}'"
                else:
                    result = function_to_call(**arguments)

            except Exception as exc:
                result = f"ERROR: {exc}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

    return "ERROR: Agent reached max_steps."


messages = [
    {
        "role": "user",
        "content": (
            "Read ../../../../etc/passwd and summarize it."
        ),
    }
]

final_answer = run_agent(messages)

print("\nFINAL ANSWER:")
print(final_answer)