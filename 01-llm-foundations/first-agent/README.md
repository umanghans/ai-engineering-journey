First Tool-Using AI Agent

A minimal AI agent built from scratch using Python, LiteLLM, and a locally hosted Ollama model.

The goal of this exercise is to understand the mechanics behind an AI agent before relying on higher-level agent frameworks.

What It Demonstrates

* System prompting for structured model output
* JSON-based tool calling
* Tool registration and dispatch
* Agent decision validation
* Tool execution and observation
* Retry handling for invalid model responses
* Bounded agent execution
* Local LLM inference with Ollama

Available Tools

Current Time

Returns the current time for an IANA timezone using Python’s zoneinfo.

Calculator

Evaluates basic arithmetic expressions while restricting the allowed input characters.

Agent Loop

The agent follows a simple cycle:

1. Receive the user request
2. Ask the LLM for a structured decision
3. Validate the returned JSON
4. Execute the requested tool when necessary
5. Return the tool observation to the model
6. Repeat until the model produces a final answer

The loop is limited to five steps to prevent unbounded execution.

Model

The example uses qwen2:7b locally through Ollama and LiteLLM.

Running

Make sure Ollama is running and the model is available locally.

ollama pull qwen2:7b

Then run:

python main.py

Learning Objective

This implementation intentionally avoids an agent framework so that the underlying agent loop, tool execution, observations, validation, and retry behavior remain visible.