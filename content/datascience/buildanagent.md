---
title: "I Built My Own AI Agent with GPT-4 (And You Can Too)"
date: 2024-03-29
draft: false
---

# Building a Simple Agentic AI with GPT-4: A Hands-On Guide

> I've been experimenting lightweight AI agents, so I threw together a very basic starter guide to get you on your way. This uses OpenAI GPT API and a few simple packages.

## What Is an Agentic AI, Anyway?

Think of it as the difference between:
- A calculator that gives you an answer when you type in a formula
- An assistant that notices you're trying to budget for a trip, suggests calculations you hadn't thought of, and then helps you book the flights

The agent I'll show you how to build is pretty simple, but it follows the same principles as those cutting-edge systems making headlines:

1. It takes in a goal from you (the human)
2. Figures out a plan to achieve that goal
3. Uses tools (APIs, functions, etc.) to actually DO things
4. Reports back with results and explains its process

You can build this in about 50 lines of Python code.

## What You'll Need

- Python 3.8 or newer
- An OpenAI API key (I'm using GPT-4, but you could try with 3.5)
- The `openai` Python package
- Optionally, the `rich` package for prettier console output

I'm assuming you know basic Python. If you don't, this might be a bit challenging, but you can still follow along.

## Step 1: Setup

First, let's get our environment ready:

```python
pip install openai rich
```

Then we need to set up our OpenAI key:

```python
import openai
openai.api_key = "your-api-key-here"  # Or better yet, use environment variables!
```

## Step 2: Give Your Agent Some Tools

Here's where things get interesting. An agent without tools is just a chatbot. The tools are what allow it to actually *do* things.

Let's start with a couple of simple ones:

```python
def search_todos(query):
    # In a real app, this might query a database or file
    todos = ["Buy milk", "Call mom", "Finish blog post", "Book dentist appointment"]
    return [todo for todo in todos if query.lower() in todo.lower()]

def simple_calculator(expression):
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {str(e)}"
```

Now we need to register these tools so our agent knows about them:

```python
TOOLS = {
    "search_todos": {
        "function": search_todos,
        "description": "Searches the to-do list. Input should be a keyword."
    },
    "simple_calculator": {
        "function": simple_calculator,
        "description": "Evaluates a math expression. Input should be a valid Python expression."
    }
}
```

I've kept it simple here, but you could add tools for checking the weather, sending emails, or even controlling smart home devices!

## Step 3: Build the Agent's Brain

This is where the magic happens. We'll create a loop that:
1. Asks GPT-4 what to do next
2. Executes the tool it chooses
3. Feeds the result back to GPT-4
4. Repeats until the goal is achieved

```python
from rich import print
import json

def run_agent(goal):
    messages = [
        {"role": "system", "content": "You're an AI agent that can complete tasks by calling tools. Think step-by-step."},
        {"role": "user", "content": f"My goal is: {goal}"}
    ]

    while True:
        print("\n[bold yellow]Thinking...[/bold yellow]")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            functions=[
                {
                    "name": name,
                    "description": meta["description"],
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "input": {"type": "string", "description": "Input for the function"}
                        },
                        "required": ["input"]
                    }
                }
                for name, meta in TOOLS.items()
            ],
            function_call="auto"
        )

        reply = response['choices'][0]['message']
        messages.append(reply)

        if reply.get("function_call"):
            tool_name = reply["function_call"]["name"]
            tool_input = json.loads(reply["function_call"]["arguments"])["input"]

            print(f"[green]Calling tool: {tool_name}('{tool_input}')[/green]")
            result = TOOLS[tool_name]["function"](tool_input)

            messages.append({
                "role": "function",
                "name": tool_name,
                "content": result
            })
        else:
            print("[bold cyan]Agent reply:[/bold cyan]", reply["content"])
            break
```

What's happening here? We're creating a conversation with GPT-4 and telling it about our tools. When GPT-4 decides to use a tool, we actually run the corresponding Python function and feed the result back into the conversation.

It's like having GPT-4 as the "brain" while your Python functions are its "hands" to interact with the world.

## Step 4: Let's Take It for a Spin!

Now for the fun part—let's run our agent:

```python
if __name__ == "__main__":
    goal = input("What's your goal? ")
    run_agent(goal)
```

Try it with these goals:

- "What math homework do I still need to do?"
- "Search my to-dos for anything related to appointments"
- "What is 42 * (2 + 3)?"

When I ran "Search for any appointments in my todos," I got:

```
Thinking...
Calling tool: search_todos('appointment')
Agent reply: I found 1 to-do item related to appointments:
- "Book dentist appointment"
```

And for "Calculate the area of a circle with radius 5":

```
Thinking...
Calling tool: simple_calculator('3.14159 * 5 * 5')
Agent reply: The area of a circle with radius 5 is 78.53975 square units.
(Using π ≈ 3.14159 and the formula area = π * r²)
```

## What's Really Going On Here?

What makes this different from a regular chatbot?

1. **It can take actions**: Our agent doesn't just talk about doing things—it actually executes Python functions.
2. **It chains reasoning**: If you give it a complex goal, it will break it down and use multiple tools to solve it.
3. **It adapts**: If a tool returns unexpected results, the agent will adjust its plan.

The coolest part is watching it decide which tool to use and how to interpret the results. Sometimes it might surprise you with its creativity!

## Where to Go From Here

This simple agent is just the beginning. Here's how you could take it further:

- **Add internet access**: Integrate with search APIs or web scraping tools
- **Connect to your digital life**: Give it access to your calendar, email, or task management systems
- **Add memory**: Let it remember past conversations and tasks
- **Make it proactive**: Run it on a schedule to check for important updates

For the more technically adventurous, you could even:
- Host it as an API using FastAPI
- Add authentication so only you can access it
- Create a web interface instead of using the console

## The Real Magic of Agentic AI

I've been playing with this simple agent for weeks now, and what fascinates me most is how it feels more like a colleague than a tool. When I ask it to research something, it doesn't just dump information—it organizes its approach, follows leads, and compiles results in a way that feels... well, human.

The line between "using a tool" and "delegating to an assistant" gets blurry fast. And that's what makes agentic AI so powerful. It's not just about automation—it's about collaboration with an entity that can think.

With just a few dozen lines of code and the right hooks into your digital world, you can build an assistant that actually gets stuff done.

What would you delegate to your agent?