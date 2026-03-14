# NEXUS AI Agent

**A live multimodal social content assistant built with Gemini and Google Cloud.**

NEXUS AI Agent helps users **speak, type, upload, and capture visual references in real time**, refine ideas through a live AI conversation, and generate a complete social content pack from one workflow.

It is designed for creators, student leaders, clubs, marketers, startups, and teams who want faster, smarter content creation without jumping between multiple tools.

---

## Live Demo

**Production URL:** `https://nexus-ai-agent-700973101241.us-central1.run.app`

---

## Overview

Social content creation is often fragmented.

People usually brainstorm in one place, rewrite prompts in another, generate visuals somewhere else, and manually organize everything afterward. That process is slow, repetitive, and difficult for non-experts.

**NEXUS AI Agent** brings that process into one live workspace.

Users can:
- brainstorm with a live AI agent
- speak or type naturally
- upload or capture reference images
- refine ideas in real time
- automatically move the refined brief into the generator
- trigger generation from the live workflow
- receive a complete content pack with exports and saved history

The result is a more natural, guided, and production-ready creative workflow.

---

## What It Does

NEXUS AI Agent transforms rough ideas into polished social media assets.

The app supports:

- **Live AI conversation** for idea refinement
- **Voice input** in both the prompt area and live chat
- **Spoken AI replies** for a more natural live experience
- **Image upload** in both generation and live sections
- **Camera capture** in both generation and live sections
- **Automatic prompt writing** from live discussion into the generator
- **Agent-triggered generation**
- **Content pack generation**
- **Persistent history**
- **Export as JSON, TXT, and PDF**

---

## Why It Stands Out

NEXUS AI Agent is designed to go beyond the traditional text-box-only interaction model.

Instead of forcing users to manually move ideas between chat, prompt writing, image tools, and export tools, the application acts like a **live multimodal assistant** that can:

- listen
- speak back
- understand image context
- refine creative direction
- move conversation into action
- generate final assets

This creates a smoother user experience and a stronger sense of working with a real agent rather than a static form or one-shot prompt box.

---

## Core Features

### 1. Live Agent Workflow
Users can start a live session and collaborate with the AI in real time to brainstorm, refine, and structure content ideas.

### 2. Speak or Type
The app supports continuous speech-to-text and typed input in both:
- the main content generation section
- the live chat section

### 3. Spoken Agent Replies
The live agent can respond in text and also speak replies aloud using browser voice synthesis.

### 4. Image Upload
Users can upload reference images in:
- the Generate Content Pack section
- the Live Mode section

### 5. Camera Capture
Users can open the camera and capture still reference images in:
- the Generate Content Pack section
- the Live Mode section

### 6. Live-to-Generate Automation
After refining ideas in live chat, the agent can:
- write the final prompt directly into the Generate Content Pack section
- clear or update the prompt
- trigger content generation automatically

### 7. Content Pack Generation
The app generates:
- social caption
- hashtags
- image prompt
- AI-generated image
- notes / guidance output

### 8. History
Generated content is saved to persistent history for later review.

### 9. Exports
Users can export saved results as:
- JSON
- TXT
- PDF

### 10. Google Cloud Hosting
The backend is deployed on **Google Cloud Run** and uses Google Cloud services for storage and persistence.

---

## Submission Category Fit

This project is best suited for the **Live Agents** category.

NEXUS AI Agent focuses on:
- real-time interaction
- multimodal input
- live idea refinement
- conversational workflow
- Google Cloud-hosted Gemini-based agent behavior

---

## Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- FastAPI

### AI Layer
- Gemini
- Google GenAI SDK
- Gemini Live API patterns

### Google Cloud
- Cloud Run
- Firestore
- Cloud Storage

---

## Architecture

The application uses a simple cloud-based multimodal architecture:

### Frontend Web App
Responsible for:
- landing page
- workspace UI
- prompt input
- live chat
- speech-to-text
- voice replies
- image upload
- camera capture
- generated result display
- history sidebar
- downloads / exports

### FastAPI Backend
Responsible for:
- serving the frontend
- handling live WebSocket sessions
- orchestrating prompt refinement and generation
- processing content generation requests
- storing and retrieving history
- providing export endpoints

### Gemini / Live Agent Layer
Responsible for:
- live creative brainstorming
- prompt refinement
- multimodal understanding
- agentic UI actions
- final content generation support

### Firestore
Responsible for:
- storing history records
- storing metadata
- storing document references

### Cloud Storage
Responsible for:
- storing uploaded images
- storing captured references
- storing generated images
- serving media assets

### Cloud Run
Responsible for:
- hosting the backend service
- serving the deployed application

---

## Project Structure

```bash
app/
├── api/
│   ├── live_routes.py
│   └── ...
├── live/
│   └── live_session.py
├── static/
│   ├── styles.css
│   ├── landing.css
│   ├── script.js
│   └── nexus-logo.png
├── templates/
│   ├── landing.html
│   └── index.html
├── main.py
└── ...
