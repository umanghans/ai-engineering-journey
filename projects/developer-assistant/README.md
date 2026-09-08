# Developer Assistant

A repository-aware AI developer assistant built with Python, LiteLLM, LangChain, and a locally hosted Ollama model.

The assistant can inspect files, search a repository for code or configuration values, perform calculations, and combine information from multiple tool calls to answer developer questions.

The project contains both a manually orchestrated implementation and a LangChain-based implementation, making it possible to compare the underlying agent mechanics with a higher-level agent framework.

## What It Demonstrates

- LLM tool calling
- Multi-step agent execution
- Repository search
- File inspection
- Dynamic tool dispatch
- Tool result handling
- Filesystem sandboxing
- Path traversal protection
- Local LLM inference with Ollama
- LangChain tools and agent orchestration

## Available Tools

### `search_repository`

Searches files within the sandbox repository for a string or code symbol and returns matching files, line numbers, and content.

Example use cases:

- Locate a constant such as `TAX_RATE`
- Find where a function is defined
- Search for configuration values
- Locate references to a class or variable

### `read_file`

Reads a file from the sandbox when the assistant knows which file it needs to inspect.

The tool resolves the requested path and verifies that it remains inside the sandbox before allowing access.

### `calculator`

Evaluates basic mathematical expressions when the assistant needs an exact numerical result.

## How It Works

The assistant receives a developer question and determines which tools are required.

For example, a request could ask the assistant to locate a tax rate in the repository and calculate the total price of several items.

The agent can:

1. Search the repository for the relevant configuration.
2. Inspect the appropriate file if additional context is required.
3. Perform the calculation using the calculator tool.
4. Return the final answer.

Tool results are added back to the conversation, allowing the model to reason across multiple steps.

## Security

Repository access is restricted to a dedicated sandbox directory.

File paths are resolved before access and checked against the sandbox root. Requests attempting to escape the sandbox, such as accessing files through `../`, are rejected.

This prevents the model from using the file-reading tool to access arbitrary files on the host system.

## Model

The current implementations use `qwen2:7b` locally through Ollama.

The original implementation communicates with the model through LiteLLM, while the LangChain implementation uses `ChatOllama`.

## Learning Objective

This project explores how an AI agent can interact safely with a codebase rather than relying solely on information contained in the model's context.

It also demonstrates the progression from implementing the mechanics of an agent loop directly to expressing the same behavior through a higher-level agent framework.

## LangChain Version

`langchain_agent.py` rebuilds the developer assistant using LangChain's `create_agent()` abstraction.

The original `agent.py` implements the tool-calling loop directly using LiteLLM. The LangChain version keeps the same core capabilities while delegating agent orchestration and tool execution flow to LangChain.

### What This Adds

- LangChain `@tool` definitions
- Agent creation with `create_agent()`
- Framework-managed tool selection and execution
- Multi-step repository inspection
- Full agent execution trace inspection
- The same filesystem sandbox and path traversal protection

### Agent Workflow

A repository-dependent request can follow a workflow such as:

```text
User Request
    ↓
Agent
    ↓
search_repository
    ↓
read_file
    ↓
calculator
    ↓
Agent
    ↓
Final Answer
```

The exact sequence is determined by the agent. It may use only the tools required for a particular request.

For example, the agent can locate a repository constant such as `TAX_RATE`, inspect the relevant source file, use that value in a calculation, and return the resulting answer.

## Manual vs LangChain Implementation

The project contains two implementations of the developer assistant:

```text
agent.py
    ↓
LiteLLM native tool calling
    ↓
Application manually manages the agent loop

langchain_agent.py
    ↓
LangChain tools + create_agent()
    ↓
Framework manages the agent loop
```

Building both versions demonstrates the abstraction LangChain provides rather than treating the framework as a black box.

The first implementation exposes the mechanics of tool calling, tool execution, observations, and repeated model calls directly.

The second implementation expresses the same agent behavior through higher-level LangChain abstractions.

## Sandbox Repository

The `sandbox/` directory contains a small sample codebase used to test the assistant's repository search and file-reading capabilities.

```text
sandbox/
├── README.md
├── pricing.py
└── users.py