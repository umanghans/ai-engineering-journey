Developer Assistant

A repository-aware AI developer assistant built with Python, LiteLLM, and a locally hosted Ollama model.

The assistant can inspect files, search a repository for code or configuration values, perform calculations, and combine information from multiple tool calls to answer developer questions.

What It Demonstrates

* LLM tool calling
* Multi-step agent execution
* Repository search
* File inspection
* Dynamic tool dispatch
* Tool result handling
* Filesystem sandboxing
* Path traversal protection
* Local LLM inference with Ollama

Available Tools

search_repository

Searches files within the sandbox repository for a string or code symbol and returns matching files, line numbers, and content.

Example use cases:

* Locate a constant such as TAX_RATE
* Find where a function is defined
* Search for configuration values
* Locate references to a class or variable

read_file

Reads a file from the sandbox when the assistant knows which file it needs to inspect.

The tool resolves the requested path and verifies that it remains inside the sandbox before allowing access.

calculator

Evaluates basic mathematical expressions when the assistant needs an exact numerical result.

How It Works

The assistant receives a developer question and determines which tools are required.

For example, a request could ask the assistant to locate a tax rate in the repository and calculate the total price of several items.

The agent can:

1. Search the repository for the relevant configuration.
2. Inspect the appropriate file if additional context is required.
3. Perform the calculation using the calculator tool.
4. Return the final answer.

Tool results are added back to the conversation, allowing the model to reason across multiple steps.

Security

Repository access is restricted to a dedicated sandbox directory.

File paths are resolved before access and checked against the sandbox root. Requests attempting to escape the sandbox, such as accessing files through ../, are rejected.

This prevents the model from using the file-reading tool to access arbitrary files on the host system.

Model

The current implementation uses qwen2:7b locally through Ollama and LiteLLM.

Learning Objective

This project explores how an AI agent can interact safely with a codebase rather than relying solely on information contained in the model’s context.

It also serves as a foundation for progressively adding more capable developer tools and rebuilding the assistant with higher-level agent frameworks.