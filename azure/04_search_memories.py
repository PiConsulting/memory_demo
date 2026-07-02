import os
from dotenv import load_dotenv
load_dotenv()

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MemorySearchOptions
from azure.identity import DefaultAzureCredential

# Initialize project client
project_client = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

memory_store_name = os.environ.get("MEMORY_STORE_NAME")
scope = "customer001"

# Retrieve static memories (user profile memories)
print("Searching for static memories...")
try:
    static_search_response = project_client.beta.memory_stores.search_memories(
        name=memory_store_name,
        scope=scope,
        options=MemorySearchOptions(max_memories=100)
    )
    
    print("Static Memories (User Profile):")
    if hasattr(static_search_response, 'results') and static_search_response.results:
        for memory in static_search_response.results:
            print(memory)
    else:
        print("  No memories found")
except Exception as e:
    print(f"  Error: {e}")

# Search memories by a query (contextual search)
print("\nSearching with contextual query...")
query_text = "What are all your memories?"

try:
    contextual_search_response = project_client.beta.memory_stores.search_memories(
        name=memory_store_name,
        scope=scope,
        query=query_text,
        options=MemorySearchOptions(max_memories=100)
    )

    print("Contextual Search Results:")
    if hasattr(contextual_search_response, 'results') and contextual_search_response.results:
        for memory in contextual_search_response.results:
            print(memory)
    else:
        print("  No memories found")
except Exception as e:
    print(f"  Error: {e}")
