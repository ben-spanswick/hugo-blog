---
title: "Self-Hosted Series: Tandoor"
description: "How I finally got my recipe chaos under control with a self-hosted solution that actually works"
date: 2025-05-27T14:30:00-04:00
draft: false
tags: ["Self-Hosted", "Docker", "Recipes", "Homelab", "Proxmox"]
categories: ["Self-Hosted", "Homelab", "Guide"]
image: "/img/head/tandoor.png"
---

### AI Summary

- Tandoor Recipes is an open-source, self-hosted recipe manager that solves the scattered bookmark problem
- Features include OCR for digitizing old cookbooks, meal planning tools, and automatic grocery list generation
- Docker deployment on Proxmox with external PostgreSQL provides a robust, backup-friendly architecture
- After months of use, it's genuinely transformed meal planning and grocery shopping workflows

---

### Finally Getting My Recipe Chaos Under Control

The last time I tried to find that incredible pasta sauce recipe my friend shared, I spent twenty minutes digging through browser bookmarks, photo albums, and random text files. That moment of frustration was the final straw in my ongoing battle with recipe organization chaos.

My kitchen strategy had devolved into a digital disaster zone. Screenshots buried three layers deep in my camera roll, bookmarks scattered across browsers, handwritten notes shoved in drawers, and the occasional recipe texted to me that vanished into message history. Every attempt at organization failed because the solutions were either too expensive, too limiting, or - my biggest fear - destined to disappear when the company pivoted or shut down.

That's when I discovered Tandoor Recipes, and it's been a genuine revelation.

### Why Self-Hosting Makes Sense Here

The conventional wisdom says just use whatever recipe app has the best reviews. But after wrestling with this problem across multiple failed attempts, I realized the fundamental issue wasn't the interface - it was control.

**My data stays exactly where I want it.** I've been through the Google Reader shutdown, the endless parade of acquired startups, and the slow feature creep of subscription models. Not happening again with something as personal as my recipe collection.

**Zero algorithmic interference.** I don't need machine learning suggesting recipes based on my "cooking personality profile." I need to find my go-to chicken tikka masala when I'm standing in the grocery store at 6 PM on a Wednesday.

**Real customization that actually works.** Custom categories that map to how I actually cook. Tags that make sense to my workflow. A interface that doesn't assume I want to scroll through food photography when I just need the ingredient list.

The built-in meal planning and grocery list generation turned out to be the killer features I didn't know I needed. But the OCR capability for digitizing old cookbook pages? That's pure magic.

### The Technical Setup That Actually Works

My homelab runs on a Proxmox cluster, with most applications deployed in a dedicated Docker VM that has plenty of resources allocated. PostgreSQL lives in its own LXC container because centralized database management makes backups and maintenance infinitely easier.

This architecture has proven rock-solid for Tandoor. The separation means database maintenance doesn't impact the application, and I can snapshot the entire setup independently.

Here's the structure that's been working flawlessly:

```
/opt/docker/tandoor/          # Application files
/mnt/r430/tandoor/recipes/    # Recipe database
/mnt/r430/tandoor/mediafiles/ # Recipe photos
/mnt/r430/tandoor/staticfiles/ # Static assets
```

The Docker configuration is straightforward but robust:

```yaml
version: '3'

services:
  web:
    image: vabene1111/recipes:latest
    container_name: tandoor_web
    restart: unless-stopped
    volumes:
      - /mnt/r430/tandoor/recipes:/opt/recipes
      - /mnt/r430/tandoor/mediafiles:/opt/recipes/mediafiles
      - /mnt/r430/tandoor/staticfiles:/opt/recipes/staticfiles
    env_file:
      - .env
    ports:
      - "8080:8000"
    networks:
      - tandoor-net

networks:
  tandoor-net:
    driver: bridge
```

Environment configuration handles the database connection and Django security settings:

```bash
# Database connection
POSTGRES_HOST=your-postgres-ip
POSTGRES_PORT=your-port
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=your-postgres-db

# Django settings
SECRET_KEY=generate-a-proper-secret-key
DEBUG=0
ALLOWED_HOSTS=*
TZ=America/New_York
```

*Pro tip: Actually generate a real secret key. Django's security depends on it, and "password123" isn't going to cut it.*

Database setup in the PostgreSQL LXC is clean and minimal:

```sql
CREATE DATABASE dbname;
CREATE USER tandoor WITH ENCRYPTED PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE dbname TO username;
ALTER DATABASE dbname OWNER TO username;
```

Configure PostgreSQL to accept connections from the Docker host network, restart the service, and you're ready to deploy.

### Living With Tandoor Day-to-Day

After months of actual use, this setup has fundamentally changed how I approach cooking and meal planning. The web interface is responsive and intuitive - I can quickly add recipes, organize them into logical categories, and actually find things when I need them.

Recipe import works seamlessly with most cooking websites. Copy the URL, paste it into Tandoor, and it automatically extracts ingredients, instructions, and photos. The parsing accuracy is impressive, though I occasionally need to clean up formatting quirks from particularly complex recipe sites.

**The OCR feature deserves special recognition.** I've been systematically digitizing recipes from family cookbooks that have been collecting dust for years. Take a photo of the page, and Tandoor extracts the text with remarkable accuracy. It's not perfect, but it beats manually typing every ingredient and instruction.

Meal planning integration has genuinely improved my grocery shopping efficiency. Plan out the week's dinners, and Tandoor automatically generates a consolidated shopping list organized by ingredient type. No more wandering the aisles trying to remember if I already have cumin at home.

**Storage footprint remains surprisingly light.** Even with several hundred recipes and associated photos, the entire setup uses less than 2GB of space. Database backups are quick, and the whole system restarts in seconds during maintenance windows.

### Why This Actually Matters

The real test of any self-hosted solution isn't the initial setup excitement - it's whether you're still using it six months later. Tandoor has passed that test definitively.

*It works the way I think about cooking*, not the way some product manager imagined I should think about cooking. Custom categories map to my actual meal rotation. Tags reflect ingredients I commonly substitute or dietary restrictions that matter to my household. The interface gets out of the way and lets me focus on the recipes themselves.

The peace of mind factor can't be overstated. My recipe collection is backed up alongside my other important data, version controlled, and completely under my control. No subscription fees, no feature deprecation, no sudden policy changes that break my workflow.

Sure, there are no social features for sharing recipes with friends or browsing community collections. But honestly, that feels like a benefit rather than a limitation. I wanted a tool, not a social network.

### The Path Forward

I'm still refining the deployment. Adding it to my reverse proxy setup for external access is on the roadmap, and I want to implement automated database backups as part of my broader infrastructure maintenance.

The mobile app development looks promising for those moments when you're actually standing in the kitchen with flour on your hands trying to remember if the recipe called for one teaspoon or one tablespoon of vanilla.

For now, the web interface works perfectly on mobile browsers, though a native app would provide a smoother experience for recipe viewing while cooking.

### Worth the Investment?

If you're already running a homelab with Docker capability, Tandoor integrates seamlessly into your existing infrastructure. The initial setup investment pays dividends immediately through improved meal planning efficiency and the genuine satisfaction of having a recipe management system that works exactly how you want it to.

The bigger question is whether self-hosting makes sense for your particular situation. If you're comfortable with the technical requirements and value data ownership over convenience features, Tandoor represents exactly the kind of thoughtful, well-executed open source project that makes self-hosting worthwhile.

My recipe chaos is officially under control. Now I just need to work on actually cooking all these recipes I've been meticulously organizing.
