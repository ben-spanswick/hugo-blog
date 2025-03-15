---
title: "Setting Up Hugo with Gitea, GitHub, and Cloudflare Pages"
date: 2025-03-15
tags: ["Hugo", "Cloudflare Pages", "Gitea", "GitHub", "Self-Hosting"]
categories: ["Tech", "Self-Hosting"]
draft: false
---

# Setting Up Hugo with Gitea, GitHub, and Cloudflare Pages

## Why Hugo?
Hugo is one of the fastest static site generators available, making it ideal for self-hosted and low-maintenance deployments. I wanted a simple, efficient way to publish content without dealing with databases or complex CMS setups. The goal was to maintain full control over the blog while using a streamlined deployment process.

## The Setup
I started with a local Hugo installation, managed through an internal **Gitea** instance for private version control. The blog needed to be public, though, so I mirrored the repository to **GitHub**, allowing **Cloudflare Pages** to handle automatic deployments. This approach keeps the primary repo internal while using GitHub as an intermediary for seamless publishing.

### **1. Installing Hugo**
I installed Hugo directly on my server:
```bash
apt install hugo
```
Then, I created the site structure:
```bash
hugo new site myblog
```

## **Using a Theme: Submodule Issues and Fixes**
Hugo themes are typically managed as Git submodules, which caused some headaches when syncing between Gitea and GitHub.

### **The Submodule Problem**
Initially, I added a theme as a submodule:
```bash
git submodule add https://github.com/CaiJimmy/hugo-theme-stack.git themes/stack
```
This worked locally, but Cloudflare Pages failed to build, throwing errors like:
```
fatal: No url found for submodule path 'themes/stack' in .gitmodules
```
This happened because GitHub wasn’t properly recognizing the submodule reference. Attempts to remove and re-add it using `git rm --cached` didn’t fully resolve the issue.

### **The Proper Fix**
The cleanest way to handle submodules for a public build was:
```bash
# Remove any broken references
git submodule deinit -f themes/stack
git rm --cached themes/stack
rm -rf .git/modules/themes/stack
rm -rf themes/stack

# Re-add as a proper submodule
git submodule add https://github.com/CaiJimmy/hugo-theme-stack.git themes/stack
git submodule update --init --recursive
git commit -m "Re-added Stack theme as a proper submodule"
git push origin main
```
Once this was done, Cloudflare Pages could properly clone the theme during its build process.

## **Configuring Cloudflare Pages**
With GitHub mirroring the repository, Cloudflare Pages handled automatic deployments.

1. **Connected the GitHub repo** to Cloudflare Pages.
2. Set the **build command** to:
   ```bash
   git submodule update --init --recursive && hugo --gc --minify
   ```
3. **Fixed Hugo Version Issues** – Cloudflare was running an outdated Hugo version by default, causing errors like:
   ```
   can't evaluate field Lastmod in type page.Site
   ```
   The fix was to **specify the correct Hugo version** in `package.json`:
   ```json
   {
       "engines": {
           "hugo": "0.118.2"
       }
   }
   ```
   This ensured Cloudflare Pages used a compatible version.

## **Adding a Custom Domain**
The final step was setting up a custom domain (`blog.spanswick.dev`).

1. **Added the domain in Cloudflare Pages** under `Custom Domains`.
2. Updated **DNS settings**:
   - Added a CNAME record pointing `blog.spanswick.dev` to `pages.dev`.
   - Enabled **proxied mode** for better performance and security.
3. Enabled **Full (Strict) SSL** to ensure HTTPS worked correctly.

## **Final Thoughts**
The final setup works smoothly:
- **Gitea** for internal version control.
- **GitHub** as a public mirror.
- **Cloudflare Pages** for automatic deployments.
- **Custom domain** for a professional look.

The biggest pain point was dealing with **submodules**—GitHub didn’t always handle them correctly, and Cloudflare’s default Hugo version was outdated. Once those were sorted, everything fell into place.

Going forward, I might explore additional integrations like **webhooks** to automatically push from Gitea to GitHub, removing the need for manual mirroring.
