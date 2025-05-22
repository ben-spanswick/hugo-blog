---
title: "From Torrent to Library: Automating TV, Movies, and Audiobooks with Gluetun, qBittorrent, and arr"
date: 2025-05-14T13:00:00-04:00
description: "How I built a private, automated media pipeline with bulletproof VPN, container orchestration, and seamless syncing to Unraid."
categories: ["homelab", "self-hosting", "privacy"]
tags: ["homelab", "self-hosting", "torrenting", "automation", "gluetun", "qbittorrent", "sonarr", "radarr", "audiobookshelf", "unraid"]
draft: false
------------

# Building My Perfect Media Automation Pipeline

*How I stopped manually managing downloads and built a self-running media server*

Posted: May 14, 2025 | ~11 minute read

---

I got tired of the constant dance. Download something, figure out where it went, rename it properly, move it to the right folder, update the media server. Rinse and repeat, dozens of times a week. There had to be a better way.

What I really wanted was dead simple: new episodes show up automatically, everything gets organized correctly, and most importantly, my ISP never sees what I'm actually downloading. After months of tinkering, I finally have a setup that just works.

## What I Built

The core idea is a fully automated pipeline that handles everything from search to final organization, all running behind a VPN with proper kill switches. Here's what happens now:

1. Sonarr/Radarr monitor for new releases
2. They automatically grab torrents through qBittorrent
3. Everything downloads through a VPN (Gluetun) with zero IP leaks
4. Files get renamed and sorted automatically
5. Media shows up in Jellyfin ready to stream

No manual intervention required. It's honestly a bit magical when it works right.

## The Technical Stack

**Gluetun** - This is the secret sauce. It's a VPN container that other containers can route through. No VPN leaks, ever.

**qBittorrent** - The actual torrent client, but locked inside Gluetun's network

**Sonarr & Radarr** - The automation brains for TV and movies respectively

**Audiobookshelf** - Because I got tired of Audible's limitations

**Unraid NAS** - Where everything actually lives

The architecture looks like this:

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

## The VPN Foundation: Gluetun

Most VPN setups are sketchy. They work until they don't, and then your real IP gets exposed while downloading the latest season of whatever. Gluetun solves this by creating a container that other services route through. If the VPN goes down, nothing gets through. Period.

I'm using Private Internet Access because their pricing is decent and they don't keep logs (allegedly). The setup looks like this:

```yaml
services:
  gluetun:
    image: qmcgaw/gluetun:latest
    cap_add:
      - NET_ADMIN
    environment:
      - VPN_SERVICE_PROVIDER=private internet access
      - OPENVPN_USER=your-username
      - OPENVPN_PASSWORD=your-password
      - SERVER_COUNTRIES=United States
    ports:
      - "8080:8080"  # qBittorrent Web UI
      - "8989:8989"  # Sonarr
      - "7878:7878"  # Radarr
    volumes:
      - ./gluetun:/gluetun
```

The key insight is that all the web UI ports get mapped through the Gluetun container. This way, if the VPN is down, nothing is accessible.

## The Download Engine: qBittorrent

qBittorrent runs inside Gluetun's network namespace, which means it literally cannot access the internet without the VPN being up. This is way more reliable than trying to configure a VPN client inside the container.

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

The `network_mode: "service:gluetun"` line is crucial - that's what locks qBittorrent inside the VPN tunnel.

## The Automation Layer: Sonarr and Radarr

These are the tools that actually make everything automatic. They monitor RSS feeds and indexers for new releases, then tell qBittorrent what to download. Once something finishes downloading, they handle the renaming and moving to final folders.

Sonarr handles TV shows:

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
```

Radarr does the same thing for movies:

```yaml
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

Both also run through the VPN, though this is arguably overkill since they're just managing files locally.

## Audiobooks: Breaking Free from Audible

I got sick of Audible's limitations and DRM nonsense, so I added Audiobookshelf to the mix. It's like having your own private audiobook streaming service.

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

This one doesn't need the VPN since it's just serving files that are already local.

## Storage: The Unraid Foundation

Everything lives on my Unraid NAS, shared out via SMB. The Docker containers mount these shares directly:

- `/mnt/r430/media/torrents` - Downloads staging area
- `/mnt/r430/media/tv` - Final TV show library
- `/mnt/r430/media/movies` - Final movie library  
- `/mnt/r430/media/audiobooks` - Audiobook collection

This keeps everything centralized and accessible to other services like Jellyfin.

## What Goes Wrong (And How to Fix It)

**VPN Connection Issues** - Your VPN provider matters. Some have terrible reliability or throttle torrent traffic. I've had good luck with PIA, but YMMV.

**Permission Nightmares** - Make sure all containers run with the same PUID/PGID (1000/1000 in my case). Otherwise file moves between containers will fail spectacularly.

**Network Complexity** - Docker networking plus VLANs plus VPNs can get weird. Keep it simple - only expose the ports you actually need.

**Storage Explosion** - Automated downloads can fill up drives fast. Set up monitoring and maybe some cleanup scripts.

**Quality Control** - Without good filters, you'll end up with terabytes of garbage. Spend time configuring quality profiles in Sonarr/Radarr.

## Lessons from the Trenches

**Test your kill switch** - Disconnect your VPN and make sure nothing leaks. I use https://ipleak.net from inside the qBittorrent container.

**Version control your configs** - Keep your Docker Compose files in Git. When (not if) you break something, you can roll back easily.

**Monitor disk space** - Automated downloads are great until they fill your array at 3 AM.

**Good indexers matter** - The quality of your automation is only as good as your sources. Invest in decent private trackers if you can.

**Backup your configs** - Losing your Sonarr/Radarr database means re-adding everything manually. Not fun.

## The Results

After running this for about six months, I'm genuinely happy with how it's working out. New episodes just appear in Jellyfin without me thinking about it. Movies I want to watch show up automatically. Audiobooks sync across all my devices.

The privacy aspect gives me peace of mind - there's literally no way for downloads to happen without the VPN being active. Even if something goes wrong with the VPN connection, everything just stops rather than falling back to my real IP.

Performance has been solid too. The VPN overhead is minimal, and having everything automated means the system stays busy during off-peak hours when bandwidth is cheap.

## Worth the Complexity?

For me, absolutely. The initial setup took a weekend of tinkering, but now I spend maybe 5 minutes a month managing the whole system. Compare that to the hours I used to spend manually downloading and organizing files.

The main downside is complexity - there are a lot of moving parts, and troubleshooting can be tricky when something breaks. But the time savings and peace of mind make it worthwhile.

If you're already comfortable with Docker and have a decent understanding of networking, this setup isn't too bad to replicate. If you're just getting started with self-hosting, maybe begin with something simpler and work your way up.

## What's Next

I'm considering adding Prowlarr to manage indexers more centrally, and maybe Bazarr for subtitle automation. The setup is modular enough that adding new components is pretty straightforward.

I also want to improve the monitoring - knowing when things break before they affect the end user experience would be nice.

Overall though, this has been one of my more successful homelab projects. It solves a real problem and actually stays working once you get it configured properly.

---

*If you're curious about specific configuration details or run into issues setting this up, I've got the full Docker Compose files and notes in my GitHub repo. Just search for my username and "media-automation" or something similar.*
