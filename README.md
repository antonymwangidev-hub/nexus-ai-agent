# NEXUS AI Agent

**A live multimodal social content assistant built with Gemini and Google Cloud.**

NEXUS AI Agent helps users move from rough ideas to ready-to-post campaign assets through a single live workflow. Instead of switching between brainstorming tools, prompt editors, image tools, and export utilities, users can **speak, type, upload images, capture camera references, refine ideas in real time, and generate a complete content pack** inside one application.

**Live App:** https://nexus-ai-agent-700973101241.us-central1.run.app  
**Repository:** https://github.com/antonymwangidev-hub/nexus-ai-agent

---

## Overview

Social content creation is often fragmented.

A typical workflow looks like this:
- brainstorm ideas in one place
- manually rewrite them into prompts
- create visuals elsewhere
- organize outputs by hand
- export everything manually

NEXUS AI Agent solves that by acting like a **live creative assistant**. Users collaborate with the agent conversationally, add visual context when needed, and turn that refined discussion directly into production-ready content.

This makes the process:
- faster
- more natural
- more multimodal
- more agentic
- more useful for creators, student leaders, clubs, startups, and small teams

---

## What It Does

NEXUS AI Agent transforms rough creative ideas into polished social media assets.

The application supports:

- **Live AI conversation** for brainstorming and refinement
- **Speech-to-text input** in both the main prompt area and live chat
- **Spoken AI replies** for a more natural interaction experience
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

Instead of forcing users to manually move ideas between chat, prompt writing, image tools, and export tools, the application behaves like a **live multimodal assistant** that can:

- listen
- speak back
- understand image context
- refine creative direction
- move conversation into action
- generate final assets

This creates a smoother workflow and a stronger sense of working with a real AI agent rather than a static form or one-shot prompt box.

---

## Core Features

### 1. Live Agent Workflow
Users can start a live session and collaborate with the AI in real time to brainstorm, refine, and structure content ideas.

### 2. Speak or Type
The app supports continuous speech-to-text and typed input in both:
- the main content generation section
- the live chat section

### 3. Spoken Agent Replies
The live agent can respond in text and also speak replies aloud using browser speech synthesis.

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
- notes / supporting output

### 8. Persistent History
Generated content is saved and can be reopened later for review.

### 9. Export Options
Users can export saved results as:
- JSON
- TXT
- PDF

### 10. Google Cloud Deployment
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

The application uses a cloud-based multimodal architecture:

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


LOCAL SETUP

1. Clone the repository
git clone https://github.com/antonymwangidev-hub/nexus-ai-agent.git
cd nexus-ai-agent

2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Create a .env file
GOOGLE_CLOUD_PROJECT=socialfusion-agent
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GCS_BUCKET_NAME=socialfusion-agent-images-antony-2026

5. Run locally
uvicorn app.main:app --reload --reload-dir app

Open:

http://127.0.0.1:8000

Deployment
The application is deployed on Google Cloud Run.

Example deployment command:

gcloud run deploy nexus-ai-agent \
  --source . \
  --region us-central1 \
  --service-account nexus-ai-agent-sa@socialfusion-agent.iam.gserviceaccount.com \
  --set-env-vars GOOGLE_CLOUD_PROJECT=socialfusion-agent,GOOGLE_CLOUD_LOCATION=global,GOOGLE_GENAI_USE_VERTEXAI=TRUE,GCS_BUCKET_NAME=socialfusion-agent-images-antony-2026 \
  --no-invoker-iam-check \
  --quiet
  
How to Use
Content Generation Flow

1. Enter a prompt or speak into the prompt input
2. Optionally upload or capture a reference image
3. Click Generate
4. Review the generated content pack
5. Export or reopen later from history

Live Mode Flow

1. Start a live session
2. Brainstorm ideas with the live agent
3. Speak or type naturally
4. Optonally upload or capture a live reference image
5. Refine the brief in conversation
6. Ask the agent to write the final prompt into the generator
7. Ask the agent to generate the content
8. Review the generated result and downloads

Example Live Agent Commands
Inside Live Mode, users can say things like:

 - “Give me three content ideas for an Instagram event promo.”
 - “Refine the first idea and make it more modern.”
 - “Write a final prompt in the Generate Content Pack section using everything we discussed.”
 - “Clear the current prompt and write a stronger one.”
 - “Now generate the content.”

Best Experience
For the best experience, use:

1. Google Chrome on desktop
2. Google Chrome on Android

 - Some browser speech-related features may vary across browsers.

Reproducibility

This repository includes the source code, setup instructions, and deployment flow needed to run the project locally or deploy it to Google Cloud Run.

To reproduce the project:

1. clone the repository
2. install dependencies
3. configure environment variables
4. run locally with FastAPI
5. or deploy directly to Cloud Run

Future Improvements
Planned enhancements include:

 - stronger voice-native orchestration
 - improved collaboration workflows
 - more advanced grounding and retrieval
 - broader browser compatibility
 - richer multimodal campaign generation

Author

Antony Mwangi
GitHub: https://github.com/antonymwangidev-hub

Project Repo: https://github.com/antonymwangidev-hub/nexus-ai-agent

License

This project is shared for portfolio, demonstration, and hackathon submission purposes




