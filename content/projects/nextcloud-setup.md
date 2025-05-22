---
title: "Building a Self-Hosted Nextcloud: Detailed Setup"
date: 2025-03-13T12:00:00-05:00
description: "A deep dive into building a self-hosted Nextcloud for scalability, speed, and reliability."
tags: ["nextcloud", "self-hosting", "homelab", "storage"]
draft: false
---

# Building a Proper Nextcloud Setup in Proxmox LXC

*How I got Nextcloud running smoothly without losing my mind (mostly)*

---

So I finally decided to bite the bullet and set up my own Nextcloud instance. I've been putting this off for months, but I got tired of paying for three different cloud storage services while having zero control over my data. Time to bring everything home.

I wanted something that would actually perform well and not feel sluggish like some Nextcloud instances I've used before. That meant doing it right from the start: separate database, proper caching, and decent storage. Here's how it all came together.

## Starting with the TurnKey Template

Instead of building everything from scratch, I went with the TurnKey Nextcloud template. It's basically a pre-configured Nextcloud setup that saves you from dealing with all the initial Apache and PHP configuration headaches.

```bash
pct create 101 local:vztmpl/turnkey-nextcloud-18.0-buster-amd64.tar.gz --storage local-zfs --hostname NextCloud --memory 8000 --cores 4
pct start 101
```

I gave it 8GB of RAM and 4 cores because I didn't want to be stingy and then regret it later. Storage performance matters way more for Nextcloud than most people realize.

## Database: Don't Use SQLite

This is where a lot of people go wrong. The default SQLite setup is fine for testing, but if you actually want decent performance, you need a proper database. I went with PostgreSQL in its own LXC container.

```bash
apt update && apt install -y postgresql
systemctl enable --now postgresql
```

Then set up the database for Nextcloud:

```bash
sudo -u postgres psql
CREATE DATABASE nextcloud;
CREATE USER nextclouduser WITH PASSWORD 'your-secure-password-here';
ALTER DATABASE nextcloud OWNER TO nextclouduser;
\q
```

Yeah, I know MySQL is more common for this stuff, but PostgreSQL just feels more robust. Plus it handles concurrent connections better, which actually matters when you've got multiple devices constantly syncing files.

## Storage: Getting the Data Off the Boot Drive

Here's something most guides don't emphasize enough - Nextcloud is going to store a *lot* of data, and you definitely don't want that filling up your main system drive. I've got a separate HDD pool for bulk storage, so that's where the actual files need to live.

### Setting Up the ZFS Dataset

On the Proxmox host:

```bash
zfs create -o mountpoint=/mnt/r430pool/nextcloud r430pool/nextcloud
```

### Mounting in the LXC

Edit the container config:

```bash
nano /etc/pve/lxc/101.conf
```

Add this line:

```
mp0: /mnt/r430pool/nextcloud,mp=/mnt/nextcloud
```

### The Permissions Dance

This is where unprivileged LXC containers get annoying. The UIDs don't match up, so you have to manually fix permissions:

```bash
chown -R 101033:101033 /mnt/r430pool/nextcloud
```

That 101033 is the mapped UID for the www-data user inside the container. Took me way too long to figure that out the first time.

## Moving Nextcloud's Data Directory

With the storage mounted, I needed to actually move Nextcloud's data to the new location. This is one of those "stop everything first" operations:

```bash
systemctl stop apache2
rsync -av /var/www/nextcloud/data/ /mnt/nextcloud/
```

Then update the config file (`/var/www/nextcloud/config/config.php`):

```php
'datadirectory' => '/mnt/nextcloud',
```

Start it back up:

```bash
systemctl restart apache2
```

At this point I was crossing my fingers that I didn't break anything. Spoiler alert: it worked fine.

## Performance: Caching Makes Everything Better

Default Nextcloud can feel pretty sluggish, especially with lots of files. The solution is proper caching. I installed Redis for file locking and APCu for local caching:

```bash
apt install -y redis-server php-redis php-apcu
systemctl restart apache2
```

Then updated the config:

```php
'memcache.local' => '\OC\Memcache\APCu',
'memcache.locking' => '\OC\Memcache\Redis',
'redis' => array(
    'host' => 'localhost',
    'port' => 6379,
    'timeout' => 0.0,
),
```

The difference is night and day. File operations that used to take forever now happen almost instantly.

## Making Sure Everything Actually Works

After all this setup, I wanted to verify things were actually working properly:

### Check the status:
```bash
su - www-data -s /bin/bash -c 'php /var/www/nextcloud/occ status'
```

### Scan for any missing files:
```bash
su - www-data -s /bin/bash -c 'php /var/www/nextcloud/occ files:scan --all'
```

### Optimize the database:
```bash
su - www-data -s /bin/bash -c 'php /var/www/nextcloud/occ db:add-missing-indices'
```

That last one is important - Nextcloud sometimes misses database indices during setup, and they make a huge difference for performance.

## Backup Strategy (Work in Progress)

I'm still working on a proper backup strategy, but the basic idea is:

```bash
rsync -av /mnt/nextcloud/ /mnt/nas/backups/nextcloud/
```

Obviously you need to backup the database and config files too, but that's the bulk of the data right there.

## The Final Configuration

Here's what my setup looks like now:

**LXC Config** (`/etc/pve/lxc/101.conf`):
```conf
arch: amd64
cores: 4
features: nesting=1
hostname: NextCloud
memory: 8000
mp0: /mnt/r430pool/nextcloud,mp=/mnt/nextcloud
net0: name=eth0,bridge=vmbr0,firewall=1,hwaddr=XX:XX:XX:XX:XX:XX,ip=dhcp,type=veth
ostype: debian
rootfs: local-zfs:subvol-101-disk-0,size=8G
swap: 8000
unprivileged: 1
```

**Nextcloud Config** (the important bits):
```php
<?php
$CONFIG = array (
  'trusted_domains' =>
  array (
    0 => 'localhost',
    1 => '192.168.1.100', // your actual IP
  ),
  'datadirectory' => '/mnt/nextcloud',
  'dbtype' => 'pgsql',
  'dbname' => 'nextcloud',
  'dbhost' => '192.168.1.101', // database server IP
  'dbuser' => 'nextclouduser',
  'dbpassword' => 'your-secure-password',
  'installed' => true,
  'memcache.local' => '\OC\Memcache\APCu',
  'memcache.locking' => '\OC\Memcache\Redis',
  'redis' => array(
      'host' => 'localhost',
      'port' => 6379,
      'timeout' => 0.0,
  ),
);
```

## How It's Working Out

The whole setup has been running for a few months now and I'm pretty happy with it. File sync is fast, the web interface is responsive, and I haven't had any data corruption issues.

The separate database was definitely worth the extra complexity - queries that used to take forever now happen instantly. And having the data on proper storage means I'm not worried about running out of space or wearing out an SSD.

If I were doing it again, I might look into setting up the database as a cluster for redundancy, but for a home setup, this is working great.

The main lesson learned? Don't skimp on the infrastructure. A little extra work upfront makes everything so much better in the long run.

---

*Next up: figuring out a proper automated backup strategy. Because nothing lasts forever, and I really don't want to lose all my photos again.*
