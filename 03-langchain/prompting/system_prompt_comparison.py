from langchain.agents import create_agent
from langchain_ollama import ChatOllama


model = ChatOllama(
    model="qwen2:7b",
    temperature=0,
)

concise_agent = create_agent(
    model=model,
    tools=[],
    system_prompt=(
        "You are a concise software engineering assistant. "
        "Answer every question in no more than two sentences."
    ),
)

teacher_agent = create_agent(
    model=model,
    tools=[],
    system_prompt=(
        "You are a software engineering teacher. "
        "Explain concepts carefully using an example and an analogy."
    ),
)

question = {
    "messages": [
        {
            "role": "user",
            "content": "What is Redis?",
        }
    ]
}

concise_result = concise_agent.invoke(question)
teacher_result = teacher_agent.invoke(question)

print("\n=== CONCISE AGENT ===")
print(concise_result["messages"][-1].content)

print("\n=== TEACHER AGENT ===")
print(teacher_result["messages"][-1].content)