# File: deploy.py
# A custom deployment script to upload all your project files to Windmill via its REST API.
# This script bypasses the problematic 'wmill sync' command.

import os
import requests
import json
import yaml
from typing import Dict, Any

# --- CONFIGURATION: EDIT THESE THREE VARIABLES ---
WINDMILL_URL = "http://5.78.138.105:8088"  # <--- IMPORTANT: REPLACE WITH YOUR VPS IP
WINDMILL_TOKEN = "sBICrMZeDv0LtWH2D7xPSskyPNUSUX1y"    # <--- IMPORTANT: REPLACE WITH YOUR TOKEN
# -------------------------------------------------

HEADERS = {"Authorization": f"Bearer {WINDMILL_TOKEN}"}

def deploy_item(filepath: str, item_type: str, workspace: str):
    """Deploys a single script or flow."""
    
    if item_type == "script":
        with open(filepath, "r") as f:
            content = f.read()
        language = "python" if filepath.endswith(".py") else "typescript"
        path_in_windmill = os.path.splitext(os.path.relpath(filepath, workspace))[0].replace(os.path.sep, "/")
        payload = {"path": path_in_windmill, "content": content, "language": language}
        url = f"{WINDMILL_URL}/api/w/{workspace}/scripts/create"
        update_url = f"{WINDMILL_URL}/api/w/{workspace}/scripts/update"
    elif item_type == "flow":
        with open(filepath, "r") as f:
            content_str = f.read()
            content_yaml = yaml.safe_load(content_str)
        path_in_windmill = os.path.splitext(os.path.basename(filepath))[0]
        payload = {"path": path_in_windmill, "value": content_yaml}
        url = f"{WINDMILL_URL}/api/w/{workspace}/flows/create"
        update_url = f"{WINDMILL_URL}/api/w/{workspace}/flows/update"
    else:
        return

    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=20)
        # 409 Conflict means it already exists, so we try to update it
        if response.status_code == 409:
            print(f"INFO: {item_type.capitalize()} '{path_in_windmill}' already exists. Updating...")
            response = requests.post(update_url, headers=HEADERS, json=payload, timeout=20)

        response.raise_for_status()
        print(f"✅ Successfully deployed {item_type.upper()}: {filepath}")
    except requests.exceptions.RequestException as e:
        print(f"❌ FAILED to deploy {item_type.upper()}: {filepath}")
        error_text = e.response.text if hasattr(e, 'response') and e.response is not None else str(e)
        print(f"   Error: {error_text}")

def main():
    """Main function to find and deploy all project files."""
    projects = {
        "cryptex_ai_omega": "cryptex_project",
        "content_factory": "content_project"
    }

    for workspace, project_dir in projects.items():
        if not os.path.isdir(project_dir):
            continue
        print(f"\n--- Deploying {project_dir} to workspace: {workspace} ---")
        for root, _, files in os.walk(project_dir):
            for file in files:
                filepath = os.path.join(root, file)
                if file.endswith((".py", ".ts")):
                    deploy_item(filepath, "script", workspace)
                elif file.endswith(".yml"):
                    deploy_item(filepath, "flow", workspace)

    print("\n🚀 Deployment complete!")

if __name__ == "__main__":
    if "YOUR_VPS_IP_ADDRESS" in WINDMILL_URL or "YOUR_WINDMILL_AUTH_TOKEN" in WINDMILL_TOKEN:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! ERROR: Please edit the deploy.py script and fill in your")
        print("!!!        WINDMILL_URL and WINDMILL_TOKEN variables.")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        main()