import os
from datetime import datetime
from typing import Optional
import traceback
from fastapi import FastAPI, Body, HTTPException  # Added HTTPException
import httpx
from pydantic import BaseModel
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from utils import safe_json_response

from models import init_db, save_failure, get_all_failures

# ─── Set up ─────────────────────────────────────────────────────────
load_dotenv()
init_db()

app = FastAPI(title="Monorail MCP Server")

BASE_URL      = os.getenv("BASE_URL")
SLACK_TOKEN   = os.getenv("SLACK_BOT_TOKEN")

slack = WebClient(token=SLACK_TOKEN)
webhooks: list[str] = []

# ─── Pydantic Payload Model ─────────────────────────────────────────
class TradePayload(BaseModel):
    side: str
    amount: float
    sender: Optional[str] = None
    slippage: Optional[int] = 50
    deadline: Optional[int] = 60
    max_hops: Optional[int] = 3

# ─── Helpers ────────────────────────────────────────────────────────
def is_failure(resp: httpx.Response) -> bool:
    if resp.status_code != 200:
        return True
    try:
        data = resp.json()
        return data.get("success") is False or "error" in data
    except Exception:
        return True

def report_failure(message: str):
    try:
        slack_channel = os.getenv("SLACK_CHANNEL", "C08PL55FATG")
        slack.chat_postMessage(channel=slack_channel, text=message)
    except SlackApiError as e:
        print("Slack error:", e.response["error"])


def call_webhooks(record: dict):
    for url in webhooks:
        try:
            httpx.post(url, json=record)
        except Exception as e:
            print("Webhook failed:", e)

# ─── Endpoints ──────────────────────────────────────────────────────

@app.get("/quote")
async def get_quote(
    amount: float,
    from_token: str,
    to_token: str,
    sender: Optional[str] = None,
    slippage: int = 50,
    deadline: int = 60,
    max_hops: int = 3,
    source: Optional[str] = None,
):
    url = f"{BASE_URL}/v1/quote"
    params = {
        "amount": amount,
        "from": from_token,
        "to": to_token,
        "sender": sender,
        "slippage": slippage,
        "deadline": deadline,
        "max_hops": max_hops,
        "source": source,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params={k:v for k,v in params.items() if v is not None})
    return resp.json()

@app.post("/trade/{token_pair}")
async def create_trade(
    token_pair: str,
    payload: TradePayload = Body(...),
):
    try:
        record = {
            "pair": token_pair,
            "payload": payload.model_dump(),
            "error": None,
            "timestamp": datetime.utcnow(),
        }

        url = f"{BASE_URL}/v1/trade/{token_pair}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload.model_dump())

        # — safe parse once —
        resp_data = safe_json_response(resp)

        # — check failure via status or error field —
        failed = resp.status_code != 200 or resp_data.get("success") is False or "error" in resp_data
        if failed:
            err = resp_data.get("error", resp.text)
            record["error"] = err
            save_failure(record)
            report_failure(f":x: Trade Failed on {token_pair}\nError: {err}")
            call_webhooks(record)
            return {"status": "failed", "error": err}

        # — always return the safe data —
        return resp_data

    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        raise HTTPException(status_code=500, detail=f"{e}\n\n{tb}")
@app.get("/failed-trades")
def failed_trades():
    try:
        trades = get_all_failures()
        return {"failed_trades": [t.model_dump() for t in trades]}  # Changed from .dict()
    except Exception as e:
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch trades")

@app.post("/webhooks/register")
def register_webhook(url: str = Body(..., embed=True)):
    webhooks.append(url)
    return {"registered": url}