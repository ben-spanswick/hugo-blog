---
title: "How to Scale a Data Science Team Without Losing Agility"
description: "Real lessons from building a data science organization from 2 analysts to 20+ people across multiple business units in six years."
date: 2025-01-30T14:30:00-04:00
draft: false
tags: ["Data Science", "Team Building", "Leadership", "Scaling", "Enterprise"]
categories: ["Data Science", Leadership"]
image: "/img/head/agile.png"
---

### AI Summary

- Scaling from 2 analysts to 20+ data scientists requires evolving from scrappy execution to structured operations while preserving speed
- Infrastructure dependencies become the primary scaling constraint in most enterprise environments
- Rigorous best practices early on actually accelerate agility as teams grow - you pay yourself back later
- Formalization becomes mandatory as you grow, but it should enable faster execution, not slow it down

---

### The Reality Check Nobody Talks About

Six years ago, I walked into a room with two analysts and a mandate to build something bigger. Today, I'm running a 20+ person data science organization spanning multiple business units, covering everything from operational optimization to customer experience modeling.

The conventional scaling wisdom - squads, agile methodologies, minimal process - isn't wrong. But it's incomplete when you're operating in any enterprise environment where your biggest constraint isn't team dynamics or technical debt. It's waiting months for infrastructure teams to align with your growth trajectory.

Let me walk you through what actually happens when you scale a data science team in the real world, not the startup fantasy version.

### The Infrastructure Chokepoint

The first hard lesson: your technical infrastructure will become your primary scaling bottleneck before you hit any of the sexy organizational challenges everyone writes about.

Enterprise IT organizations have their own priorities, their own timelines, and their own risk tolerance. When you need new environments, tools, or access provisioned, you're not just asking for resources - you're asking them to deviate from their carefully orchestrated roadmap.

> The three-month delay for a single workspace deployment taught me more about enterprise scaling than any management book ever could.

This reality forces a different kind of strategic thinking. You can't just hire more people and expect linear productivity gains. You have to sequence your growth around infrastructure availability, which means getting really good at forecasting your technical needs 6-12 months ahead of your hiring plans.

The practical solution: build relationships with infrastructure teams early, understand their constraints, and align your scaling timeline with their capacity. It's not glamorous, but it's the difference between a team that grows smoothly and one that spends half its time waiting for access to tools.

### The Production-Ready Paradox

Here's where most data science scaling advice falls apart: it assumes you have the luxury of iterative improvement from prototype to production. In most enterprise environments with real business impact, that's not sustainable.

My team produces more models than our deployment pipeline can handle. The bottleneck isn't ideation or experimentation - it's getting things into production. The solution isn't hiring more deployment engineers; it's changing how data scientists operate.

Now, I understand that not every team can require full production-grade code from day one. Your MLOps maturity, tooling, and business context all factor into what's realistic. But here's what I've learned: **implementing rigorous best practices early, while it seems to stifle agility, actually accelerates it as you scale.**

You pay yourself back later.

When data scientists write clean, documented, testable code from the start - even if it's not fully production-ready - the compound benefits are massive:
- Faster code reviews and collaboration
- Easier debugging and maintenance
- Smoother handoffs to deployment teams  
- Reduced technical debt that would otherwise cripple velocity

The mindset shift is crucial: *we're not researchers exploring possibilities; we're engineers building systems that solve business problems.* The rigor isn't about crushing creativity - it's about making creativity sustainable at scale.

### When to Put Away Childish Things

There's a moment in every scaling journey where informal processes stop working. You can feel it coming - decisions take longer, coordination becomes painful, and new team members struggle to understand how things actually get done.

This is where the startup mentality has to evolve. Not abandoned - evolved.

The early scrappy approach that got you from 2 to 8 people will kill you at 20. But the solution isn't to swing completely into bureaucracy. It's about formalizing the things that enable speed, not the things that slow you down.

**What we formalized:**
- Code standards and review processes
- Model governance and risk assessment
- Value capture documentation and ROI tracking
- Cross-functional collaboration protocols

**What we kept informal:**
- Experimental project approval
- Individual learning and development paths
- Day-to-day team coordination
- Technical architecture decisions within established patterns

The key insight: formalization should accelerate decision-making for routine work, preserving the informal speed for the work that actually requires creativity and judgment.

### The Multi-Business Unit Complexity Layer

Scaling across multiple business units adds a dimension that most scaling advice ignores entirely. You're not just managing team growth - you're managing different stakeholder expectations, varying technical maturity levels, and competing priorities that may not align.

Each business unit has its own definition of success, its own timeline pressures, and its own tolerance for experimentation. What works for supply chain optimization in one area might be completely inappropriate for customer analytics in another.

The solution isn't trying to force standardization everywhere. It's about building *platforms* that can accommodate different use cases while maintaining consistency in governance and quality standards.

We built shared infrastructure - feature stores, deployment pipelines, monitoring systems - but allowed flexibility in how each business unit applied the capabilities to their specific challenges.

### Value Capture as a Scaling Strategy

As your team grows, the pressure to demonstrate ROI becomes exponentially more intense. A two-person analytics team can fly under the radar. A 20-person organization with a multi-million-dollar budget cannot.

This is where many data science teams fail. They treat value capture as an afterthought, something to document after the fact for reporting purposes. But at scale, value capture becomes a core competency that determines whether you continue to grow or get budget-cut into irrelevance.

**Our approach:**
- Every project starts with a business case and success metrics
- We track not just technical performance but business impact
- Quarterly reviews focus on outcomes, not outputs
- We proactively communicate wins and learnings to stakeholders

The uncomfortable truth: at scale, your technical excellence matters less than your ability to articulate and capture business value. Teams that can't make this transition don't survive budget cycles.

### The Rigor Dividend

The biggest misconception about scaling data science teams is that more process means less agility. In my experience, the opposite is true - but only if you implement the right kind of rigor.

Rigorous code standards feel slow when you're starting out. But six months later, when you can onboard new team members in days instead of weeks, when debugging takes minutes instead of hours, when models can be updated and deployed without archaeology projects to understand the original code - that's when you realize you've been paying yourself back.

The teams that maintain agility at scale aren't the ones that avoid process. They're the ones that implement process strategically, focusing on the practices that create compound returns on productivity.

### The Evolution Mindset

The biggest mistake I see in scaling data science teams is trying to preserve what made the early team successful instead of evolving into what the scaled team needs to become.

The principles stay constant: speed, ownership, experimentation, impact. But the implementation has to change completely.

A 20-person team can't operate like a 5-person team any more than a 5-person team should operate like a 20-person team. The magic is in evolving the structure to support the principles at whatever scale your business requires.

Because the alternative - becoming one of those expensive teams that produces impressive PowerPoints and minimal business impact - isn't just a failure of process. It's a failure to recognize that scaling is fundamentally about evolution, not preservation.

The math of team growth is unforgiving, but so is the market for data science value. Teams that figure out how to evolve while staying effective don't just survive scaling - they become indispensable.

And in a world where data science budgets are under constant scrutiny, indispensable is exactly where you want to be.
