#!/usr/bin/env python3
# update_project_map.py - Script to update TrintityAI_Project_Map.json

import json

# Template data (update this with new details)
data = {  # Your full JSON from the map above
    "project_name": "TrinityAI Ecosystem",
    # ... full JSON content from above ...
}

with open("TrintityAI_Project_Map.json", "w") as f:
    json.dump(data, f, indent=4)
print("Project map updated.")