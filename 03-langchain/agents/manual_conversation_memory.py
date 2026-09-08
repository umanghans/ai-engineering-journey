from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage


model = ChatOllama(
    model="qwen2:7b",
    temperature=0,
)

agent = create_agent(
    model=model,
    tools=[],
    system_prompt=(
        "Answer concisely. "
        "Use facts stated earlier in the conversation. "
        "Do not give generic advice when the answer is already present "
        "in the conversation."
    ),
)


messages = [
    {
        "role": "user",
        "content": (
            "My project database is PostgreSQL. "
            "Remember this for this conversation."
        ),
    }
]

first_result = agent.invoke({
    "messages": messages
})

print("\n=== FIRST RESPONSE ===")
print(first_result["messages"][-1].content)


messages = first_result["messages"]

messages.append(
    HumanMessage(
        content="What database does my project use?"
    )
)


print("\n=== CONVERSATION HISTORY ===")

for index, message in enumerate(messages):
    print(f"\n--- MESSAGE {index} ---")
    print(type(message).__name__)
    print(message.content)


print("\n=== DIRECT MODEL RESPONSE ===")

direct_response = model.invoke(messages)
print(direct_response.content)


print("\n=== AGENT RESPONSE ===")

second_result = agent.invoke({
    "messages": messages
})

print(second_result["messages"][-1].content)