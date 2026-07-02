"""
Add Memories Directly to Memory Store via API

Note: Requires the Azure Foundry project to have Memory Stores feature enabled.
If you get "preview_feature_required" error, contact your Azure admin.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Initialize project client  
project_client = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

memory_store_name = os.environ.get("MEMORY_STORE_NAME")
scope = "customer001"

print("Adding memories to Memory Store...\n")

# Add first memory
memory_1 = "Me gusta mucho el ajo y la cebolla en mis comidas"
print(f"1. Adding: {memory_1}")

try:
    poller = project_client.beta.memory_stores.begin_update_memories(
        name=memory_store_name,
        scope=scope,
        items=[{"type": "message", "content": memory_1}],
    )
    result = poller.result()
    print(f"   [SUCCESS] Memory 1 added\n")
except Exception as e:
    print(f"   [ERROR] {str(e)[:100]}\n")

# Add second memory
memory_2 = "Odio profundamente el apio"
print(f"2. Adding: {memory_2}")

try:
    poller = project_client.beta.memory_stores.begin_update_memories(
        name=memory_store_name,
        scope=scope,
        items=[{"type": "message", "content": memory_2}],
    )
    result = poller.result()
    print(f"   [SUCCESS] Memory 2 added\n")
except Exception as e:
    print(f"   [ERROR] {str(e)[:100]}\n")

print("Done!")
