---
title: "Self-Hosted Series: Tandoor"  
date: 2025-03-15  
description: "A guide to setting up one of the most popular recipie tracking services."
tags: [Self-Hosting, Tandoor, Open Source, Recipe Management, Privacy]
categories: [Technology, Self-Hosting]  
draft: false
---

# Finally Getting My Recipe Chaos Under Control with Tandoor

*How I stopped losing track of great recipes and built my own digital cookbook*

---

I had a problem. Actually, multiple problems, all related to recipes. There were bookmarks scattered across three different browsers, screenshots buried in my photo library, handwritten notes shoved in kitchen drawers, and that one amazing pasta sauce recipe my friend texted me two years ago that I can never find when I actually need it.

Sound familiar? I kept meaning to get organized, but every solution I looked at had some dealbreaker. Too expensive, too limited, required subscriptions, or worst of all - what happens when the service shuts down and takes all my carefully curated recipes with it?

That's when I discovered Tandoor Recipes. It's open source, runs on my own hardware, and gives me complete control over my recipe collection. After using it for several months, I can honestly say it's been a game changer for meal planning and grocery shopping.

## Why I Went the Self-Hosted Route

Look, I get it. Setting up your own recipe manager sounds like overkill. There are plenty of apps out there that work fine. But here's what sold me on doing it myself:

**My data stays mine.** I've been burned before by services shutting down or changing their business model. Remember Google Reader? Yeah, I'm not doing that again with my recipe collection.

**No algorithmic nonsense.** I don't need an AI suggesting recipes based on my "cooking personality" or whatever. I just want to find that chicken tikka masala recipe without wading through ads.

**Actual customization.** I can organize things exactly how I want. Custom categories, tags that make sense to me, themes that don't hurt my eyes.

**Built-in meal planning tools.** The grocery list generation alone has saved me countless trips back to the store for forgotten ingredients.

**OCR for old cookbooks.** This feature is honestly magic. I can take a photo of a recipe from my grandmother's cookbook and it'll extract the text automatically.

## Getting Tandoor Up and Running

I run most of my self-hosted stuff in Docker on a home server, and Tandoor fits right into that setup. Here's how I got it working.

### My File Organization

I try to keep things organized, so everything lives under `/opt/docker/` with data stored on my NAS:

```
/opt/docker/tandoor/          # Application files
/mnt/r430/tandoor/recipes/    # Recipe database
/mnt/r430/tandoor/mediafiles/ # Recipe photos
/mnt/r430/tandoor/staticfiles/ # CSS, JS, etc.
```

### The Docker Setup

Here's my `docker-compose.yml`. I'm using an external PostgreSQL database because I already had one running for other services, but you could easily run the database in Docker too:

```yaml
version: '3'

services:
  web:
    image: vabene1111/recipes:latest
    container_name: tandoor_web
    restart: unless-stopped
    depends_on: []
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

### Environment Configuration

All the sensitive stuff goes in the `.env` file:

```ini
# Database connection
POSTGRES_HOST=192.168.100.52
POSTGRES_PORT=5432
POSTGRES_USER=tandoor
POSTGRES_PASSWORD=your-secure-password-here
POSTGRES_DB=tandoor

# Django settings
SECRET_KEY=generate-a-long-random-string-here
DEBUG=0
ALLOWED_HOSTS=*
TZ=America/New_York
```

Make sure you generate a proper secret key - Django uses this for security stuff, so don't just use "password123" or something equally terrible.

### Database Setup (External PostgreSQL)

Since I'm running PostgreSQL in a separate LXC container, I had to set up the database manually. If you're doing the same:

SSH into your database server and create the Tandoor database:

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE tandoor;
CREATE USER tandoor WITH ENCRYPTED PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE tandoor TO tandoor;
ALTER DATABASE tandoor OWNER TO tandoor;
```

Then configure PostgreSQL to accept connections from your Docker host. Edit `postgresql.conf`:

```ini
listen_addresses = '*'
```

And update `pg_hba.conf` to allow your network:

```
host    tandoor    tandoor    192.168.100.0/24    md5
```

Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

### Firing It Up

With everything configured, start the container:

```bash
docker-compose up -d
```

Check the logs to make sure everything's working:

```bash
docker logs -f tandoor_web
```

If all goes well, Tandoor should be accessible at `http://your-server-ip:8080`.

## Living With Tandoor

After using this setup for months, I'm genuinely happy with how it's working out. The web interface is clean and responsive, recipe import works well with most sites, and the meal planning features have actually changed how I approach grocery shopping.

The OCR feature deserves special mention - I've been slowly digitizing recipes from old family cookbooks, and it saves tons of typing. Not perfect, but way better than doing it all manually.

Storage-wise, it's been pretty lightweight. Even with a couple hundred recipes and photos, it's using less than 2GB of space.

## Worth the Effort?

For me, absolutely. The peace of mind of having everything under my own control is worth the initial setup time. Plus, it's nice having a recipe system that actually works the way I want it to, not the way some product manager thinks I should want it to.

If you're already running other self-hosted services, Tandoor fits right in. If this would be your first Docker container, it might be worth starting with something simpler, but it's not particularly complex to set up.

The main downside is that it's not going to have all the social features of some commercial recipe apps. No sharing recipes with friends or browsing community collections. But honestly, I see that as a feature, not a bug.

## Next Steps

I'm still tweaking the setup. Considering adding it to my reverse proxy setup so I can access it from outside my network, and I want to set up automated backups of the recipe database.

There's also a mobile app in development, which would be handy for checking recipes while actually cooking. Right now I just use the web interface on my phone, which works fine but isn't quite as smooth as a native app.

If you decide to give Tandoor a try, let me know how it goes. I'm always curious to hear how other people organize their recipe collections and whether they run into any issues I haven't encountered yet.

---

*Now if only I could get as organized with actually using all these recipes I've been collecting...*
