---
title: "Self-Hosted Series: Tandoor"  
date: 2025-03-15  
description: "A guide to setting up one of the most popular recipie tracking services."
tags: [Self-Hosting, Tandoor, Open Source, Recipe Management, Privacy]
categories: [Technology, Self-Hosting]  
draft: false
---




# Self-Hosting Tandoor Recipes: Taking Control of Your Recipe Collection

If you're like me, you've probably got recipes scattered everywhere—saved in browser bookmarks, tucked away in old notes, maybe even written down on random scraps of paper. It's a mess. I wanted a better way to organize everything, but I didn't want to rely on a third-party service. I wanted something **self-hosted**, something I controlled. That's where **Tandoor Recipes** comes in.

Tandoor is an open-source recipe manager that lets you store, categorize, and search your recipes while giving you full control over your data. It’s basically a **self-hosted, privacy-first alternative to something like Paprika or AnyList**, but with even more customization. Since it runs in Docker, it’s easy to set up on any home server or VPS.

## Why Self-Host Your Recipes?

The idea of self-hosting recipes might sound a bit excessive at first. I mean, it’s just recipes, right? But once you start using a dedicated system, you realize how much of an upgrade it is. Here’s why I think Tandoor is worth the effort:

- **No data lock-in.** Your recipes are yours. No cloud service decides to shut down and take your collection with it.
- **Privacy.** No tracking, no ads, no creepy AI trying to "enhance" your cooking habits.
- **Full customization.** You control the categories, tags, and even the UI themes.
- **Automatic ingredient scaling and meal planning.** Helps with grocery shopping and weekly planning.
- **Built-in OCR for scanned recipes.** Perfect for digitizing old family cookbooks.

So yeah, it's a niche tool, but once you get it set up, it's pretty great.

## Setting Up Tandoor Recipes with Docker

I run Tandoor in Docker on my home server. Here’s how I set it up, along with my redacted configuration files so you can replicate it if you want.

### Folder Structure
I keep all my self-hosted apps organized under `/opt/docker/`, with persistent data stored on my NAS. Here’s the structure for Tandoor:

```
/opt/docker/tandoor/          # Tandoor install location
/mnt/r430/tandoor/recipes/    # Recipe data storage
/mnt/r430/tandoor/mediafiles/ # Uploaded images
/mnt/r430/tandoor/staticfiles/ # Static assets
```

### `docker-compose.yml`
This is the main Docker Compose file for Tandoor. I’m using an **external PostgreSQL database** running on an LXC container, but you could run it in Docker if you prefer.

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
      - "8080:8000" # Expose Tandoor on port 8080
    networks:
      - tandoor-net

networks:
  tandoor-net:
    driver: bridge
```

### `.env`
This contains the database credentials and general app settings. Make sure to set a strong `SECRET_KEY`.

```ini
# Database settings
POSTGRES_HOST=192.168.100.52
POSTGRES_PORT=5432
POSTGRES_USER=tandoor
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=tandoor

# Django settings
SECRET_KEY=your-random-secret-key
DEBUG=0
ALLOWED_HOSTS=*
TZ=America/New_York
```

### Setting Up PostgreSQL (If External)
If you're running PostgreSQL in an LXC like I am, you need to set it up manually.

1. SSH into the LXC container running PostgreSQL.
2. Open the PostgreSQL shell:
   ```bash
   sudo -u postgres psql
   ```
3. Create the database and user:
   ```sql
   CREATE DATABASE tandoor;
   CREATE USER tandoor WITH ENCRYPTED PASSWORD 'your-secure-password';
   GRANT ALL PRIVILEGES ON DATABASE tandoor TO tandoor;
   ALTER DATABASE tandoor OWNER TO tandoor;
   ```
4. Allow remote connections by editing `postgresql.conf`:
   ```ini
   listen_addresses = '*'
   ```
5. Update `pg_hba.conf` to allow connections from your Docker host:
   ```
   host    tandoor    tandoor    192.168.100.0/24    md5
   ```
6. Restart PostgreSQL:
   ```bash
   sudo systemctl restart postgresql
   ```

### Starting Tandoor
Once everything is configured, start the container:

```bash
docker-compose up -d
```

If you need to check logs:
```bash
docker logs -f tandoor_web
```

Now, Tandoor should be available at `http://your-server-ip:8080`.

## Wrapping Up

Tandoor is a fantastic tool if you want full control over your recipes and meal planning. It takes a little effort to set up, but once it’s running, you get **complete data freedom**—no subscriptions, no forced updates, just a solid, reliable system for organizing your kitchen. If you’re into self-hosting and home automation, it fits right in with the whole ethos of controlling your own data.

If you set it up, let me know how it works for you. I’d love to hear about any customizations or integrations you come up with. Also, if you have a killer recipe collection, I’m always open to swapping ideas.
