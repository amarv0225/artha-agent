import os
from langchain_google_vertexai import ChatVertexAI

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
regions = ["us-central1", "us-east4", "asia-southeast1"]

print(f"--- Diagnosing Gemini Availability for Project: {project_id} ---")

for region in regions:
    print(f"\nChecking Region: {region}...")
    try:
        # We use a very short timeout to keep the probe fast
        llm = ChatVertexAI(model_name="gemini-1.5-pro", project=project_id, location=region)
        response = llm.invoke("Hello")
        print(f"SUCCESS: Gemini is live in {region}!")
        break # Stop once we find a working region
    except Exception as e:
        if "404" in str(e):
            print(f"NOT FOUND: Gemini 1.5 Pro is not enabled in {region}.")
        else:
            print(f"ERROR in {region}: {e}")