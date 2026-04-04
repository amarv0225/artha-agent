import asyncio
from app.agent import artha_brain

async def test_run():
    print("--- 🚀 STARTING LOCAL VERIFICATION ---")
    inputs = {"ticker": "ARE&M.NS"}
    
    # This runs the LangGraph exactly as it would in Cloud Run
    async for output in artha_brain.astream(inputs):
        for key, value in output.items():
            print(f"\nNode '{key}' finished:")
            print(f"Result: {value}")
    print("\n--- ✅ LOCAL VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_run())