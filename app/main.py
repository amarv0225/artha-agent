import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from supabase import create_client, Client
from .agent import artha_brain

app = FastAPI(title="The Artha-Agent System: Executive Assistant API")

# Initialize Supabase Client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

class AnalysisRequest(BaseModel):
    ticker: Optional[str] = None

@app.get("/")
def health():
    return {"status": "Artha Agent is Online", "mode": "Executive Assistant"}

async def run_brian_engine(ticker: str):
    """Core logic to invoke the LangGraph Brain for a specific ticker."""
    initial_state = {
        "ticker": ticker,
        "market_data": {},
        "personal_context": {},
        "analysis": ""
    }
    # Invoke the LangGraph orchestrator (Brian)
    return artha_brain.invoke(initial_state)

@app.post("/v1/analyze")
async def analyze_adhoc(request: AnalysisRequest):
    """AD-HOC MODE: Triggered by user for a specific ticker."""
    if not request.ticker:
        raise HTTPException(status_code=400, detail="Ticker is required for ad-hoc analysis.")
    
    try:
        result = await run_brian_engine(request.ticker)
        return {
            "mode": "adhoc",
            "ticker": request.ticker,
            "recommendation": result["analysis"],
            "summary": {
                "price": result["market_data"].get("price"),
                "target": result["personal_context"].get("target_price")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/pulse")
async def proactive_pulse(background_tasks: BackgroundTasks):
    """PROACTIVE MODE: Triggered by Cloud Scheduler to scan the watchlist."""
    try:
        # 1. Fetch the active watchlist from Supabase
        # Assumes table 'watchlist' has a column 'ticker'
        response = supabase.table("watchlist").select("ticker").execute()
        watchlist = [item['ticker'] for item in response.data]
        
        if not watchlist:
            return {"status": "Pulse complete", "message": "Watchlist is empty."}

        summary_actions = []

        # 2. Iterate through each ticker
        for ticker in watchlist:
            result = await run_brian_engine(ticker)
            
            # 3. Decision Logic: Only "Action" if it's not a HOLD
            # This prevents Gmail/Calendar from being flooded every hour
            if "Action: HOLD" not in result["analysis"]:
                # The 'take_action' node inside artha_brain handles the Gmail/Calendar
                summary_actions.append(f"Alert triggered for {ticker}")
            else:
                summary_actions.append(f"{ticker}: No action required (HOLD)")

        return {
            "mode": "proactive_pulse",
            "tickers_scanned": len(watchlist),
            "actions_taken": summary_actions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pulse failed: {str(e)}")