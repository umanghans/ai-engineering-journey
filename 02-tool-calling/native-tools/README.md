Native Tool Calling

An AI agent that uses native LLM tool calling with LiteLLM and a locally hosted Ollama model.

This example builds on the earlier manually orchestrated agent by allowing the model to return structured tool calls through the model API instead of requiring tool requests to follow a custom JSON response format.

What It Demonstrates

* Native LLM tool calling
* JSON Schema tool definitions
* Multiple tool calls within a single request
* Dynamic tool dispatch
* Tool result messages
* Multi-step agent execution
* Local LLM inference with Ollama

Available Tools

Calculator

Evaluates basic mathematical expressions.

Current Time

Returns the current time for an IANA timezone such as Asia/Tokyo or America/New_York.

How It Works

The agent sends the available tool definitions to the model along with the conversation.

When the model requests a tool:

1. The requested tool and arguments are extracted.
2. The corresponding Python function is executed.
3. The result is added to the conversation as a tool message.
4. The updated conversation is sent back to the model.
5. The process continues until the model produces a final response.

The agent also supports multiple tool calls, allowing a request such as finding the current time in Tokyo and performing a calculation to be handled within the same interaction.

Model

The example uses qwen2:7b locally through Ollama and LiteLLM.

Learning Objective

The purpose of this example is to understand the transition from manually implementing a tool-calling protocol to using the structured tool-calling capabilities provided by modern LLM APIs.