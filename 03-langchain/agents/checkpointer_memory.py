from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver


model = ChatOllama(
    model="qwen2:7b",
    temperature=0,
)

checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    tools=[],
    system_prompt=(
        "Answer concisely. "
        "Use facts stated earlier in the conversation."
    ),
    checkpointer=checkpointer,
)


primary_thread = {
    "configurable": {
        "thread_id": "conversation-1"
    }
}

secondary_thread = {
    "configurable": {
        "thread_id": "conversation-2"
    }
}


first_result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "My project database is PostgreSQL.",
            }
        ]
    },
    config=primary_thread,
)

print("\n=== FIRST RESPONSE ===")
print(first_result["messages"][-1].content)


second_result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What database does my project use?",
            }
        ]
    },
    config=primary_thread,
)

print("\n=== SAME THREAD ===")
print(second_result["messages"][-1].content)


third_result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What database does my project use?",
            }
        ]
    },
    config=secondary_thread,
)

print("\n=== DIFFERENT THREAD ===")
print(third_result["messages"][-1].content)


print("\n=== MESSAGES IN DIFFERENT THREAD ===")

for index, message in enumerate(third_result["messages"]):
    print(f"\n--- MESSAGE {index} ---")
    print(type(message).__name__)
    print(message.content)