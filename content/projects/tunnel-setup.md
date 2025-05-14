---
title: "Building a Robust Access Layer for Self-Hosted Services"
date: 2025-05-14T12:00:00-05:00
description: "A practical guide to securely exposing your self-hosted services using Cloudflared Tunnel, Traefik reverse proxy, and Authelia authentication—featuring a real-world Tandoor Recipes integration."
tags: ["homelab", "self-hosting", "traefik", "cloudflared", "authelia", "docker"] 
draft: false
---

## Building a Robust Access Layer for Self-Hosted Services

If you’ve ever tried to securely expose a self-hosted service—especially something running on a different VLAN, host, or network segment—you’ll know it’s rarely as simple as “open a port and point a domain.” Security, authentication, and user experience all matter—especially if you want to make your setup both safe and maintainable.

Recently, I set out to unify remote access for my core services using a trio of modern open source tools:  
**Cloudflared Tunnel** for secure remote access,  
**Traefik** for reverse proxying and routing, and  
**Authelia** for SSO and two-factor authentication.

My test case? Getting [Tandoor Recipes](https://tandoor.dev/)—my favorite recipe manager—securely accessible from anywhere, while keeping everything modular, portable, and as “future-proof” as possible.

Let’s break down how I approached the problem, what worked, where I struggled, and the lessons learned.

---

## The Challenge: Security Meets Usability

My self-hosted services live across a sprawling homelab network, segmented by VLANs for security. Tandoor, for example, is on a Docker host in its own VLAN. The proxy and auth stack are elsewhere. I wanted:

- **Remote access with minimal attack surface** (no open ports, no NAT headaches)
    
- **Central authentication** (not just for Tandoor, but for all future services)
    
- **User-friendly access** (SSO, 2FA, clean URLs, etc.)
    
- **Modularity** (each service and component should be replaceable and independently upgradable)
    
- **Easy migration to new hosts or VLANs**
    

Off-the-shelf solutions (and default “expose to the world” settings) were simply not robust enough. So I turned to **Cloudflared Tunnel, Traefik, and Authelia**—a stack designed for this kind of composable, secure access.

---

## The Architecture: How the Pieces Fit

**1. Cloudflared Tunnel**  
This is the secret sauce for secure remote access—think of it as an outbound VPN tunnel that connects your homelab to Cloudflare’s edge, so you can access your services via custom domains (e.g., "service.website.com") with _zero_ inbound ports exposed.

**2. Traefik**  
Acts as a reverse proxy and smart router. Handles SSL via Let’s Encrypt, routes requests to the right internal services, and integrates with authentication/authorization layers like Authelia.

**3. Authelia**  
Provides single sign-on (SSO) and two-factor authentication (2FA) for protected services. It sits in front of Traefik-proxied endpoints, enforcing access policies.

**4. Example Service: Tandoor**  
A recipe manager running on a dedicated Docker host and VLAN, exposed internally on a non-standard port.

### Visual Diagram (Text)

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

---

## Implementation Details

### Step 1: Cloudflared Tunnel

**What worked:**

- Outbound-only connection—no open ports required
    
- Quick setup with Cloudflare dashboard and Docker
    

**What tripped me up:**

- The tunnel token/credentials file _must_ be mapped correctly in Docker
    
- Internal DNS sometimes didn’t resolve as expected between VLANs
    
- Proxying WebSockets (for some apps) can require extra config
    

**Redacted Docker Compose Snippet:**

```yaml
services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    restart: unless-stopped
    command: tunnel run
    environment:
      - TUNNEL_TOKEN=<REDACTED>
    volumes:
      - ./cloudflared:/etc/cloudflared
```

- For detailed setup, see [Cloudflared Tunnel on GitHub](https://github.com/cloudflare/cloudflared)
    

---

### Step 2: Traefik as Reverse Proxy

**What worked:**

- Dynamic routing based on labels—great for multiple services
    
- Easy SSL with Let’s Encrypt (wildcard domains supported)
    
- Good integration with Docker, static files, and Cloudflare headers
    

**What tripped me up:**

- Label syntax is _very_ particular (small mistakes break routing)
    
- Services on other VLANs/hosts: requires careful network and firewall rules
    
- Wildcard certificates only work if DNS challenge is set up
    

**Redacted Static Configuration:**

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
      email: "<REDACTED>"
      storage: "/etc/traefik/acme.json"
      dnsChallenge:
        provider: cloudflare
        delayBeforeCheck: 0
```

**Service Label Example:**

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.tandoor.rule=Host(`service.website.com`)"
  - "traefik.http.routers.tandoor.entrypoints=websecure"
  - "traefik.http.routers.tandoor.tls.certresolver=cloudflare"
  - "traefik.http.routers.tandoor.middlewares=authelia@docker"
```

---

### Step 3: Authelia Authentication Layer

**What worked:**

- Easy to set up with file-based users for homelab use
    
- Supports 2FA out of the box
    
- Flexible access control rules by domain/path
    

**What tripped me up:**

- Initial config can be overwhelming (lots of options; a single typo = silent failures)
    
- Network segmentation meant some cookies/auth flows didn’t cross VLANs until I tweaked CORS and cookie settings
    
- Need to mount configuration and secrets into the container
    

**Redacted Example `configuration.yml`:**

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
    - domain: "service.website.com"
      policy: two_factor

session:
  name: authelia_session
  secret: <REDACTED>
  expiration: 1h

storage:
  local:
    path: /config/db.sqlite3

notifier:
  filesystem:
    filename: /config/notification.txt
```

---

### Step 4: Routing to Tandoor (On a Different VLAN/Host)

This was where _networking pain_ surfaced:

- **Challenge:** Tandoor runs on a separate VLAN and Docker host, so Traefik (on its own network) couldn’t access it by default.
    
- **Solution:**
    
    - Open specific firewall rules for Traefik’s host IP to Tandoor’s port
        
    - Add internal DNS/static mapping so `tandoor.internal.lab` (or direct IP) resolved from Traefik’s container
        
    - Adjust Traefik service definition to use the target IP:port
        

**Redacted Docker Compose Example (Tandoor Service):**

```yaml
services:
  tandoor:
    image: vabene1111/recipes
    environment:
      - ...
    ports:
      - "8085:8080"
    networks:
      - tandoor
networks:
  tandoor:
    external: true
```

**Key Traefik dynamic config:**

```yaml
- "traefik.http.services.tandoor.loadbalancer.server.url=http://192.168.100.100:8085"
```

Or set a local DNS entry for `tandoor.internal.lab` and use:

```yaml
- "traefik.http.services.tandoor.loadbalancer.server.url=http://tandoor.internal.lab:8080"
```

---

## Lessons Learned (and What I’d Do Differently)

**1. VLANs are powerful but unforgiving.**  
Small misconfigurations in firewall rules or Docker network settings can break cross-VLAN service routing. Use granular allow rules and monitor logs early and often.

**2. Authelia config is verbose—but the docs are your friend.**  
Start with the simplest possible working config, then layer in access rules, 2FA, and notifications one at a time.

**3. Cloudflared Tunnel = peace of mind.**  
Outbound-only tunnels are game-changing. No more open ports, no more sketchy port forwards.

**4. Traefik labels: Get them right, or nothing works.**  
Use YAML linting, double-check case sensitivity, and always test with a basic HTTP service before layering in Authelia or complex middlewares.

**5. Use Git for everything.**  
All configs are in a private GitHub repo—if you make a mistake, you can always roll back. Plus, it’s much easier to track what changed when troubleshooting.

---

## Configuration Reference

- **Full sample Docker Compose files and configs:**  
    [My GitHub repo for this stack (redacted version)](https://github.com/yourusername/selfhosted-auth-stack)
    

---

## Final Thoughts

The real win here isn’t any single technology, but how Cloudflared, Traefik, and Authelia can work together—especially for anyone juggling multiple hosts, VLANs, and services.

This approach lets you:

- **Expose new services with minimal friction**
    
- **Enforce central auth and 2FA everywhere**
    
- **Scale your setup—move services to new VLANs or hosts without rearchitecting everything**
    

If you’re just getting started, focus on a single service (like Tandoor), get that rock-solid, and then build out from there. The modular approach pays dividends—what works for one app can quickly protect your entire homelab.

---

_If you want detailed, up-to-date configs or a deeper dive into VLAN firewall rules, check the GitHub link above.
