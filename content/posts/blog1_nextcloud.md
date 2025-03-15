---
title: "Nextcloud Setup"
date: 2025-03-13T12:00:00-05:00
description: "This is my first blog post using Hugo and the Poison theme!"
tags: ["nextcloud", "services", "self-hosted"]
draft: false
---

# Building a Self-Hosted Nextcloud: Architecture, Setup, and Lessons Learned

## Introduction: How We Designed This Setup
When setting up Nextcloud, I wanted to **strike a balance between speed, scalability, and reliability** while keeping everything self-hosted. That meant carefully choosing **where to store each component** and how to optimize performance. Here's the structure I landed on:

1. **Nextcloud app runs on an SSD**  
   - The core application and web interface should be as fast as possible. Running Nextcloud on an LXC container stored on a local SSD ensures fast load times.
  
2. **PostgreSQL for database performance**  
   - Instead of MariaDB, I went with PostgreSQL, which offers better scalability and performance, especially when dealing with metadata-heavy queries.
   - The database is stored on an HDD pool, where I have plenty of storage but still decent IOPS for database operations.

3. **Large file storage on a separate HDD pool**  
   - Instead of storing everything on SSDs, I mounted an HDD-based ZFS pool for bulk file storage (videos, documents, backups). This keeps costs down while still being performant enough for Nextcloud’s use case.

4. **Backups scheduled to the NAS**  
   - In the near future, I plan to automate nightly rsync backups from the HDD pool to a separate NAS, ensuring redundancy and data safety.

With this approach, I get fast UI response times, efficient database operations, scalable storage for large files, and a solid backup plan.  

**Now, let's dive into how we built it.**

---

## Why Nextcloud?
Nextcloud is an open-source cloud storage platform that gives you complete control over your data. Unlike Google Drive or Dropbox, you aren’t locked into a proprietary ecosystem, and there are no monthly fees.  

Beyond just storing files, Nextcloud offers:
- **File synchronization across devices**
- **Built-in sharing and collaboration**
- **A growing ecosystem of apps** (e.g., calendar, tasks, media streaming)
- **Advanced security features** (encryption, 2FA, remote wipe)

For a homelab or self-hosted setup, **it’s one of the best tools available.**

---

## How We Set It Up

### 1. Choosing TurnKey LXC for Simplicity
Rather than manually installing Apache, PHP, and configuring everything from scratch, I opted for a **TurnKey Linux (TKL) LXC container**. The benefits:
- Comes with **Nextcloud pre-installed**  
- **Pre-configured Apache, PHP, and Redis**
- **Automated security updates**  

**Why an LXC instead of a VM?**  
LXCs are **more lightweight and efficient** than a full virtual machine. Since they share the Proxmox kernel, they **use fewer system resources** while still maintaining isolation.

**Resources Allocated:**
- **4 vCPUs** – To handle Nextcloud’s PHP and web requests efficiently.
- **8GB RAM** – Since Nextcloud benefits from caching, more RAM helps.
- **8GB SSD root disk** – Only the core OS and application live here.

---

### 2. Using PostgreSQL Instead of MariaDB
Nextcloud supports **both MariaDB and PostgreSQL**, but PostgreSQL is **better for high-concurrency workloads** and provides **stronger ACID compliance**.

**Why PostgreSQL?**
- **Handles concurrent users better** – More efficient transaction management.
- **Better JSON & search performance** – Useful for Nextcloud's metadata queries.
- **More robust scaling** – PostgreSQL handles larger datasets with ease.

#### Setting Up PostgreSQL
We installed it in a **separate LXC container**:
```bash
apt install -y postgresql
```
Then created a **Nextcloud-specific database**:
```bash
sudo -u postgres psql
CREATE DATABASE nextcloud;
CREATE USER user WITH PASSWORD 'supersecurepassword';
ALTER DATABASE nextcloud OWNER TO mandrake;
```
Finally, we pointed Nextcloud to use the external database server at `192.168.xxx.xxx`.

---

### 3. Separating File Storage: SSD for System, HDD for Data
Storing Nextcloud’s **entire dataset on SSDs** is overkill—especially for **large media files** that don’t need instant access speeds.

#### Our Storage Breakdown:
- **SSD (local-zfs):** Hosts the LXC container and Nextcloud application.
- **HDD Pool (r430pool):** Stores Nextcloud user files (documents, videos, etc.).
- **NAS Backup (future upgrade):** Will hold nightly snapshots of the data.

This ensures the **UI stays fast**, while **bulk storage remains cost-effective**.

#### How We Mounted the HDD Pool in Nextcloud LXC
First, we created a **ZFS dataset** for Nextcloud data:
```bash
zfs create -o mountpoint=/mnt/r430pool/nextcloud r430pool/nextcloud
```
Then, we **mounted it inside the LXC container**:
```bash
nano /etc/pve/lxc/101.conf
```
Added:
```
mp0: /mnt/r430pool/nextcloud,mp=/mnt/nextcloud
```
Finally, we moved Nextcloud’s data:
```bash
rsync -av /var/www/nextcloud/data/ /mnt/nextcloud/
```

---

### 4. Caching for Performance: Redis & APCu
Caching **reduces database queries** and **makes Nextcloud feel more responsive**.

#### **What APCu Does**
- **APCu (Alternative PHP Cache)** speeds up Nextcloud by **caching PHP objects and session data in memory**.
- This prevents Nextcloud from constantly hitting the database for **frequently accessed metadata**.

#### **What Redis Does**
- **Redis is an in-memory key-value store** that Nextcloud uses for **file locking**.
- Without Redis, Nextcloud relies on **database locks**, which slow things down.
- Redis ensures **simultaneous users don’t interfere with each other’s file operations**.

#### Installing Redis & APCu
```bash
apt install -y redis-server php-redis php-apcu
```
Then, we updated `config.php`:
```php
'memcache.local' => '\OC\Memcache\APCu',
'memcache.locking' => '\OC\Memcache\Redis',
'redis' => array(
    'host' => 'localhost',
    'port' => 6379,
    'timeout' => 0.0,
),
```
This dramatically **improves Nextcloud’s performance**.

---

## Next Steps & Future Improvements
- **Automated Nightly Backups**
  ```bash
  rsync -av /mnt/nextcloud/ /mnt/nas/backups/nextcloud/
  ```
- **Setting Up an SMTP Server for Notifications**

---

## Final Thoughts
This setup gives us:
- **Fast performance** (SSD for app, Redis caching)  
- **Scalable storage** (HDD pool for bulk files)  
- **Reliability** (PostgreSQL, separate DB & app containers)  

Next steps? **Automating backups, adding SMTP email alerts, and possibly integrating OnlyOffice for document editing.**
