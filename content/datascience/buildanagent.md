---
title: "I Built My Own AI Agent with GPT-4 (And You Can Too)"
date: 2025-03-29T02:59:30Z
draft: false
categories: ["AI", "AgenticAI", "Guide"]
tags: ["AI Agent", "AI"]
description: "Building a Quick and Dirty AI Agent"
---

# Build Your First AI Agent That Actually Does Stuff

*From chatbot to digital assistant in 50 lines of Python*

---

I've been messing around with AI agents for the past few weeks, and honestly, it's addictive. Started as curiosity about "what's beyond ChatGPT" and turned into building little digital helpers that can actually get work done.

Most people think AI agents are either science fiction or require a PhD to build. Neither is true. You can create something genuinely useful in an afternoon with basic Python skills.

---

## Agent vs Chatbot: The Difference That Matters

**Regular chatbot:** "What's 2+2?"  
*"It's 4!"*

**AI agent:** "Help me budget for my vacation"  
*"I'll calculate your available funds, research flight costs, suggest a daily budget, and can book the flights when you're ready."*

The agent I'm about to show you:
- Takes your goal
- Makes a plan
- Uses actual tools to get things done  
- Reports back with results

Basic? Yes. But it follows the same pattern as those million-dollar enterprise systems.

---

## What You Need

- Python 3.8+
- OpenAI API key (GPT-4 works best, 3.5 is okay)
- Two packages: `openai` and `rich`

That's it. No complicated frameworks or cloud deployments.

```bash
pip install openai rich
```

---

## Step 1: Give Your Agent Some Hands

An agent without tools is just an expensive chatbot. Let's start simple:

```python
def search_todos(query):
    # Fake database for demo
    todos = ["Buy milk", "Call mom", "Finish blog post", "Book dentist appointment"]
    return [todo for todo in todos if query.lower() in todo.lower()]

def simple_calculator(expression):
    try:
        return str(eval(expression))  # Don't do this in production!
    except Exception as e:
        return f"Error: {str(e)}"
```

Now register them:

```python
TOOLS = {
    "search_todos": {
        "function": search_todos,
        "description": "Searches the to-do list. Input should be a keyword."
    },
    "simple_calculator": {
        "function": simple_calculator,
        "description": "Evaluates math expressions."
    }
}
```

**Real talk:** These are toy examples. In practice, you'd connect to actual APIs, databases, or services.

---

## Step 2: The Agent Brain

Here's where it gets interesting. We create a loop where GPT-4 decides what to do, we execute it, and feed the results back:

```python
import openai
import json
from rich import print

def run_agent(goal):
    messages = [
        {"role": "system", "content": "You're an AI agent that completes tasks using tools. Think step-by-step."},
        {"role": "user", "content": f"My goal: {goal}"}
    ]

    while True:
        print("\n[yellow]Thinking...[/yellow]")
        
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
                            "input": {"type": "string"}
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
            # Agent chose to use a tool
            tool_name = reply["function_call"]["name"]
            tool_input = json.loads(reply["function_call"]["arguments"])["input"]

            print(f"[green]Using: {tool_name}('{tool_input}')[/green]")
            result = TOOLS[tool_name]["function"](tool_input)

            # Feed result back to agent
            messages.append({
                "role": "function",
                "name": tool_name,
                "content": result
            })
        else:
            # Agent is done
            print("[cyan]Result:[/cyan]", reply["content"])
            break
```

**What's happening:** GPT-4 acts as the "brain" deciding what to do. Your Python functions are its "hands" that actually do things.

---

## Step 3: Take It for a Test Drive

```python
if __name__ == "__main__":
    openai.api_key = "your-api-key-here"  # Use environment variables!
    goal = input("What's your goal? ")
    run_agent(goal)
```

**Try these:**
- "What appointments do I have coming up?"
- "Calculate compound interest on $1000 at 5% for 3 years"
- "Find anything in my todos about family"

**Example run:**
```
Goal: Search for any appointments in my todos
Thinking...
Using: search_todos('appointment')
Result: I found 1 appointment-related item:
- "Book dentist appointment"

You should probably schedule that dentist visit!
```

---

## Why This is Actually Cool

### It Chains Actions
Give it a complex goal and watch it break things down:

"Calculate my monthly budget and find related todos" becomes:
1. Use calculator for budget math
2. Search todos for financial items
3. Combine and present results

### It Adapts
If a tool returns unexpected results, the agent adjusts. No rigid scripting.

### It Explains Itself
You can see exactly what it's doing and why. Full transparency.

---

## Level Up Ideas

**Connect to real services:**
- Weather APIs
- Your calendar
- Email or Slack
- Smart home devices

**Add memory:**
- Store past conversations
- Remember your preferences
- Build context over time

**Go proactive:**
- Run on a schedule
- Send you daily summaries
- Alert about important changes

**Get fancy:**
- Web interface with Flask/FastAPI
- Voice commands
- Mobile app integration

---

## The Breakthrough Moment

After playing with this for a few days, something clicked. This isn't just automation - it's delegation to something that can actually think through problems.

I asked it to "help me prep for my Monday meetings" and watched it:
1. Search my todos for meeting-related items
2. Calculate how much time I had available
3. Suggest a preparation schedule
4. Offer to set reminders

It felt less like using a tool and more like working with a really efficient intern.

**That's the magic of agentic AI.** You're not just getting answers - you're getting a thinking partner that can take action.

---

## Start Building

The code above is literally all you need to get started. Clone it, modify the tools, add your own functions. 

Most importantly: **start simple.** Don't try to build Jarvis on day one. Build something that solves one small problem really well, then expand from there.

The future isn't about replacing humans with AI. It's about humans working with AI that can actually get stuff done.

What will you build first?

---

*Pro tip: Keep your API costs low while experimenting by using GPT-3.5 for simple tasks and only upgrading to GPT-4 when you need the extra reasoning power.*
