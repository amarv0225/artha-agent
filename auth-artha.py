from arcadepy import Arcade
import os

# Initialize Arcade client
client = Arcade(api_key=os.environ.get("ARCADE_API_KEY"))
user_id = "amarprasad.v@gmail.com"

def authorize_and_wait():
    """Step 1: Get the Full-Access Executive Badge."""
    print(f"🚀 [1/2] Starting authorization for {user_id}...")
    
    # We are requesting 5 specific scopes for full management
    auth_response = client.auth.start(
        user_id=user_id,
        provider="google", 
        scopes=[
            "https://www.googleapis.com/auth/gmail.send", 
            "https://www.googleapis.com/auth/calendar.events",gcloud 
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid"
        ]
    )
    
    if auth_response.status == "completed":
        print("✅ Connection is already active.")
    else:
        print(f"\n🔗 ACTION REQUIRED: Visit this URL:\n{auth_response.url}\n")
        print("⏳ Waiting for you to complete the OAuth flow...")
        
        completed_auth = client.auth.wait_for_completion(auth_response)
        
        if completed_auth.status == "completed":
            print("✅ Authorization confirmed.")
        else:
            print(f"❌ Failed: {completed_auth.status}")
            return

def verify_identity():
    """Step 2: Verification Snippet."""
    print(f"\n🔍 [2/2] Running Identity Health Check...")
    try:
        # Execute the WhoAmI tool you requested
        # Note: If this fails, Brian may need 'google.list_events' instead
        response = client.tools.execute(
            tool_name="GoogleCalendar.WhoAmI", 
            user_id=user_id
        )
        print(f"✅ Brian is verified as: {response.output.value}")
    except Exception as e:
        print(f"⚠️ Identity verification skipped: {e}")
        print("Checking if 'google.list_events' works instead...")
        try:
            # Fallback check to see if the standard Google toolkit is active
            client.tools.execute(tool_name="google.list_events", user_id=user_id)
            print("✅ Standard Google Calendar tools are accessible!")
        except:
            print("❌ All Calendar access denied. Check the OAuth checkboxes.")

if __name__ == "__main__":
    authorize_and_wait()
    verify_identity()