*This is a submission for the [DEV Weekend Challenge: Community](https://dev.to/challenges/weekend-2026-02-28)*

## The Community
I built this for the Brazilian public-exam student community ("concurseiros") and for anyone studying dense content for months at a time.

I care about this community because I have seen the same pattern over and over: people are motivated in week 1, exhausted by week 6, and lost by week 12. Not because they are lazy, but because the study workflow is chaotic.

The real problems I wanted to help with were simple and very human:
- "I don't know what to review first."
- "I studied a lot, but I can't see progress."
- "Most tools feel generic and disconnected from my exam reality."
- "If I leave my desktop, my routine breaks."

## What I Built
I built **OmniFlash**, a FastAPI + React study companion that combines:
- Domain-based study organization (subjects/topics).
- AI-assisted flashcard generation.
- Swipe-based card flow for quick decisions.
- SRS (Spaced Repetition) training for retention.
- Oracle-style analytics dashboard for progress and planning.
- Mobile-first access with installable PWA and Android build via Capacitor.

What this changes for learners:
- They can split a huge exam syllabus into clear, manageable domains.
- They can generate cards, review with intention, and avoid random revision.
- They can see real progress (hours, consistency, performance), which reduces anxiety and improves discipline.

### How To Access and Use OmniFlash
1. Open the live app: `https://fotodenatal.me/`.
2. Create an account with email/password.
3. Create your first domain (for example: Constitutional Law, Math, Biology).
4. Open the domain and generate cards (or create them manually).
5. Reveal the answer and swipe to save/discard.
6. Go to Training and review due cards with SRS ratings (0-5).
7. Check Oracle/Dashboard to plan your next sessions with data, not guesswork.

Live access:
- Web: `https://fotodenatal.me/`
- Mobile browser: `https://fotodenatal.me/`

### Running Locally (Web)
```bash
git clone https://github.com/joaosnet/klique-api.git
cd klique-api
uv sync
uv run task run

# in another terminal
cd frontend
npm install
npm run dev
```

Then access:
- Backend API: `http://localhost:8000`
- Frontend app: `http://localhost:5173`

## Demo
- Live demo: `https://fotodenatal.me/`
- Suggested video flow for the submission:
  1. Register/Login
  2. Create a domain
  3. Generate and swipe cards
  4. Run an SRS training session
  5. Show dashboard metrics
  6. Open the same app on Android

## Code
Repository:
- https://github.com/joaosnet/klique-api

Tech highlights from this repo:
- Backend: FastAPI, APScheduler, MongoDB
- Frontend: React 19, Vite, i18n
- Mobile: Capacitor Android
- AI integrations and async flows for card generation and assistant features

## How I Built It
### Architecture
I wanted this to be useful in real life, not just in a demo. So I focused on a practical architecture:
- **FastAPI backend** for auth, domains, cards, SRS, analytics, payments, and integrations.
- **React frontend** with mobile-first UX and study-focused routes.
- **Shared API layer** in `frontend/src/services/api.js` to keep frontend/backend communication clean.
- **Capacitor Android** via `frontend/capacitor.config.ts` so the same product can run as a web app and Android app.

### Android: How To Download and Use
Android can be used in two ways:

1. Direct access (no APK build required):
- Open `https://fotodenatal.me/` on your Android device.
- Sign in and use the same study flow in a mobile-friendly layout.

2. Install as app (PWA):
- Open `https://fotodenatal.me/` in Chrome on Android.
- Tap the browser menu and choose `Add to Home screen` / `Install app`.
- Launch OmniFlash from your home screen like a native app.

For contributors/developers, I also provide Android through source build (debug APK) from this repository:

1. Connect an Android device with USB debugging enabled (optional, but recommended).
2. From project root, run:
```bash
uv run task android
```
3. The build script:
- Builds frontend assets
- Syncs Capacitor Android project
- Runs Gradle `assembleDebug`
- Generates APK in:
  `frontend/android/app/build/outputs/apk/debug/`
- If `adb` detects your device, it installs automatically.

4. If not auto-installed, manually install the APK from the generated path.
5. Open **OmniFlash** on your Android device and use the same study flow as web.

### Optional Android Hot Reload During Development
```bash
uv run task android-hot
```
This launches Vite + Capacitor live reload for faster testing on device/emulator.

### Why this execution is practical for the weekend challenge
- One codebase serves web + Android.
- Fast iteration for UI and feature experiments.
- A real user flow focused on learning outcomes, not just interface polish.

Most importantly: this project was built to support people who are trying to stay consistent during long study cycles. If it helps someone review one more day instead of giving up, it already did its job.

