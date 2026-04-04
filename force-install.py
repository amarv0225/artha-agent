import os
from arcadepy import Arcade

# Your project key
client = Arcade(api_key="arc_proj1U1kJ82xD8e4owaJQgvEZZf21xxH5BpTpzsMgbKTvzadj0arjwb")

def install_toolkit(name):
    try:
        print(f"Attempting to install '{name}' toolkit...")
        # Programmatic installation for 2026 SDK
        client.tools.install(name) 
        print(f"✅ Successfully installed {name}!")
    except Exception as e:
        print(f"⚠️ Installation note for {name}: {e}")

# Install the two engines Artha needs
install_toolkit("google")
install_toolkit("google_finance")

# Immediate verification
print("\n--- NEW ACTIVE TOOL LIST ---")
active_tools = [t.fully_qualified_name for t in client.tools.list(limit=2000).items 
                if any(x in t.fully_qualified_name.lower() for x in ['google', 'gmail'])]
print(active_tools if active_tools else "Still empty. Checking for manual publish...")