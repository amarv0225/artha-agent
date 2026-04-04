import os
from langchain_google_genai import ChatGoogleGenerativeAI

print("--- Artha-Agent: 2026 Connection Test ---")
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        location="us-central1",
        vertexai=True
    )
    response = llm.invoke("Are you there, Artha?")
    print(f"SUCCESS! Artha says: {response.content}")
except Exception as e:
    print(f"FAILED: {e}")