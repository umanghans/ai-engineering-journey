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