---
title: "Getting My Blog Actually Working: Hugo + Gitea + GitHub + Cloudflare Pages"
description: "A real-world walkthrough of setting up Hugo with Git submodules, including all the frustrating parts they don't tell you about."
date: 2024-09-02T14:30:00-04:00
draft: false
tags: ["Hugo", "DevOps", "Blogging", "Git", "Cloudflare"]
categories: ["Guides", "Self-Hosting"]
image: "/img/head/hugo.png"
---

### AI Summary

- Setting up Hugo with Gitea, GitHub, and Cloudflare Pages turned into a multi-hour debugging adventure
- Git submodules are finicky - sometimes nuking and starting over is faster than fixing broken states
- Version pinning matters for Hugo builds on Cloudflare Pages (add a package.json with Hugo version)
- The final workflow is actually clean: write in markdown, commit to Git, automatic deployment

---

### The Itch Finally Got Scratched

So I finally got tired of not having a proper blog. You know that feeling - thoughts pile up, insights accumulate, little discoveries happen in your homelab, and you keep thinking "I should write this down somewhere people might actually find it useful."

But then you hit the eternal question: *where do I even host this thing?*

I'd been running other services in my homelab, so naturally I wanted to keep control of my content while still making it easy to publish. After way too much research and a few spectacular false starts, I ended up with Hugo feeding into what turned out to be a pretty elegant deployment pipeline.

Here's how it all came together - including the parts where I wanted to throw my laptop out the window.

### Why Hugo Made Sense

Speed and simplicity won me over. I've dealt with WordPress before, and while it's undeniably powerful, I really didn't want to babysit another database or worry about security updates for a CMS that's probably overkill for what I need.

Hugo just takes markdown files and spits out a static site that loads insanely fast. The whole *write in markdown, commit to git, site updates automatically* workflow appealed to the developer side of my brain. No admin panels, no databases, just files and version control.

Sometimes the simplest path is the right path.

### The Setup That Got Complicated Fast

My plan seemed reasonable enough:

- Keep the main repo in my internal Gitea instance (because I like having control)
- Mirror it to GitHub (because that's what Cloudflare Pages wants to see)  
- Let Cloudflare handle the building and hosting (because why reinvent that wheel)

Simple, right? 

*Narrator: It was not simple.*

### Getting Hugo Running (The Easy Part)

The basic setup was actually painless. On my server:

```bash
apt install hugo
hugo new site myblog
```

So far so good. Then I needed a theme, and that's where things got interesting in all the wrong ways.

### The Great Submodule Adventure

Hugo themes are typically managed as Git submodules, which sounds elegant in theory. In practice? Well, let me tell you about my afternoon of increasingly creative swearing.

I found a theme I liked (hugo-theme-stack) and added it the "normal" way:

```bash
git submodule add https://github.com/CaiJimmy/hugo-theme-stack.git themes/stack
```

Worked perfectly locally. Hugo was happy, the site looked good, everything was great. Then I pushed to GitHub and tried to deploy with Cloudflare Pages.

```
fatal: No url found for submodule path 'themes/stack' in .gitmodules
```

Great. Just great.

### Down the Rabbit Hole

This is where I spent way too much time trying different variations of `git rm --cached` and `git submodule deinit` and generally making things worse. Turns out GitHub was getting confused about the submodule reference, and Cloudflare couldn't clone the theme during builds.

I probably could have saved myself two hours by just reading the error message more carefully, but sometimes I prefer the reckless abandon approach to debugging.

### The Nuclear Option (Which Actually Worked)

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

This time it actually worked. Sometimes the nuclear option genuinely is the right option.

### Getting Cloudflare Pages to Cooperate

With the submodule situation sorted, setting up Cloudflare Pages should have been straightforward. 

*Should have been.*

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

### Custom Domain Setup (Finally, Something Easy)

The last piece was getting my custom domain working properly. This part was actually straightforward for once:

- Added the domain in Cloudflare Pages under Custom Domains
- Set up DNS with a CNAME record pointing to the pages.dev URL
- Enabled proxy mode for better performance
- Set SSL to Full (Strict) because why not

And it worked. First try. I was almost disappointed by how easy it was after everything else.

### What I Actually Learned

The final workflow is genuinely nice:

> I write posts in markdown and commit to my Gitea instance, push to GitHub, and Cloudflare automatically builds and deploys. Everything just works.

The main lessons from this adventure:

- **Git submodules are finicky but they do work** once you get them right
- **Version pinning matters** - don't assume the build environment has what you need
- **Sometimes starting over is faster** than trying to fix a broken git state
- **Read error messages carefully** (I'm still working on this one)

### What's Next

I'm genuinely happy with how this turned out. The writing experience is smooth, deployment is automatic, and I don't have to worry about keeping a CMS updated.

I might add webhooks to automatically sync from Gitea to GitHub, just to remove that manual step. But honestly, the current setup works well enough that I'm not in a rush to complicate it further.

Plus, now I actually have a place to write about all the other stuff I've been tinkering with. And more importantly, a place to get these thoughts out of my head and into the world - even if most people don't read them.

Mission accomplished, I guess.
