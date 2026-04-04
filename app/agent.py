import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from .tools import (
    get_market_data, 
    get_personal_strategy, 
    send_investor_briefing, 
    schedule_trade_review, 
    archive_research_note
)

# 1. Define the Agent State
class AgentState(TypedDict):
    ticker: str
    market_data: dict
    personal_context: dict
    analysis: str
    action_taken: str

# 2. Initialize Gemini 2.5 Flash
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    project=project_id,
    location="us-central1",
    vertexai=True,
    temperature=0
)

# 3. Define the Nodes
def context_node(state: AgentState):
    context = get_personal_strategy(state["ticker"])
    return {"personal_context": context}

def market_node(state: AgentState):
    """Retrieves live price via Arcade."""
    market_response = get_market_data(state["ticker"])
    data = {}
    if hasattr(market_response, 'output') and hasattr(market_response.output, 'value'):
        data = market_response.output.value
    return {"market_data": data}

def analyst_node(state: AgentState):
    """Gemini compares targets to live data."""
    system_prompt = SystemMessage(content=(
        "You are Artha, a sophisticated Stock Market Assistant. "
        "Compare live market data against the user's personal targets. "
        "Provide a concise, executive-level recommendation (Buy/Hold/Sell)."
        "If market data is 'Market Closed', focus on comparing the target to the last known price."
        "Always start with a clear 'Action: BUY' or 'Action: HOLD' line."
    ))
    
    human_content = (
        f"Ticker: {state['ticker']}\n"
        f"Market Data: {state['market_data']}\n"
        f"Watchlist Context: {state['personal_context']}"
    )
    
    response = llm.invoke([system_prompt, HumanMessage(content=human_content)])
    return {"analysis": response.content}

def action_node(state: AgentState):
    """The 'Chief of Staff' Agent: Manages Tasks, Schedules, and Information."""
    analysis = state["analysis"]
    ticker = state["ticker"]
    
    # Logic: Proactive engagement for Buy alerts or specific target hits
    if "BUY" in analysis.upper() or "ALERT" in analysis.upper():
        print(f"--- CHIEF OF STAFF: Executing Proactive Actions for {ticker} ---")
        
        # 1. Manage Interaction: Email the briefing to your Optum account
        send_investor_briefing(
            recipient="amar.vankayalapati@optum.com",
            ticker=ticker,
            analysis=analysis
        )
        
        # 2. Manage Schedule: Block 15 mins for tomorrow's trade review
        schedule_trade_review(ticker)
        
        # 3. Manage Information: Store the analysis in Supabase for long-term memory
        archive_research_note(f"Research logic for {ticker}: {analysis}")
        
        return {"action_taken": "Briefing Sent, Meeting Scheduled, Note Archived."}
    
    return {"action_taken": "No immediate executive action required."}

# 4. Build the Graph
workflow = StateGraph(AgentState)
workflow.add_node("get_context", context_node)
workflow.add_node("get_market", market_node)
workflow.add_node("analyze", analyst_node)
workflow.add_node("take_action", action_node)

# Define the Edges
workflow.set_entry_point("get_context")
workflow.add_edge("get_context", "get_market")
workflow.add_edge("get_market", "analyze")
workflow.add_edge("analyze", "take_action")
workflow.add_edge("take_action", END)

artha_brain = workflow.compile()