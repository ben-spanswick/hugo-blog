---
title: "I Built My Own AI Agent with GPT-4o (And You Can Too)"
description: "From chatbot to digital assistant in 50 lines of Python - a practical guide to building your first AI agent that actually gets things done."
date: 2025-03-26T14:30:00-04:00
draft: false
tags: ["AI", "Python", "Automation", "GPT-4o", "Agents"]
categories: [Technology, AI, Agents]
image: "/img/head/buildanagent.png"
---

### AI Summary

- AI agents differ from chatbots by taking action through tools, not just providing answers
- You can build a functional agent in an afternoon with basic Python and the OpenAI API
- The core pattern involves GPT-4o as the "brain" deciding what to do, with Python functions as the "hands" that execute tasks
- Starting simple with toy examples teaches the fundamental concepts before connecting to real-world services

---

### From Chatbot to Digital Assistant

I've been tinkering with AI agents for the past few weeks, and honestly, it's become a bit of an obsession. What started as idle curiosity about "what comes after ChatGPT" turned into building little digital helpers that can actually accomplish tasks instead of just talking about them.

The thing that hooked me wasn't the complexity - it was the simplicity. Most people assume AI agents are either science fiction or require a computer science degree to build. The reality is you can create something genuinely useful in a single afternoon with basic Python skills.

The breakthrough moment came when I realized the difference between asking an AI a question and giving it the ability to take action on your behalf. That's the gap between a chatbot and an agent.

### The Distinction That Actually Matters

Here's the difference in practice:

**Regular chatbot interaction:**
"What's 2+2?"
*"It's 4!"*

**AI agent interaction:**
"Help me budget for my vacation"
*"I'll calculate your available funds, research flight costs, suggest a daily budget, and can book the flights when you're ready."*

The agent I'm about to walk you through does exactly this kind of multi-step thinking:
- Takes your goal
- Makes a plan
- Uses actual tools to get things done  
- Reports back with results

It's basic, sure. But it follows the same fundamental pattern as those million-dollar enterprise systems everyone's talking about.

### What You Actually Need

The barrier to entry is refreshingly low:
- Python 3.8+
- OpenAI API key (GPT-4o works best)
- Two packages: `openai` and `rich`

That's it. No complicated frameworks, no cloud deployments, no PhD required.

```bash
pip install openai rich
```

### Step 1: Give Your Agent Some Hands

An agent without tools is just an expensive chatbot. Let's start with simple examples that demonstrate the concept:

```python
def search_todos(query):
    # Fake database for demonstration
    todos = ["Buy milk", "Call mom", "Finish blog post", "Book dentist appointment"]
    return [todo for todo in todos if query.lower() in todo.lower()]

def simple_calculator(expression):
    try:
        return str(eval(expression))  # Don't do this in production!
    except Exception as e:
        return f"Error: {str(e)}"
```

Now register them so the agent knows what's available:

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

> These are toy examples to illustrate the pattern. In production, you'd connect to actual APIs, databases, or services. I'm working on a full writeup of my PaperlessNGX document management agent that does exactly this - stay tuned.

### Step 2: The Agent Brain

This is where it gets interesting. We create a decision loop where GPT-4o decides what to do, we execute it, and feed the results back:

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
            model="gpt-4o",
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

The magic here: GPT-4o acts as the decision-making "brain" while your Python functions become its "hands" for actually executing tasks.

### Step 3: Take It for a Test Drive

```python
if __name__ == "__main__":
    openai.api_key = "your-api-key-here"  # Use environment variables!
    goal = input("What's your goal? ")
    run_agent(goal)
```

Try these prompts:
- "What appointments do I have coming up?"
- "Calculate compound interest on $1000 at 5% for 3 years"
- "Find anything in my todos about family"

Here's what a typical run looks like:

```
Goal: Search for any appointments in my todos
Thinking...
Using: search_todos('appointment')
Result: I found 1 appointment-related item:
- "Book dentist appointment"

You should probably schedule that dentist visit!
```

### Why This Pattern Actually Works

**It chains actions intelligently.** Give it a complex goal like "Calculate my monthly budget and find related todos" and watch it break the problem down:
1. Use calculator for budget math
2. Search todos for financial items  
3. Combine and present results

**It adapts on the fly.** If a tool returns unexpected results, the agent adjusts its approach. No rigid scripting required.

**It explains itself.** You can see exactly what it's doing and why. Full transparency into the decision process.

### Scaling Beyond Toy Examples

The real power emerges when you connect to actual services:
- Weather APIs for context-aware suggestions
- Your calendar for scheduling intelligence  
- Email or Slack for communication
- Smart home devices for automation
- Document systems for knowledge retrieval

You can also add persistence:
- Store conversation history
- Remember user preferences
- Build context over time

Or go proactive:
- Run agents on schedules
- Send daily summaries
- Alert about important changes

### The "Aha" Moment

After playing with this pattern for a few days, something clicked that changed how I think about AI tooling. This isn't just automation - it's delegation to something that can actually reason through problems.

I tested it with "help me prep for my Monday meetings" and watched it methodically search my todos for meeting-related items, calculate available prep time, suggest a preparation schedule, and offer to set reminders.

It felt less like using a tool and more like working with a capable assistant who could think through multi-step problems. That's the fundamental shift with agentic AI - you're not just getting answers, you're getting a thinking partner that can take action.

### Start Building Today

The code above is literally all you need to begin. Fork it, modify the tools, add your own functions. Most importantly: start simple and expand gradually.

Don't try to build Jarvis on day one. Build something that solves one small problem really well, then iterate from there.

The future isn't about replacing humans with AI - it's about humans working alongside AI that can actually get stuff done. What will you delegate first?
