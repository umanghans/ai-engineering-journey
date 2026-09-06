System Prompt Comparison

An experiment demonstrating how system prompts influence the behavior and response style of an AI agent while using the same underlying language model.

What It Demonstrates

* System prompt design
* Controlling model behavior through instructions
* Creating agents with LangChain
* Comparing responses from the same model
* Separating model capability from agent behavior

Experiment

Two agents use the same qwen2:7b model with a temperature of 0.

The concise agent is instructed to answer software engineering questions in no more than two sentences.

The teacher agent is instructed to explain concepts carefully using examples and analogies.

Both agents receive the same question:

What is Redis?

Comparing their responses demonstrates how the system prompt can shape the behavior of an application without changing the underlying model.

Model

The experiment uses qwen2:7b locally through Ollama with LangChain.

Learning Objective

The purpose of this example is to understand the role of system prompts in defining an AI application’s behavior before moving into more complex agents with tools, state, and memory.