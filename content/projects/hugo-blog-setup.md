---
title: "Setting Up Hugo with Gitea, GitHub, and Cloudflare Pages"
date: 2025-03-15
tags: ["Hugo", "Cloudflare Pages", "Gitea", "GitHub", "Self-Hosting"]
categories: ["Tech", "Self-Hosting"]
draft: false
---

# Getting My Blog Actually Working: Hugo + Gitea + GitHub + Cloudflare Pages

*Or: How I learned to stop worrying and love Git submodules (eventually)*

---

So I finally got tired of not having a proper blog. You know how it is - you keep meaning to write stuff down, maybe share some of the things you've figured out, but then you get stuck on the whole "where do I even host this thing" question for like six months.

I'd been running other services in my homelab, so naturally I wanted to keep control of my content while still making it easy to publish. After way too much research (and a few false starts), I ended up with Hugo feeding into a pretty slick deployment pipeline. Here's how it all came together.

## Why Hugo Though?

Honestly? Speed and simplicity. I've dealt with WordPress before and while it's powerful, I really didn't want to babysit another database or worry about security updates for a CMS. Hugo just takes markdown files and spits out a static site that loads crazy fast.

Plus, the whole "write in markdown, commit to git, site updates automatically" workflow really appealed to the developer side of my brain. No admin panels, no databases, just files and version control.

## The Setup (Spoiler: It Got Complicated)

My plan seemed reasonable enough:
- Keep the main repo in my internal Gitea instance (because I like having control)
- Mirror it to GitHub (because that's what Cloudflare Pages wants to see)
- Let Cloudflare handle the building and hosting (because why reinvent that wheel)

Simple, right? *Narrator: It was not simple.*

### Getting Hugo Running

The basic setup was actually painless. On my server:

```bash
apt install hugo
```

Create the site structure:

```bash
hugo new site myblog
```

So far so good. Then I needed a theme, and that's where things got... interesting.

## The Great Submodule Adventure

Hugo themes are typically managed as Git submodules, which sounds great in theory. In practice? Well, let me tell you about my afternoon of increasingly creative swearing.

### What I Tried First

I found a theme I liked (hugo-theme-stack) and added it the "normal" way:

```bash
git submodule add https://github.com/CaiJimmy/hugo-theme-stack.git themes/stack
```

Worked perfectly locally. Hugo was happy, the site looked good, everything was great. Then I pushed to GitHub and tried to deploy with Cloudflare Pages.

```
fatal: No url found for submodule path 'themes/stack' in .gitmodules
```

Great. Just great.

### The Rabbit Hole

This is where I spent way too much time trying different variations of `git rm --cached` and `git submodule deinit` and generally making things worse. Turns out GitHub was getting confused about the submodule reference, and Cloudflare couldn't clone the theme during builds.

I probably could have saved myself two hours by just reading the error message more carefully, but where's the fun in that?

### What Actually Fixed It

Eventually I just nuked the whole thing and started over:

```bash
# Burn it all down
git submodule deinit -f themes/stack
git rm --cached themes/stack
rm -rf .git/modules/themes/stack
rm -rf themes/stack

# Start fresh
git submodule add https://github.com/CaiJimmy/hugo-theme-stack.git themes/stack
git submodule update --init --recursive
git commit -m "Re-added Stack theme as a proper submodule"
git push origin main
```

This time it actually worked. Sometimes the nuclear option is the right option.

## Getting Cloudflare Pages to Cooperate

With the submodule situation sorted, setting up Cloudflare Pages should have been straightforward. Should have been.

I connected my GitHub repo to Cloudflare and set the build command:

```bash
git submodule update --init --recursive && hugo --gc --minify
```

First build attempt: failed. The error was something about field evaluation, which led me down another fun debugging path.

### The Hugo Version Problem

Turns out Cloudflare Pages was running some ancient version of Hugo by default. My theme needed newer features, so I was getting errors like:

```
can't evaluate field Lastmod in type page.Site
```

The fix was adding a `package.json` file to specify the Hugo version:

```json
{
    "engines": {
        "hugo": "0.118.2"
    }
}
```

Why this isn't documented more prominently, I have no idea. But once I added that, builds started working.

## Custom Domain Setup

The last piece was getting my custom domain (`blog.spanswick.dev`) working properly. This part was actually straightforward for once:

1. Added the domain in Cloudflare Pages under Custom Domains
2. Set up DNS with a CNAME record pointing to the pages.dev URL
3. Enabled proxy mode for better performance
4. Set SSL to Full (Strict) because why not

And... it worked. First try. I was almost disappointed by how easy it was after everything else.

## What I Learned

The final workflow is actually pretty nice:
- I write posts in markdown and commit to my Gitea instance
- Push to GitHub (manual for now, but I might automate this)
- Cloudflare automatically builds and deploys
- Everything just works

The main lessons:
- **Git submodules are finicky** but they do work once you get them right
- **Version pinning matters** - don't assume the build environment has what you need
- **Sometimes starting over is faster** than trying to fix a broken git state
- **Read error messages carefully** (I'm still working on this one)

## What's Next?

I'm pretty happy with how this turned out. The writing experience is smooth, deployment is automatic, and I don't have to worry about keeping a CMS updated.

I might add webhooks to automatically sync from Gitea to GitHub, just to remove that manual step. But honestly, the current setup works well enough that I'm not in a rush to complicate it further.

Plus, now I actually have a place to write about all the other stuff I've been tinkering with. Mission accomplished, I guess.

---

*If you're trying to do something similar and get stuck on the submodule thing, just remember: when in doubt, nuke it and start over. Sometimes that's genuinely the fastest path forward.*
