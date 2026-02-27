---
title: Building a Robust Access Layer for Self-Hosted Services
date: 2024-11-20T12:00:00-05:00
description: A practical guide to securely exposing your self-hosted services using Cloudflared Tunnel, Traefik reverse proxy, and Authelia authentication—featuring a real-world Tandoor Recipes integration.
categories: ["Projects", "Homelab"]
tags:
  - homelab
  - self-hosting
  - traefik
  - cloudflared
  - authelia
  - docker
image: /img/oneoff/authelia1.png
draft: false
---

# Making My Self-Hosted Services Actually Accessible (Without Going Insane)

*How I finally got my recipe manager working from anywhere without poking holes in my firewall*

Posted: May 14, 2025 | 6 min read

---

So here's the thing - I've been running services in my homelab for years, and every time I want to access something remotely, it turns into this whole ordeal. You know the drill: "just open a port," they say. "Point your domain at it," they say. Yeah, right. Tell that to my segmented VLANs and my paranoia about security.

Last month I finally had enough. My wife kept asking why she couldn't access our recipe collection (Tandoor Recipes) when she was out grocery shopping, and honestly, I was getting tired of VPN'ing in just to check if I had the ingredients for dinner. Time to build something proper.

After way too much research and probably more frustration than necessary, I ended up with a setup using Cloudflared tunnels, Traefik, and Authelia. Spoiler alert: it actually works really well now, but getting there was... an adventure.

## The Problem (aka Why Simple Solutions Suck)

My homelab isn't just one machine sitting in a closet. I've got services scattered across different VLANs because, you know, security. Tandoor lives on its own Docker host, the proxy stuff is somewhere else, and everything's firewalled to hell and back. 

What I wanted was pretty reasonable, I thought:
- Access my stuff from anywhere without opening ports
- Stop managing separate logins for everything
- Make it user-friendly enough that my family could actually use it
- Keep it modular so I'm not locked into some monolithic solution

The "just use a VPN" crowd can save it - I wanted something that actually felt like using a normal website.

## How I Solved It (The Technical Bits)

### The Stack

I went with three main pieces:

**Cloudflared Tunnel** - This thing is honestly brilliant. Instead of punching holes in your firewall, it creates an outbound connection to Cloudflare. Your services stay completely internal, but you can access them through proper domains.

**Traefik** - Handles all the reverse proxy magic. Routes requests, manages SSL certificates, plays nice with Docker labels. Once you get the hang of it, adding new services is actually pretty painless.

**Authelia** - The authentication layer. Single sign-on, 2FA, granular access controls. Makes everything feel professional instead of like a garage project.

Here's how they fit together:

```
Internet
   │
Cloudflare (your domain DNS)
   │
Cloudflared Tunnel (Docker container)
   │
Traefik Reverse Proxy
   │
Authelia Authentication
   │
Tandoor Service (on another VLAN)
```

### Getting Cloudflared Working

The tunnel setup was actually the easiest part, which surprised me. Create a tunnel in the Cloudflare dashboard, grab the token, throw it in a Docker container:

```yaml
services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    restart: unless-stopped
    command: tunnel run
    environment:
      - TUNNEL_TOKEN=<your-token-here>
    volumes:
      - ./cloudflared:/etc/cloudflared
```

The only gotcha I hit was making sure the credentials file was mounted properly. Oh, and if you're dealing with WebSocket apps, you might need some extra config - learned that one the hard way.

### Traefik Configuration Hell (Then Heaven)

Traefik's great once it's working, but man, those labels are picky. Miss a capital letter or mess up the syntax and nothing works. No helpful error messages either - it just silently ignores your configuration.

My static config ended up looking like this:

```yaml
# traefik.yml
entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  docker:
    exposedByDefault: false

certificatesResolvers:
  cloudflare:
    acme:
      email: "your-email@domain.com"
      storage: "/etc/traefik/acme.json"
      dnsChallenge:
        provider: cloudflare
```

For services, the labels look like this:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.tandoor.rule=Host(`recipes.yourdomain.com`)"
  - "traefik.http.routers.tandoor.entrypoints=websecure"
  - "traefik.http.routers.tandoor.tls.certresolver=cloudflare"
  - "traefik.http.routers.tandoor.middlewares=authelia@docker"
```

Pro tip: Use a YAML linter. Seriously. Saved me hours of debugging.

### Authelia: Powerful but Intimidating

Authelia's config file is... extensive. Like, really extensive. I probably spent more time on this than everything else combined, mostly because I kept overthinking it.

Here's what worked for me (simplified):

```yaml
host: 0.0.0.0
port: 9091
log_level: info

authentication_backend:
  file:
    path: /config/users_database.yml

access_control:
  default_policy: deny
  rules:
    - domain: "recipes.yourdomain.com"
      policy: two_factor

session:
  name: authelia_session
  secret: your-secret-here
  expiration: 1h

storage:
  local:
    path: /config/db.sqlite3

notifier:
  filesystem:
    filename: /config/notification.txt
```

Start simple, get it working, then add complexity. Trust me on this one.

### The VLAN Nightmare

Here's where things got interesting. Tandoor runs on a completely different network segment, so Traefik couldn't just magically find it. I had to:

1. Open firewall rules between the Traefik host and Tandoor's host
2. Set up proper DNS resolution (or just use IP addresses)
3. Configure Traefik to route to the external service

The key was adding this to Traefik:

```yaml
- "traefik.http.services.tandoor.loadbalancer.server.url=http://192.168.100.100:8085"
```

Took me way too long to figure out that one line.

## What I Learned (The Hard Way)

**VLANs will humble you.** I thought I knew networking. I was wrong. Spend time getting your firewall rules right before you blame the software.

**Start with the basics.** Don't try to set up everything at once. Get a simple HTTP service working first, then add authentication, then SSL, then complexity.

**Documentation is your friend.** Especially for Authelia - that config file has about 50 different options and most of them aren't obvious.

**Version control everything.** I keep all my configs in a private Git repo. When something breaks (and it will), you can actually figure out what changed.

**Cloudflared is magic.** Seriously, the peace of mind of not having any open ports is worth the setup hassle.

## Was It Worth It?

Absolutely. My wife can now check recipes while shopping, I can access my services from anywhere, and I sleep better knowing I'm not running an open port festival. 

The best part? Adding new services is actually easy now. Same pattern every time: add the Docker labels, create an Authelia rule, done. It scales really well once you have the foundation in place.

If you're thinking about doing something similar, start small. Pick one service, get it working end-to-end, then expand. The modular approach means you're not locked into anything - if you hate Traefik tomorrow, you can swap it out without rebuilding everything.

And hey, if you get stuck, the homelab community is pretty helpful. Just don't ask them about VLANs unless you want a 3-hour discussion about network segmentation philosophy.

---

*All the config files and Docker Compose examples are in my GitHub repo if you want to see the full setup. Just search for my username and "homelab-access-stack" or something like that.*
