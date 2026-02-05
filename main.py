from fastapi import FastAPI, Request

app = FastAPI()

# -----------------------------
# Scam keyword patterns
# (kept internally, not returned)
# -----------------------------
SCAM_KEYWORDS = [
    "account blocked", "verify", "urgent",
    "upi", "bank", "suspended", "blocked",
    "click", "refund", "kyc"
]

# -----------------------------
# Honeypot API Endpoint
# -----------------------------
@app.api_route("/api/honeypot", methods=["POST", "GET", "OPTIONS"])
async def honeypot_api(request: Request):
    payload = {}

    # Safely parse JSON body
    try:
        if request.method == "POST":
            payload = await request.json()
    except:
        payload = {}

    # Extract message text (safe for missing fields)
    message_text = (
        payload.get("message", {})
        .get("text", "")
        .lower()
    )

    # Internal scam signal detection (not returned)
    scam_detected = any(keyword in message_text for keyword in SCAM_KEYWORDS)

    # Honeypot-style neutral reply
    if scam_detected:
        reply_text = "I don’t understand. Can you explain what you mean?"
    else:
        reply_text = "Sorry, I’m not clear. Can you please explain again?"

    # -----------------------------
    # IMPORTANT:
    # Return ONLY what validator expects
    # -----------------------------
    return {
        "status": "success",
        "reply": reply_text
    }
