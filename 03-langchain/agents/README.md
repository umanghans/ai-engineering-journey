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

## Manual Conversation Memory

`manual_conversation_memory.py` demonstrates how conversation context can be preserved by explicitly passing previous messages back into later model or agent calls.

LLMs and agents do not automatically remember separate invocations unless conversation state is supplied or persisted externally.

### What This Demonstrates

- Maintaining conversation history manually
- Preserving both user and AI messages between calls
- Passing accumulated messages into a later agent invocation
- Sending the same conversation history directly to the underlying model
- Comparing direct model invocation with agent invocation
- Understanding the difference between model context and persistent memory

### How It Works

The first conversation turn tells the agent:

```text
My project database is PostgreSQL.

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