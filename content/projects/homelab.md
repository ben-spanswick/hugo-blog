---
title: "First Homelab: Reflections, Diagram, and Stack"
date: 2025-05-14T15:00:00-04:00
description: "My first ever homelab diagram, hardware reflections, and current stack of self-hosted services, security tools, and AI experiments."
tags: ["homelab", "self-hosting", "networking", "AI", "hardware"]
categories: ["Self-Hosting", "Hardware"]
weight: 1
draft: false
---

![Homelab Diagram](/img/HL.jpg)

# Building My First Homelab: Reflections, Stack, and Next Steps

I've always admired the impressive homelab diagrams circulating on self-hosting forums. After years of lurking, tinkering, and gradually collecting hardware, I finally decided to document my own setup and journey.

This post summarizes what I'm running, what I've learned along the way, and how a casual experiment turned into a full-blown hobby.

---

## From Proxmox Curiosity to a Full Rack

The homelab journey began a couple of years ago, when I picked up a Lenovo m720q Tiny to run a Kali VM for some light pen-testing and CTF challenges. The spark was there, but life intervened, and the project was shelved.

Still, the curiosity stuck. After discovering the homelab and self-hosted communities, I took the plunge and bought two used servers—a Dell r730xd and an r430—right before the arrival of our second child. As you might expect, the servers went straight into storage.

---

## Picking Up the Project

Earlier this year, with a bit more time and sleep, I finally assembled the rack, wired up switches, and started building out the network. What started as a few VMs quickly became a full stack: network segmentation, VLANs, containers, and a host of new services.

Recently, my attention has shifted toward AI experimentation. I built a dedicated AI rig, first with MI50 GPUs and now with 3090s and 3090Tis. Running local LLMs, experimenting with AI agents, and integrating custom tools has been a huge part of the learning curve.

---

## Background

For context, I’m not a professional system administrator. My background is in tech leadership and data science for a large company, but the homelab is strictly a hobby. It’s a late-night project fueled by curiosity, trial-and-error, and a desire to truly understand the technology I use.

I enjoy exploring open-source services, experimenting with network architectures (sometimes to excess), and continually learning about security and automation in a hands-on way.

---

## Current Stack

Here's what I have running today, organized by function.

**Media & Entertainment**  
Jellyfin, *arr suite (Readarr, Prowlarr, etc.), qBittorrent with Gluetun VPN, Audiobookshelf

**Lifestyle & Smart Home**  
Tandoor (recipes), Bar Assistant, Plant It, FreshRSS, Home Assistant

**Productivity & Documentation**  
Gitea (private Git), Nextcloud, PaperlessNGX, Draw.io, Filebrowser, n8n, Karakeep, Linkwarden, SANE Network Scanning, Kopia

**Databases**  
MariaDB, PostgreSQL, InfluxDB

**Monitoring & Management**  
Grafana, Uptime Kuma, Homepage dashboard, Portainer, Watchtower, Prometheus

**Security & Networking**  
OPNSense, Fail2Ban, Authelia (SSO/2FA), Pi-hole, Traefik, MITMproxy, Tailscale, Cloudflared

**AI Stack**  
llama.cpp, AnythingLLM, PostgreSQL with pgvector, n8n for orchestration

---

## Upcoming Projects

Like most homelabbers, my "future plans" list is always growing. On the shortlist:

- Changedetection, Dashy, Glance, Homarr
- Revisit Matrix/Element setup
- Firefly III (personal finance), Immich (photos), Joplin (notes)
- Lube Logger, Monica, OnlyOffice, Open Meteo, Rocket.Chat, Syncthing, VSCode Server (currently running locally)

---

## Lessons Learned

- Hardware is interesting, but the real power is in what you do with it. The software ecosystem is where experimentation pays off.
- Network segmentation can be addictive. One VLAN for IoT leads to many more as complexity grows.
- Backups matter. Tools like Kopia and PaperlessNGX have already proven invaluable for recovery and organization.
- You do not need to be a sysadmin to run a homelab. Curiosity and persistence are more important than credentials.
- There is always more to learn, and that's what makes this hobby worth the investment.

---

## Next Steps

I'm planning a follow-up with hardware photos and a deep dive into the AI stack and automation workflows. If you have feedback, advice, or want to trade configs, let me know. I'm always looking for ways to improve or expand the lab.

Stay tuned for more, and happy self-hosting.

