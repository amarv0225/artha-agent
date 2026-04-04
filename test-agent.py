import os
from app.agent import artha_brain

def run_test():
    ticker = "SULA.NS"
    print(f"--- Starting Artha-Agent Test: {ticker} ---")
    
    # Initialize state
    initial_state = {
        "ticker": ticker,
        "market_data": {},
        "personal_context": {},
        "analysis": ""
    }
    
    try:
        # Run the brain
        print("STATUS: Executing LangGraph workflow...")
        final_output = artha_brain.invoke(initial_state)
        
        print("\n" + "="*30)
        print("ARTHA'S FINAL RECOMMENDATION")
        print("="*30)
        print(final_output["analysis"])
        print("="*30)
        
    except Exception as e:
        print(f"ERROR: Agent execution failed: {e}")

if __name__ == "__main__":
    # Ensure environment variables are active
    if not os.environ.get("SUPABASE_URL"):
        print("CRITICAL ERROR: Environment variables (SUPABASE_URL, etc.) not found.")
        print("Please run the 'export' commands in your terminal first.")
    else:
        run_test()