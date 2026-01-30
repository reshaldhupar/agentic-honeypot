from fastapi import FastAPI
from typing import Dict
import re
import time
import requests

app = FastAPI()

# -----------------------------
# GUVI CALLBACK ENDPOINT
# -----------------------------
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# -----------------------------
# Scam keyword patterns
# -----------------------------
SCAM_KEYWORDS = [
    "account blocked", "verify now", "urgent",
    "upi", "bank", "suspended", "blocked",
    "click link", "refund", "kyc"
]

UPI_PATTERN = r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}"
PHONE_PATTERN = r"\+91\d{10}"
LINK_PATTERN = r"https?://[^\s]+"


# -----------------------------
# Helper functions
# -----------------------------
def detect_scam(text: str) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in SCAM_KEYWORDS)


def extract_intelligence(text: str, intelligence: Dict):
    intelligence["upiIds"].extend(re.findall(UPI_PATTERN, text))
    intelligence["phoneNumbers"].extend(re.findall(PHONE_PATTERN, text))
    intelligence["phishingLinks"].extend(re.findall(LINK_PATTERN, text))

    for kw in SCAM_KEYWORDS:
        if kw in text.lower():
            intelligence["suspiciousKeywords"].append(kw)


def agent_reply() -> str:
    return "I am not sure, can you explain this again?"


def send_to_guvi(session_id, total_messages, intelligence):
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": intelligence,
        "agentNotes": "Urgency-based scam with payment redirection"
    }

    try:
        requests.post(GUVI_CALLBACK_URL, json=payload, timeout=5)
    except Exception as e:
        print("GUVI callback failed:", e)


# -----------------------------
# API Endpoint
# -----------------------------
@app.post("/api/honeypot")
def honeypot_api(payload: Dict):
    message = payload.get("message", {})
    session_id = payload.get("sessionId", "unknown-session")
    history = payload.get("conversationHistory", [])

    text = message.get("text", "")
    scam_detected = detect_scam(text)

    intelligence = {
        "bankAccounts": [],
        "upiIds": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": []
    }

    extract_intelligence(text, intelligence)

    total_messages = len(history) + 1

    response = {
        "status": "success",
        "scamDetected": scam_detected,
        "engagementMetrics": {
            "engagementDurationSeconds": total_messages * 30,
            "totalMessagesExchanged": total_messages
        },
        "extractedIntelligence": intelligence,
        "agentNotes": "Monitoring conversation"
    }

    if scam_detected:
        response["agentReply"] = agent_reply()

        # 🚨 GUVI CALLBACK (MANDATORY)
        if total_messages >= 2:
            send_to_guvi(session_id, total_messages, intelligence)

    return response
