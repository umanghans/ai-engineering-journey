Manual Tool Execution

A small LangChain example showing the full lifecycle of a tool call without using a higher-level agent abstraction.

What It Demonstrates

* Defining tools with LangChain’s @tool decorator
* Binding tools to a chat model
* Inspecting model-generated tool calls
* Executing the requested tool manually
* Creating ToolMessage observations
* Returning tool results to the model
* Producing a final response after tool execution

Flow

The example follows this sequence:

1. The user asks a question that requires calculation.
2. The model decides to call the calculator tool.
3. The runtime extracts the requested tool call.
4. The calculator is executed.
5. The result is wrapped in a ToolMessage.
6. The updated conversation is sent back to the model.
7. The model produces the final answer.

Why This Matters

Higher-level agent frameworks automate this process, but understanding the manual flow makes it easier to reason about agent behavior, debugging, and tool integration.

Model

The example uses qwen2:7b locally through Ollama with LangChain’s ChatOllama integration.

Learning Objective

The purpose of this example is to understand how LangChain represents and executes tool calls before moving on to agent abstractions that manage the loop automatically.