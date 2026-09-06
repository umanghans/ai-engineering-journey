from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama


model = ChatOllama(
    model="qwen2:7b",
    temperature=0,
)

messages = [
    HumanMessage(
        content="For this conversation, my project database is PostgreSQL."
    )
]

first_response = model.invoke(messages)

print("FIRST RESPONSE:")
print(first_response.content)

messages.append(first_response)

messages.append(
    HumanMessage(
        content="What database does my project use?"
    )
)

second_response = model.invoke(messages)

print("\nSECOND RESPONSE:")
print(second_response.content)