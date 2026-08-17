# Willowbrook Dental — AI Receptionist (Demo 1)

A live, working AI receptionist demo: a WhatsApp-style chat widget that answers
patient FAQs, gathers appointment details, flags emergencies, and logs
qualified leads to a staff dashboard.

**Stack:** FastAPI (backend) + Groq (Llama 3.3 70B, free tier) + plain HTML/CSS/JS
(frontend) — one single web service, deployed free on Render. Same free-tier
philosophy as your other two demos.

---

## 1. Get a free Groq API key

1. Go to https://console.groq.com and sign up (free).
2. Go to **API Keys** → **Create API Key**.
3. Copy the key — you'll paste it into Render in step 3 below. You will not be able to see it again after leaving the page, so save it somewhere safe for now.

*(Term explained: an "API key" is like a password that lets your app talk to Groq's servers.
Never put it directly in your code or commit it to GitHub — it goes in an environment
variable instead, which is a setting stored outside your code, so it stays private.)*

## 2. Push this project to GitHub

```bash
cd dental-ai-receptionist
git init
git add .
git commit -m "AI receptionist demo"
```

Then create a new empty repo on GitHub (e.g. `willowbrook-ai-receptionist`) and push:

```bash
git remote add origin https://github.com/<your-username>/willowbrook-ai-receptionist.git
git branch -M main
git push -u origin main
```

## 3. Deploy on Render

1. Go to https://render.com and sign in (free tier is enough).
2. Click **New +** → **Web Service**.
3. Connect your GitHub account and select the repo you just pushed.
4. Render should auto-detect the settings from `render.yaml`. If it asks manually, use:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
5. Under **Environment**, add these two variables:
   - `GROQ_API_KEY` → paste the key from step 1
   - `ADMIN_KEY` → make up any password (e.g. `willowbrook2026`) — this protects your staff dashboard at `/admin` so random visitors can't see captured leads.
6. Click **Create Web Service**. First deploy takes ~2-3 minutes.

Once it's live, Render gives you a URL like:
`https://willowbrook-ai-receptionist.onrender.com`

*(Term explained: "deploy" just means "put your code on a server so it's live on
the internet, not just running on your own laptop." Render is doing that server
part for you, for free.)*

## 4. Try it

- Visit your Render URL → chat with Ivy directly on the landing page.
- Try things like:
  - "What are your hours?"
  - "Do you take PPO insurance?"
  - "I have a bad toothache, can I come in this week? My name is Raj, prefer Thursday afternoon."
- After a conversation where Ivy has your name, reason, urgency, and preferred time, she'll log it as a lead automatically.
- Visit `/admin` on the same URL, enter your `ADMIN_KEY`, and see the captured lead appear.

## Notes for your Upwork portfolio entry

- **Title idea:** "AI Receptionist for Dental Clinics — WhatsApp-Style Lead Capture"
- **Case study angle:** Problem (missed after-hours messages, manual triage) → Solution (AI receptionist that qualifies and logs leads automatically) → Tech (FastAPI, Groq/Llama 3.3, tool-calling for structured data extraction).
- Mention explicitly: built as a web chat widget using the same conversational/tool-calling architecture that would sit behind a real WhatsApp Business API + Twilio integration in production — this shows you understand the real deployment path without pretending you spun up paid WhatsApp infrastructure for a portfolio piece.
- Add both the live link and a couple of screenshots (or a short screen-recording GIF) of the chat + admin dashboard, since a static screenshot alone won't show the "watch it think" quality that makes AI demos land with clients.

## Notes / limitations (fine for a demo, mention if a client asks)

- Leads are stored in memory — they reset if the free Render instance restarts (which free instances do after ~15 min of inactivity, and Render "wakes" them on the next request — a small 10-20 second delay on first message after idle is expected on the free tier).
- No real WhatsApp/Twilio integration — this is intentional for the free/portfolio version; the same backend logic would plug into Twilio's WhatsApp API for a real client with minimal changes.
