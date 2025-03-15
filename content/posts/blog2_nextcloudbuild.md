---
title: "Building a Self-Hosted Nextcloud: Detailed Setup"
date: 2025-03-13T12:00:00-05:00
description: "A deep dive into building a self-hosted Nextcloud for scalability, speed, and reliability."
tags: ["nextcloud", "self-hosting", "homelab", "storage"]
draft: false
---

# Nextcloud LXC Setup Guide (Step-by-Step)

## 1. Install the TurnKey Nextcloud LXC
```bash
pct create 101 local:vztmpl/turnkey-nextcloud-18.0-buster-amd64.tar.gz --storage local-zfs --hostname NextCloud --memory 8000 --cores 4
pct start 101
```

---

## 2. Install PostgreSQL in a Separate LXC
```bash
apt update && apt install -y postgresql
systemctl enable --now postgresql
```

### Create the Nextcloud Database
```bash
sudo -u postgres psql
CREATE DATABASE nextcloud;
CREATE USER nextclouduser WITH PASSWORD 'REDACTED';
ALTER DATABASE nextcloud OWNER TO nextclouduser;
\q
```

---

## 3. Mount HDD Pool for Nextcloud Data

### On Proxmox Host:
```bash
zfs create -o mountpoint=/mnt/r430pool/nextcloud r430pool/nextcloud
```

### Bind to LXC:
```bash
nano /etc/pve/lxc/101.conf
```
Add:
```
mp0: /mnt/r430pool/nextcloud,mp=/mnt/nextcloud
```

### Fix Permissions:
```bash
chown -R 101033:101033 /mnt/r430pool/nextcloud
```

---

## 4. Move Nextcloud Data to HDD Storage
```bash
systemctl stop apache2
rsync -av /var/www/nextcloud/data/ /mnt/nextcloud/
```

Update `config.php`:
```php
'datadirectory' => '/mnt/nextcloud',
```

Restart:
```bash
systemctl restart apache2
```

---

## 5. Install Redis & APCu for Caching
```bash
apt install -y redis-server php-redis php-apcu
systemctl restart apache2
```

Update `config.php`:
```php
'memcache.local' => '\OC\Memcache\APCu',
'memcache.locking' => '\OC\Memcache\Redis',
'redis' => array(
    'host' => 'localhost',
    'port' => 6379,
    'timeout' => 0.0,
),
```

---

## 6. Verify & Optimize Nextcloud Setup

### Check Nextcloud Status:
```bash
su - www-data -s /bin/bash -c 'php /var/www/nextcloud/occ status'
```

### Scan for Missing Files:
```bash
su - www-data -s /bin/bash -c 'php /var/www/nextcloud/occ files:scan --all'
```

### Optimize Database:
```bash
su - www-data -s /bin/bash -c 'php /var/www/nextcloud/occ db:add-missing-indices'
```

---

## 7. Configure Backups (Upcoming)
```bash
rsync -av /mnt/nextcloud/ /mnt/nas/backups/nextcloud/
```

---

# Redacted Configuration Files

## `/etc/pve/lxc/101.conf`
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

## `/var/www/nextcloud/config/config.php` (Redacted)
```php
<?php
$CONFIG = array (
  'trusted_domains' => 
  array (
    0 => 'localhost',
    1 => '192.168.X.X',
  ),
  'datadirectory' => '/mnt/nextcloud',
  'dbtype' => 'pgsql',
  'dbname' => 'nextcloud',
  'dbhost' => '192.168.X.X',
  'dbuser' => 'REDACTED',
  'dbpassword' => 'REDACTED',
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

---

This guide covers the **full Nextcloud LXC installation**, database setup, performance tuning, and data storage migration to an HDD pool.
