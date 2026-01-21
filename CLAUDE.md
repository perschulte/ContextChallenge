# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static website deployed on Vercel. Auto-deploys on every push to main.

**Live URL:** https://context-challenge-hjy7enx1w-pers-projects-6456b747.vercel.app

## Architecture

- `index.html` - Main landing page (standalone HTML with embedded CSS)
- `vercel.json` - Vercel deployment configuration (static site, no build step)

## Deployment

Push to main branch triggers automatic Vercel deployment. No build command required - files are served directly.
