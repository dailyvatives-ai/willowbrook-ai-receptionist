# Willowbrook Dental — AI Receptionist

**A live AI receptionist that answers patient questions, triages urgency, and hands the front desk a ready-to-call lead — 24 hours a day, on the channel patients already use.**

🔗 **Live demo:** _add your Render URL here once deployed_
🔗 **Staff dashboard:** `/admin` on the same URL

---

## The problem this solves

Small healthcare and service practices lose patients every day to voicemail, after-hours silence, and front-desk staff who can't be on the phone and at the counter at the same time. A missed message often just means a lost patient — they message the next clinic instead.

## What this AI receptionist does

- **Answers FAQs instantly** — hours, insurance, services — without a human touching it
- **Holds a natural conversation**, not a rigid form, to find out why the patient is reaching out
- **Triages urgency** — routine checkup vs. urgent vs. true emergency — and tells emergencies to call or go to the ER immediately, rather than just logging them
- **Captures a qualified lead automatically** — name, reason for visit, urgency, preferred time — the moment it has enough information, using structured "tool calling" rather than fragile text parsing
- **Surfaces every lead in a staff dashboard**, sorted by recency, so the front desk picks up exactly where the AI left off

## Why it's built this way

This runs as a WhatsApp-styled web chat widget rather than a live WhatsApp number — intentionally. The conversational logic, lead-qualification flow, and tool-calling architecture underneath are **exactly what would sit behind a real WhatsApp Business API integration** in a production build. That's the harder, more valuable part to get right; wiring it to a phone number is comparatively simple once the underlying agent works.

## Tech stack

| Layer | Choice |
|---|---|
| Backend | FastAPI (Python) |
| AI model | Llama 3.3 70B via Groq |
| Structured data extraction | Native LLM tool/function calling |
| Frontend | HTML, CSS, vanilla JS — no framework overhead |
| Hosting | Render |

## Adapting this for your business

This demo is built around a dental clinic, but the underlying pattern — *conversational intake → structured qualification → staff-ready lead* — applies directly to:

- Med spas, salons, and wellness clinics
- Home service businesses (plumbing, HVAC, electricians)
- Real estate inquiries
- Any business currently losing leads to unanswered messages outside business hours

Want this built for your business, on your actual WhatsApp number or website chat? [Get in touch](#) — happy to walk through what a real integration would look like for your specific workflow.

---

*This is a portfolio demo built with a fictional clinic. No real patient data is used or stored.*
