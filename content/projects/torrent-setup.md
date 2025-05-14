---
title: "From Torrent to Library: Automating TV, Movies, and Audiobooks with Gluetun, qBittorrent, and arr"
date: 2025-05-14T13:00:00-04:00
description: "How I built a private, automated media pipeline with bulletproof VPN, container orchestration, and seamless syncing to Unraid."
categories: ["homelab", "self-hosting", "privacy"]
tags: ["homelab", "self-hosting", "torrenting", "automation", "gluetun", "qbittorrent", "sonarr", "radarr", "audiobookshelf", "unraid"]
draft: false
------------

# From Torrent to Library: Automating TV, Movies, and Audiobooks with Gluetun, qBittorrent, and \*arr

**Private torrenting pipeline behind a VPN, with automatic sorting and renaming**
May 14, 2025
\~11 minute read

---

## The Problem: Secure, Hassle-Free Media Management

Anyone who runs a self-hosted media server knows the pain of keeping everything organized, private, and automated. Torrents are great for grabbing content—but exposing your real IP, sorting files, or manually managing downloads? Not so great.

My goal: Build a system where **TV shows, movies, and audiobooks** download automatically, sort themselves, are always behind a VPN (with a kill switch!), and end up right where Jellyfin or Audiobookshelf expect them—on my Unraid NAS.

Here’s how I did it, the roadblocks I hit, and what I’d do differently.

---

## The Stack: Overview

* **Gluetun**: Containerized VPN with built-in kill switch for all torrent traffic
* **qBittorrent**: The torrent client, running *inside* the Gluetun network for privacy
* **Sonarr & Radarr**: TV/movie automation and renaming
* **Audiobookshelf**: For managing and streaming audiobooks
* **Unraid NAS**: Network storage for media libraries
* **Docker Compose**: Orchestrating it all

---

## Architecture

```
[Internet]
   │
[Gluetun VPN Container]
   │
[qBittorrent Container (network_mode: service:gluetun)]
   │
[Sonarr/Radarr/Audiobookshelf]
   │
[Unraid NAS SMB/NFS Shares]
```

---

## Implementation: Step by Step

### 1. Gluetun: VPN and Kill Switch

**Why Gluetun?**
Traditional VPN clients can leak traffic or break when the connection drops. Gluetun is a Docker container that proxies *all* network traffic of connected containers—no IP leaks, ever.

* VPN provider: Private Internet Access (PIA), NordVPN, etc.
* Runs as its own service in Docker Compose
* qBittorrent, Sonarr, and Radarr use Gluetun’s network stack for 100% traffic routing

**Sample Compose Block:**

```yaml
services:
  gluetun:
    image: qmcgaw/gluetun:latest
    cap_add:
      - NET_ADMIN
    environment:
      - VPN_SERVICE_PROVIDER=private internet access
      - OPENVPN_USER=<REDACTED>
      - OPENVPN_PASSWORD=<REDACTED>
      - SERVER_COUNTRIES=United States
    ports:
      - "8080:8080"  # qBittorrent Web UI
      - "8989:8989"  # Sonarr
      - "7878:7878"  # Radarr
    volumes:
      - ./gluetun:/gluetun
```

---

### 2. qBittorrent: The Engine

* Runs in the same network as Gluetun (`network_mode: service:gluetun`)
* Only accessible if VPN is up (kill switch)
* Downloads split into separate folders for TV, Movies, and Audiobooks
* Ports mapped through Gluetun (see above)

**Compose Block:**

```yaml
  qbittorrent:
    image: linuxserver/qbittorrent
    depends_on:
      - gluetun
    network_mode: "service:gluetun"
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
      - WEBUI_PORT=8080
    volumes:
      - /mnt/r430/media/torrents:/downloads
      - ./qbittorrent/config:/config
    restart: unless-stopped
```

---

### 3. Sonarr & Radarr: Automation & Renaming

* Monitor trackers for new TV episodes/movies
* Add torrents to qBittorrent via API
* Move and rename downloads to final folders (`/mnt/r430/media/tv`, `/mnt/r430/media/movies`)

**Compose Blocks:**

```yaml
  sonarr:
    image: linuxserver/sonarr
    network_mode: "service:gluetun"
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
    volumes:
      - /mnt/r430/media/tv:/tv
      - /mnt/r430/media/torrents:/downloads
      - ./sonarr/config:/config
    restart: unless-stopped

  radarr:
    image: linuxserver/radarr
    network_mode: "service:gluetun"
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
    volumes:
      - /mnt/r430/media/movies:/movies
      - /mnt/r430/media/torrents:/downloads
      - ./radarr/config:/config
    restart: unless-stopped
```

---

### 4. Audiobookshelf: Private Audible Alternative

* Pointed directly to `/mnt/r430/media/audiobooks` and `/mnt/r430/media/ebooks`
* Runs in its own Docker container (doesn’t need VPN)
* Accessible via Traefik reverse proxy and secured with Authelia

**Compose Block:**

```yaml
  audiobookshelf:
    image: ghcr.io/advplyr/audiobookshelf:latest
    container_name: audiobookshelf
    ports:
      - "13378:80"
    environment:
      - TZ=America/New_York
    volumes:
      - /mnt/r430/media/audiobooks:/audiobooks
      - /mnt/r430/media/ebooks:/ebooks
      - ./audiobookshelf/config:/config
      - ./audiobookshelf/metadata:/metadata
    restart: unless-stopped
```

---

### 5. Unraid NAS: The Central Media Hub

* All media folders are network shares on Unraid (`/mnt/r430/media/...`)
* Docker hosts mount these shares directly (CIFS/NFS)
* Keeps everything available to Jellyfin, Audiobookshelf, Paperless, etc.

---

## Troubles & Gotchas

* **VPN Flakiness:** Make sure your credentials don’t expire and you choose reliable endpoints (test speed!).
* **Permissions Hell:** All containers should run as the same user/group (PUID/PGID), or file moves will break.
* **Network Segmentation:** VLANs and Docker networking can cause service discovery issues—map only the ports you need!
* **Automation Gone Wild:** Use good indexers and filters in Sonarr/Radarr or you’ll wake up with terabytes of junk.
* **Disk Space:** Monitor your NAS space—automated downloads fill up fast!

---

## Lessons Learned

* **All traffic must go through Gluetun.** Any port mapped directly to the host bypasses the VPN. Be careful with Docker Compose syntax.
* **Use Unraid’s built-in share management** to keep file permissions sane and make it easy to back up or move libraries.
* **Keep your Compose files in Git.** If you break something, you can always revert.
* **Test restores, not just backups.**

---

## Config Reference

👉 For detailed, redacted Docker Compose and Unraid mount settings, check [my GitHub repo](https://github.com/yourusername/mediastack-example).

---

## Final Thoughts

This setup turned my media workflow from chaos into order. Now, *everything*—from the moment a show is released to when it appears in my media library—is automated, safe, and totally private.

If you’re self-hosting and tired of manual downloads or worrying about privacy, this Gluetun-centric pipeline is a game-changer.

*Questions or want a deep dive into Sonarr or permission setups? Drop a comment or check the GitHub!*
