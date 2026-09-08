# LangChain Agents

A collection of examples exploring LangChain's agent abstractions, streaming execution, conversation context, and checkpoint-based state management.

These examples build on the earlier manual tool-calling implementations by using LangChain and LangGraph to manage increasingly sophisticated agent workflows.

## Examples

### Basic Agent Streaming

`basic_agent_streaming.py` demonstrates a LangChain agent that can automatically decide when to call a tool and stream the intermediate messages produced during execution.

The agent uses a local Ollama model and a calculator tool.

#### What This Demonstrates

- Creating tools with LangChain's `@tool` decorator
- Creating an agent with `create_agent()`
- Allowing the agent to decide when a tool is required
- Streaming execution with `agent.stream()`
- Inspecting model and tool-related message chunks
- Viewing the LangGraph node responsible for streamed messages

#### How It Works

The user asks:

```text
4387 * 927
```

The agent determines that an exact calculation should use the calculator tool.

Conceptually:

```text
User Request
    ↓
Agent
    ↓
Tool Call
    ↓
Calculator
    ↓
Tool Result
    ↓
Agent
    ↓
Final Answer
```

Unlike the earlier manual tool execution example, `create_agent()` manages the tool-calling loop while `agent.stream()` exposes the intermediate execution.

This provides the foundation for applications that display agent progress and tool activity in real time.

---

### Manual Conversation Memory

`manual_conversation_memory.py` demonstrates how conversation context can be preserved by explicitly passing previous messages into later model or agent calls.

LLMs and agents do not automatically remember independent invocations unless previous context is supplied or state is persisted externally.

#### What This Demonstrates

- Maintaining conversation history manually
- Preserving user and AI messages between calls
- Passing accumulated messages into later agent invocations
- Sending the same conversation history directly to the model
- Comparing direct model invocation with agent invocation
- Understanding the distinction between context and persistent memory

#### How It Works

The first conversation turn tells the agent:

```text
My project database is PostgreSQL.
```

The completed conversation history is preserved and another user message is added:

```text
What database does my project use?
```

The full history is then supplied to the next invocation:

```text
First User Message
        ↓
Agent Response
        ↓
Preserve Message History
        ↓
Append Second User Message
        ↓
Pass Full History
        ↓
Agent
        ↓
PostgreSQL
```

The agent can answer correctly because the PostgreSQL statement remains in the context supplied to the model.

---

### Checkpointer Memory

`checkpointer_memory.py` demonstrates how conversation state can be maintained across separate agent invocations using a LangGraph checkpointer.

Instead of manually passing the complete conversation history into every call, the agent uses an `InMemorySaver` to store state associated with a conversation thread.

#### What This Demonstrates

- Using `InMemorySaver` as an agent checkpointer
- Preserving state across separate `agent.invoke()` calls
- Identifying conversations with `thread_id`
- Keeping independent conversation threads isolated
- Restoring previous context automatically
- Inspecting messages associated with a thread

#### Thread Isolation

The first conversation thread is told:

```text
My project database is PostgreSQL.
```

A later invocation using the same `thread_id` asks:

```text
What database does my project use?
```

The checkpointer restores the earlier conversation state, allowing the agent to answer:

```text
PostgreSQL
```

A second thread asks the same question without receiving the earlier database information.

Because it uses a different `thread_id`, the conversation state is isolated.

Conceptually:

```text
Thread 1
    ↓
"My database is PostgreSQL"
    ↓
Checkpointer stores state
    ↓
Same thread asks about database
    ↓
State restored
    ↓
PostgreSQL


Thread 2
    ↓
Asks about database
    ↓
No previous database context
```

`InMemorySaver` stores checkpoints only within the current Python process. Persistent applications would typically use durable checkpoint storage.

## Manual History vs Checkpointer

The two memory examples demonstrate different approaches to maintaining conversational state.

```text
Manual Conversation History

Application
    ↓
Stores messages
    ↓
Passes complete history
    ↓
Agent / Model


Checkpointer

thread_id
    ↓
Checkpointer
    ↓
Restores stored state
    ↓
Agent
```

Manual history makes the model's context explicit and helps demonstrate what is actually being sent with each invocation.

Checkpointers provide a structured mechanism for managing conversation state across calls and separating multiple conversation threads.

## Model

All examples currently use:

```text
qwen2:7b
```

running locally through Ollama.

## Learning Progression

The examples in this directory represent a progression in agent orchestration:

```text
Basic Agent
    ↓
Automatic Tool Execution
    ↓
Streaming Agent Execution
    ↓
Manual Conversation Context
    ↓
Checkpointed Conversation State
```

Together, they establish the core concepts needed for building stateful, tool-using agent applications with LangChain and LangGraph.