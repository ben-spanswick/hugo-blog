---
title: "Nextcloud Setup"
date: 2025-03-13T12:00:00-05:00
description: "This is my first blog post using Hugo and the Poison theme!"
tags: ["nextcloud", "services", "self-hosted"]
draft: false
---

# My Nextcloud Architecture: What I Learned Building a Proper Self-Hosted Setup

*Designing for performance, scalability, and sanity*

---

After running a janky Nextcloud install for way too long, I finally sat down to build something proper. The old setup was slow, unstable, and honestly kind of embarrassing when I'd try to share files with people. Time for a complete rebuild.

I spent a lot of time thinking about the architecture before diving in. Most Nextcloud guides just throw everything on one machine and call it done, but I wanted something that would actually scale and perform well. Here's what I came up with and why.

## The Architecture: Splitting Things Up Smart

### Fast App, Cheap Storage

The core insight was realizing that not everything needs the same performance profile. The Nextcloud application itself - all that PHP code handling web requests - needs to be snappy. But the actual files? A vacation video from three years ago doesn't need NVMe speeds.

So I split things up:

**Nextcloud app lives on SSD** - The core application runs in an LXC container on local SSD storage. This keeps the web interface responsive and file operations quick.

**PostgreSQL gets its own space** - Database runs separately with enough resources to handle concurrent users without choking. I went with PostgreSQL instead of the usual MySQL/MariaDB choice for reasons I'll get into.

**Bulk storage on HDD pool** - All the actual user files live on a ZFS pool built from cheaper spinning disks. Still plenty fast for streaming videos or downloading documents, but way more cost-effective.

**Backups go to the NAS** - Eventually. I'm still working on automating this part, but the plan is nightly snapshots to a separate machine.

This approach gives me fast UI response times without breaking the bank on storage costs.

## Why Nextcloud Over Everything Else?

I looked at a bunch of options - ownCloud, Seafile, even just running straight WebDAV. But Nextcloud hit the sweet spot of features vs complexity.

The file sync works reliably across all my devices, the sharing features are actually usable, and there's a decent ecosystem of apps for calendars, tasks, and other stuff. Plus it's actively developed and has good community support.

Most importantly, I own all my data. No more wondering if Google is going to kill another service or if Dropbox is going to change their pricing again.

## The Technical Decisions

### TurnKey LXC: Standing on Shoulders

I could have built everything from scratch, but why reinvent the wheel? The TurnKey Linux Nextcloud template comes with everything pre-configured - Apache, PHP, Redis, security hardening, the works.

LXC over VM was a no-brainer. Same isolation benefits but way less overhead. Why waste RAM on a full kernel when you don't need it?

I gave it 4 vCPUs and 8GB of RAM. Might seem like overkill, but Nextcloud actually benefits from having resources available for caching and concurrent operations.

### PostgreSQL: The Database Choice

This one might be controversial. Most Nextcloud setups use MariaDB, and it works fine. But I went with PostgreSQL for a few reasons:

**Better concurrency handling** - When multiple people are accessing files simultaneously, PostgreSQL's MVCC system handles it more gracefully.

**JSON performance** - Nextcloud stores a lot of metadata, and PostgreSQL's JSON operations are genuinely faster.

**Personal preference** - I've had fewer weird issues with PostgreSQL over the years. Call it superstition if you want.

Setting it up was straightforward:

```bash
apt install -y postgresql
```

Create the database:

```bash
sudo -u postgres psql
CREATE DATABASE nextcloud;
CREATE USER nextclouduser WITH PASSWORD 'your-secure-password';
ALTER DATABASE nextcloud OWNER TO nextclouduser;
```

Point Nextcloud at the external database server and done.

### Storage Strategy: SSD Where It Matters

Here's where most people get it wrong. They either put everything on expensive SSD storage, or they put everything on cheap HDDs and wonder why their Nextcloud feels sluggish.

The trick is being strategic about it:

**SSD hosts the application** - All the PHP code, temporary files, and active caching live on fast local storage.

**HDD pool for user data** - Documents, photos, videos - all the stuff that doesn't need millisecond access times but does need lots of space.

Setting up the HDD mount was pretty standard ZFS stuff:

```bash
zfs create -o mountpoint=/mnt/r430pool/nextcloud r430pool/nextcloud
```

Then mount it in the LXC:

```bash
nano /etc/pve/lxc/101.conf
```

Add:
```
mp0: /mnt/r430pool/nextcloud,mp=/mnt/nextcloud
```

Move the data over:

```bash
rsync -av /var/www/nextcloud/data/ /mnt/nextcloud/
```

Update the config to point to the new location and restart. The performance difference is immediately noticeable.

### Caching: Making It Actually Fast

Default Nextcloud can feel pretty sluggish, especially with lots of files. The solution is proper caching at multiple levels.

**APCu for local caching** - Keeps frequently accessed PHP objects in memory instead of hitting the database constantly.

**Redis for file locking** - Prevents users from stepping on each other when accessing the same files. Way faster than database-based locks.

Installation:

```bash
apt install -y redis-server php-redis php-apcu
```

Configuration in `config.php`:

```php
'memcache.local' => '\OC\Memcache\APCu',
'memcache.locking' => '\OC\Memcache\Redis',
'redis' => array(
    'host' => 'localhost',
    'port' => 6379,
    'timeout' => 0.0,
),
```

The difference is honestly dramatic. Operations that used to take 5-10 seconds now happen almost instantly.

## What's Working Well

After running this setup for several months, I'm pretty happy with the results:

**Performance is solid** - Web interface is responsive, file operations are quick, multiple users don't slow each other down.

**Storage scaling works** - I can add more HDDs to the pool without touching the application layer.

**Maintenance is minimal** - The TurnKey base handles security updates automatically, and the modular design means I can update components independently.

**Costs are reasonable** - Most of the storage is on cheap HDDs, with SSD only where it actually matters.

## Still To Do

**Automated backups** - I've got the basic rsync command figured out, just need to script it and set up monitoring:

```bash
rsync -av /mnt/nextcloud/ /mnt/nas/backups/nextcloud/
```

**SMTP integration** - Would be nice to get email notifications working for shares and password resets.

**OnlyOffice maybe** - The built-in document editing is pretty basic. Might be worth setting up a proper office suite integration.

## Lessons Learned

**Architecture matters more than hardware** - Splitting components based on their performance needs gave me way better results than just throwing faster hardware at a monolithic setup.

**Don't skimp on the database** - PostgreSQL in its own container with proper resources makes everything feel more responsive.

**Caching is not optional** - Redis and APCu turned a sluggish system into something that actually feels professional.

**Plan for growth** - The modular approach means I can easily add more storage, upgrade components, or even migrate to different hardware without rebuilding everything.

The whole thing took longer to plan than to implement, but it was worth taking the time to think through the architecture first. Way better than my usual "build it and see what breaks" approach.

---

*Next project: figuring out why my backup script keeps failing at 3 AM. There's always something.*
