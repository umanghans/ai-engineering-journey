Models and Messages

A basic exploration of LangChain chat models, message objects, and conversation history using a locally hosted Ollama model.

What It Demonstrates

* Using ChatOllama as a LangChain chat model
* Creating structured HumanMessage objects
* Invoking a chat model with message history
* Preserving AI responses in the conversation
* Understanding how conversational context is maintained

Conversation History

LLMs do not automatically remember previous calls.

To maintain context, previous messages must be included when invoking the model again.

In this example, the user first tells the model that the project uses PostgreSQL. The resulting AI response is preserved in the message history before a follow-up question is asked.

This allows the model to answer the follow-up using information from the earlier conversation.

Model

The example uses qwen2:7b locally through Ollama with LangChain’s ChatOllama integration.

Learning Objective

The purpose of this example is to understand LangChain’s message-based conversation model before introducing higher-level concepts such as agents, checkpointing, and persistent memory.