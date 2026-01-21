# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Astro website deployed on Vercel. Auto-deploys on every push.

**Live URL:** https://context-challenge-hjy7enx1w-pers-projects-6456b747.vercel.app

## Commands

```bash
npm run dev      # Start dev server (localhost:4321)
npm run build    # Build for production
npm run preview  # Preview production build
```

## Architecture

- `src/pages/` - Astro pages (file-based routing)
- `astro.config.mjs` - Astro configuration with Vercel adapter
- `vercel.json` - Vercel deployment settings

## Deployment

Push to main triggers automatic Vercel deployment.
