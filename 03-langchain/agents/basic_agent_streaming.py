from langchain.agents import create_agent
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


agent = create_agent(
    model=model,
    tools=[calculator],
)


for message_chunk, metadata in agent.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "What is 4387 multiplied by 927?",
            }
        ]
    },
    stream_mode="messages",
):
    print("\n--- MESSAGE CHUNK ---")
    print("TYPE:", type(message_chunk).__name__)
    print("NODE:", metadata.get("langgraph_node"))
    print("CONTENT:", repr(message_chunk.content))

    if hasattr(message_chunk, "tool_call_chunks"):
        print("TOOL CALL CHUNKS:", message_chunk.tool_call_chunks)