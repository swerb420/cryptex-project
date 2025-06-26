# File: deploy.py
# --- FINAL CORRECTED VERSION v3 ---
# This version fixes two critical bugs:
# 1. Sends 'python3' as the language name instead of 'python'.
# 2. Correctly includes the 'summary' and 'description' when uploading flows.
# It has also been simplified to ONLY deploy the cryptex_project, as requested.

import os
import requests
import json
import yaml
from typing import Dict, Any

# --- CONFIGURATION: Please double-check these are correct ---
WINDMILL_BASE_URL = "http://5.78.138.105:8088"
WINDMILL_TOKEN = "8fzLR4Rkkh2CMpDhOOaJSrmBr62TTToj"
WORKSPACE = "cryptex_project"
PROJECT_DIR = "cryptex_project"
# -------------------------------------------------------------

HEADERS = {"Authorization": f"Bearer {WINDMILL_TOKEN}", "Content-Type": "application/json"}

def deploy_resource(filepath: str):
    """Determines the resource type from its file extension and deploys it."""
    
    # Construct the path as Windmill will see it (e.g., scripts/monitors/s_wallet_tracker)
    path_in_windmill = os.path.splitext(os.path.relpath(filepath, PROJECT_DIR))[0]

    if filepath.endswith((".py", ".ts")):
        item_type, language = "script", "python3" if filepath.endswith(".py") else "typescript"
        with open(filepath, "r", encoding='utf-8') as f:
            content = f.read()
        payload = {"path": path_in_windmill, "content": content, "language": language}
        create_url = f"{WINDMILL_BASE_URL}/api/w/{WORKSPACE}/scripts/create"
        update_url = f"{WINDMILL_BASE_URL}/api/w/{WORKSPACE}/scripts/update"

    elif filepath.endswith((".yml", ".yaml")):
        item_type = "flow"
        with open(filepath, "r", encoding='utf-8') as f:
            content_yaml = yaml.safe_load(f)
        
        # Use the filename as the path, and extract summary/description for the payload
        flow_path = os.path.splitext(os.path.basename(filepath))[0]
        payload = {
            "path": flow_path,
            "summary": content_yaml.get("summary", f"Flow deployed from {flow_path}.yml"),
            "description": content_yaml.get("description", ""),
            "value": content_yaml
        }
        create_url = f"{WINDMILL_BASE_URL}/api/w/{WORKSPACE}/flows/create"
        update_url = f"{WINDMILL_URL}/api/w/{WORKSPACE}/flows/update"
    else:
        return # Skip non-deployable files

    try:
        response = requests.post(create_url, headers=HEADERS, json=payload, timeout=30)
        
        if response.status_code == 409: # 409 Conflict means it already exists
            print(f"INFO: {item_type.capitalize()} '{path_in_windmill}' already exists. Updating...")
            response = requests.post(update_url, headers=HEADERS, json=payload, timeout=30)

        response.raise_for_status()
        print(f"✅ Successfully deployed {item_type.upper()}: {filepath}")

    except requests.exceptions.RequestException as e:
        print(f"❌ FAILED to deploy {item_type.upper()}: {filepath}")
        error_text = e.response.text if hasattr(e, 'response') and e.response is not None else str(e)
        print(f"   Error: {error_text}")

def main():
    """Main function to find and deploy all project files."""
    
    if not os.path.isdir(PROJECT_DIR):
        print(f"ERROR: Project directory '{PROJECT_DIR}' not found. Make sure you are running this script from the correct parent folder.")
        return

    print(f"\n--- Deploying {PROJECT_DIR} to workspace: {WORKSPACE} ---")
    for root, _, files in os.walk(PROJECT_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            deploy_resource(filepath)

    print("\n🚀 Deployment complete!")

if __name__ == "__main__":
    if "YOUR_VPS_IP_ADDRESS" in WINDMILL_BASE_URL or "YOUR_WINDMILL_AUTH_TOKEN" in WINDMILL_TOKEN:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! ERROR: Please edit the deploy.py script and fill in your")
        print("!!!        WINDMILL_BASE_URL and WINDMILL_TOKEN variables.")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        main()