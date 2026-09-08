# Basic Agent Streaming

This example demonstrates a LangChain agent that can automatically decide when to call a tool and stream the intermediate messages produced during execution.

The agent uses a local Ollama model and a calculator tool.

## What This Demonstrates

- Creating a tool with LangChain's `@tool` decorator
- Creating an agent with `create_agent()`
- Giving the agent access to a calculator tool
- Allowing the agent to decide when a tool is required
- Streaming agent execution with `agent.stream()`
- Inspecting intermediate model and tool-related message chunks
- Viewing the LangGraph node responsible for each streamed message

## How It Works

The user asks the model to calculate:

```text
4387 * 927

## Checkpointer Memory

`checkpointer_memory.py` demonstrates how LangChain agents can preserve conversation state between separate invocations using a LangGraph checkpointer.

Instead of manually passing the entire previous message history into each call, the agent stores conversation state using an `InMemorySaver`.

### What This Demonstrates

- Using `InMemorySaver` as an agent checkpointer
- Preserving conversation history across separate `agent.invoke()` calls
- Identifying conversations with `thread_id`
- Keeping multiple conversation threads isolated
- Retrieving previously stated information without manually rebuilding message history
- Inspecting the messages stored for a particular thread

### Thread Isolation

The example creates two conversation threads.

The first thread is told:

```text
My project database is PostgreSQL.