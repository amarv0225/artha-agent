import asyncio
import os
from tools import get_market_data, get_personal_strategy

async def verify_system():
    ticker = "SULA.NS"
    print(f"--- Verifying Artha-Agent Tools for {ticker} ---")
    
    # Test 1: Supabase
    try:
        context = get_personal_strategy(ticker)
        if context:
            print(f"STATUS: Supabase - Found {context.get('company_name')}")
            print(f"DATA: Target Buy Price is {context.get('target_buy_price')}")
        else:
            print("STATUS: Supabase - Ticker not found in watchlist.")
    except Exception as e:
        print(f"ERROR: Supabase connection failed - {e}")
    
    # Test 2: Arcade MCP
    print("STATUS: Connecting to Arcade Finance MCP...")
    try:
        market = await get_market_data(ticker)
        # Arcade response structure: market.output.value
        price_data = market.output.value
        if price_data:
            print(f"STATUS: Arcade - Successfully retrieved data.")
            print(f"DATA: Current Price is {price_data.get('current_price')}")
        else:
            print("STATUS: Arcade - No data returned for this ticker.")
    except Exception as e:
        print(f"ERROR: Arcade tool execution failed - {e}")

if __name__ == "__main__":
    asyncio.run(verify_system())