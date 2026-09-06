from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama


@tool
def calculator(expression: str) -> str:
    """Perform an exact basic numerical calculation."""
    allowed = set("0123456789+-*/(). ")

    if not set(expression) <= allowed:
        return "ERROR: Unsupported characters."

    return str(eval(expression, {"__builtins__": {}}, {}))


model = ChatOllama(
    model="qwen2:7b",
    temperature=0,
)

model_with_tools = model.bind_tools([calculator])

messages = [
    HumanMessage(
        content="What is 4387 multiplied by 927?"
    )
]

ai_message = model_with_tools.invoke(messages)
messages.append(ai_message)

print("MODEL REQUEST:")
print(ai_message.tool_calls)

tool_call = ai_message.tool_calls[0]

result = calculator.invoke(
    tool_call["args"]
)

print("\nTOOL RESULT:")
print(result)

tool_message = ToolMessage(
    content=str(result),
    tool_call_id=tool_call["id"],
)

messages.append(tool_message)

final_response = model_with_tools.invoke(messages)

print("\nFINAL RESPONSE:")
print(final_response.content)