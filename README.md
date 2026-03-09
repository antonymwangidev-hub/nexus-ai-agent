# NEXUS AI Agent

NEXUS AI Agent is a multimodal AI-powered social content generation platform that creates complete social media content packs from **text, voice, and uploaded visual references**.

It combines **Google Gemini**, **Imagen**, **Cloud Storage**, **Firestore**, and **FastAPI** to generate:

- captions
- hashtags
- AI image prompts
- generated images
- saved content history
- downloadable exports in JSON, TXT, and PDF

The platform is designed as a modern web app with a polished landing page, an interactive workspace, multimodal input support, and cloud-based persistence.

---

## Live Concept

NEXUS AI Agent helps users turn a simple idea into a complete social media campaign asset.

### Example workflow
A user can:

1. type a prompt
2. speak a prompt using voice input
3. upload a logo, poster, or brand image
4. click **Generate**
5. receive:
   - a caption
   - hashtags
   - an AI-generated image
   - notes and image prompt
6. save and revisit past generations
7. export results as JSON, TXT, or PDF

---

## Features

### Multimodal input
- Text prompt input
- Voice input using browser speech recognition
- Image, poster, and logo upload

### AI generation
- Caption generation
- Hashtag generation
- Image prompt generation
- AI image generation with Google Imagen

### Cloud-powered storage
- Uploaded assets stored in Google Cloud Storage
- Generated images stored in Google Cloud Storage
- History saved in Firestore

### Export options
- JSON export
- TXT export
- PDF export
- Direct image download

### User experience
- Polished landing page
- Auth-style homepage card
- Interactive workspace
- Result cards
- Clickable history detail modal
- Responsive frontend design

---

## Tech Stack

### Backend
- FastAPI
- Python

### Frontend
- HTML
- CSS
- JavaScript

### Google Cloud / AI
- Google Gemini
- Vertex AI
- Imagen
- Firestore
- Google Cloud Storage
- Cloud Run

### Other tools
- ReportLab for PDF export
- Jinja2 templates
- Uvicorn

---

## Project Structure

```bash
socialfusion-agent/
├── app/
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── agent/
│   │   ├── prompt.py
│   │   ├── runner.py
│   │   ├── schemas.py
│   │   └── social_agent.py
│   ├── services/
│   │   ├── content_pipeline.py
│   │   ├── firestore_service.py
│   │   ├── image_service.py
│   │   ├── storage_service.py
│   │   └── upload_service.py
│   ├── static/
│   │   ├── styles.css
│   │   ├── landing.css
│   │   ├── script.js
│   │   └── nexus-logo.png
│   ├── templates/
│   │   ├── index.html
│   │   └── landing.html
│   └── main.py
├── tests/
├── uploads/
├── outputs/
├── .env
├── .gitignore
├── Procfile
├── requirements.txt
└── README.md


How It Works
1. User input

The user provides:

 - a written prompt

 - or a spoken prompt

 - optionally with an uploaded image or logo

2. AI interpretation

Gemini analyzes the request and generates:

 - platform

 - target audience

 - tone

 - caption

 - hashtags

 - image prompt

 - notes

3. Image generation

Imagen generates a visual based on the generated image prompt.

4. Storage

The generated image and uploaded reference files are stored in Google Cloud Storage.

5. Persistence

Each generated content pack is saved in Firestore for later retrieval.

6. Export

Results can be exported as:

JSON

TXT

PDF

Local Development Setup

1. Clone the repository

git clone https://github.com/YOUR_USERNAME/nexus-ai-agent.git
cd nexus-ai-agent

2. Create and activatea virtual environment

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Create your .env file 
Example:
GOOGLE_CLOUD_PROJECT=socialfusion-agent
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GCS_BUCKET_NAME=socialfusion-agent-images-antony-2026

5. Run the project locally

uvicorn app.main:app --reload --reload-dir app

Then Open: http://127.0.0.1::8000/

For the workspace directly: http://127.0.0.1:8000/ui


Deployment

This app is designed to be deployed as a single full-stack service on Google Cloud Run.

Cloud Run hosts:

 - the FastAPI backend

 - the Jinja-rendered frontend

 - the API routes

 - the export functionality

 Once deployed, the app can be accessed from any phone or laptop using a single public URL, even when the developer machine is turned off.
  

Required Google Cloud Services

To run this project in production, enable and configure:

 - Vertex AI API

 - Cloud Run

 - Firestore

 - Cloud Storage

 - Artifact Registry

 - Cloud Build


Required IAM Roles

A deployment/service account typically needs access to:

 - Vertex AI

 - Firestore

 - Cloud Storage

Depending on deployment flow, additional permissions may be required for:

 - Cloud Build

 - Cloud Run source deployment

API Endpoints
Core routes

 - GET / → Landing page

 - GET /ui → Main workspace

API routes

 - POST /api/generate-content-pack

 - GET /api/history

 - GET /api/history/{document_id}

Export routes

 - GET /api/history/{document_id}/export/json

 - GET /api/history/{document_id}/export/txt

 - GET /api/history/{document_id}/export/pdf


Screens / UI Overview
Landing Page

The landing page introduces the product with:

 - brand identity

 - feature highlights

 - workflow explanation

 - CTA to open the workspace

Workspace

The workspace includes:

 - prompt textarea

 - voice input controls

 - file upload

 - generate button

 - result cards

 - downloadable exports

 - history panel

 - history detail modal

Example Use Cases

NEXUS AI Agent can be used for:

 - university club promotions

 - startup marketing campaigns

 - event promotions

 - product launch content

 - community announcements

 - personal brand content packs

 - student innovation campaigns

 - campus event posters and captions

Current Capabilities

 - Generate social content from text

 - Generate social content from voice input

 - Use uploaded image/logo as context

 - Generate AI images

 - Store generated results

 - Reopen previous generations

 - Export content in multiple formats

 - Serve both frontend and backend as one web app

Future Improvements

Planned or possible enhancements include:

 - Gemini Live API integration

 - real-time multimodal conversation

 - better auth and user accounts

 - team workspaces

 - scheduled content generation

 - platform-specific templates

 - analytics dashboard

 - custom brand profiles

 - multi-language generation

 - downloadable presentation/poster layouts

Security Notes

 - Do not commit .env to GitHub

 - Use .gitignore properly

 - Prefer service accounts for production access

 - Limit IAM permissions where possible

 - Store secrets using secure cloud secret management in production

Troubleshooting
The app loads but generation fails

Check:

internet connection

Vertex AI permissions

Firestore permissions

GCS bucket access

service account roles

Browser page loads but frontend buttons do nothing

Check:

 - browser console errors

 - script.js is loading correctly

 - hard refresh with Ctrl + Shift + R

Voice input does not work

Use:

 - Chrome

 - Edge

 - another Chromium-based browser

Firefox may not support browser speech recognition properly.

Cloud Run deployment fails

Check:

 - Procfile

 - requirements.txt

 - uvicorn is installed

 - service account permissions

 - Cloud Build / Artifact Registry access

Author

Antony Mwangi
Founder / Builder of NEXUS AI Agent

GitHub: https://github.com/antonymwangidev-hub

License

This project is currently provided for personal, academic, and portfolio use unless otherwise specified.

Acknowledgements

Built using:

 - FastAPI

 - Google Cloud

 - Vertex AI

 - Gemini

 - Imagen

 - Firestore

 - Cloud Storage

Summary

NEXUS AI Agent is a full-stack multimodal social content creation system that turns text, voice, and visual references into complete campaign-ready content packs.

It is designed to be:

 - practical

 - cloud-connected

 - exportable

 - scalable

 - demo-ready

 - deployable as a single modern web app
