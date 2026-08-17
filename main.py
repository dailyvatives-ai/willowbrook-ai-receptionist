"""
Willowbrook Dental Care -- AI Receptionist demo
------------------------------------------------
A single FastAPI service that:
  1. Serves the static front-end (landing page + WhatsApp-style chat widget + admin dashboard)
  2. Exposes /api/chat which talks to Groq's LLM API (OpenAI-compatible) and uses
     "tool calling" so the model can log a qualified lead once it has gathered
     enough information -- name, reason for visit, urgency, and a preferred time.
  3. Exposes /api/admin/leads (protected by a simple admin key) so staff can see
     every lead the AI receptionist has captured.

This is a portfolio/demo project -- storage is in-memory (a Python list), which is
perfectly fine for showing the concept live. In a real production build this would
be swapped for a real database.
"""

import os
import json
import time
import uuid
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
ADMIN_KEY = os.environ.get("ADMIN_KEY", "changeme")

CLINIC_INFO = """
You are Ivy, the friendly AI receptionist for Willowbrook Dental Care.

Clinic facts you can share with patients:
- Hours: Mon-Fri 8am-6pm, Sat 9am-2pm. Closed Sundays.
- Address: 214 Willowbrook Lane, Maple Grove.
- Services: general checkups & cleanings, fillings, whitening, root canals,
  crowns, pediatric dentistry, emergency care.
- Insurance: we accept most major PPO insurance plans. For anything specific,
  tell the patient the front desk will confirm exact coverage.
- New patients are welcome.

Your job in this chat:
1. Be warm, concise, and human -- this is a chat conversation, not an essay. Keep
   replies short (1-3 sentences) unless listing something.
2. Answer FAQs about the clinic using the facts above.
3. If the patient wants to book or describes a dental issue, gather (one question
   at a time, conversationally -- don't interrogate):
     - their name
     - the reason for the visit / what's going on
     - urgency (routine checkup vs. something painful/urgent vs. true emergency)
     - a preferred day/time to come in
4. Once you have name + reason + urgency + preferred time, call the log_lead tool
   with that information. Do this exactly once per conversation, when you have
   enough detail -- don't ask for information you already have.
5. If the patient describes a true emergency (severe bleeding, facial trauma,
   trouble breathing/swallowing), tell them clearly to call the clinic directly
   at (555) 010-1234 or go to the nearest ER -- do not just log it and move on.
6. Never invent information you don't have (exact pricing, doctor availability
   down to the minute, etc.) -- offer to have the front desk confirm details like
   that instead.
"""

LOG_LEAD_TOOL = {
    "type": "function",
    "function": {
        "name": "log_lead",
        "description": (
            "Log a qualified patient lead once you have their name, reason for "
            "visit, urgency level, and a preferred time. Call this exactly once "
            "when you have that information."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Patient's name"},
                "reason": {
                    "type": "string",
                    "description": "Why they want to come in (e.g. 'toothache', 'routine cleaning')",
                },
                "urgency": {
                    "type": "string",
                    "enum": ["routine", "urgent", "emergency"],
                    "description": "How urgent the visit is",
                },
                "preferred_time": {
                    "type": "string",
                    "description": "Patient's preferred day/time, in their own words",
                },
                "phone": {
                    "type": "string",
                    "description": "Patient's phone number, if they gave one, else empty string",
                },
            },
            "required": ["name", "reason", "urgency", "preferred_time"],
        },
    },
}

# ---------------------------------------------------------------------------
# In-memory storage (fine for a demo -- swap for a real DB in production)
# ---------------------------------------------------------------------------

SESSIONS: dict[str, list[dict]] = {}
LEADS: list[dict] = []

app = FastAPI(title="Willowbrook Dental -- AI Receptionist")


# ---------------------------------------------------------------------------
# Request/response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str


# ---------------------------------------------------------------------------
# Core chat logic
# ---------------------------------------------------------------------------

async def call_groq(messages: list[dict]) -> dict:
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not set on the server. Add it in your Render environment variables.",
        )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "tools": [LOG_LEAD_TOOL],
        "tool_choice": "auto",
        "temperature": 0.4,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(GROQ_URL, headers=headers, json=payload)

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Groq API error: {resp.text}")

    return resp.json()


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    if session_id not in SESSIONS:
        SESSIONS[session_id] = [{"role": "system", "content": CLINIC_INFO}]

    history = SESSIONS[session_id]
    history.append({"role": "user", "content": req.message})

    data = await call_groq(history)
    choice = data["choices"][0]["message"]

    # If the model wants to call the log_lead tool, execute it, then ask the
    # model for a final natural-language reply that confirms the booking.
    tool_calls = choice.get("tool_calls")
    if tool_calls:
        history.append(choice)
        for call in tool_calls:
            if call["function"]["name"] == "log_lead":
                try:
                    args = json.loads(call["function"]["arguments"])
                except json.JSONDecodeError:
                    args = {}
                lead = {
                    "id": str(uuid.uuid4()),
                    "session_id": session_id,
                    "captured_at": time.time(),
                    **args,
                }
                LEADS.append(lead)
                tool_result = "Lead logged successfully. Let the patient know the front desk will confirm shortly."
            else:
                tool_result = "Unknown tool."

            history.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": tool_result,
                }
            )

        # Ask the model to turn the tool result into a friendly reply
        data2 = await call_groq(history)
        final_message = data2["choices"][0]["message"]
        reply_text = final_message.get("content") or "Thanks! I've got your details -- our front desk will confirm shortly."
        history.append({"role": "assistant", "content": reply_text})
    else:
        reply_text = choice.get("content") or "Sorry, could you say that again?"
        history.append({"role": "assistant", "content": reply_text})

    # keep session history from growing unbounded
    SESSIONS[session_id] = history[-40:]

    return ChatResponse(session_id=session_id, reply=reply_text)


# ---------------------------------------------------------------------------
# Admin endpoints
# ---------------------------------------------------------------------------

def check_admin(x_admin_key: Optional[str]):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")


@app.get("/api/admin/leads")
async def get_leads(x_admin_key: Optional[str] = Header(default=None)):
    check_admin(x_admin_key)
    return sorted(LEADS, key=lambda l: l["captured_at"], reverse=True)


@app.get("/api/health")
async def health():
    return {"status": "ok", "groq_configured": bool(GROQ_API_KEY)}


# ---------------------------------------------------------------------------
# Static front-end
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static-assets")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/admin")
async def admin_page():
    return FileResponse("static/admin.html")
