import os
import time
from typing import Optional

from azure.ai.projects.models import MemorySearchOptions
from dotenv import load_dotenv

from memory_demo.azure.agents.base_agent import BaseAgent


load_dotenv()


class CustomerAgent(BaseAgent):
    """
    Agent specialized for customer interactions with memory support.
    """

    def __init__(self, prompt_file: str = "customer_agent"):
        super().__init__(agent_name="customer", prompt_file=prompt_file)
        self.memory_store_name = os.getenv("MEMORY_STORE_NAME")
        self.memory_scope = "customer001"

    def chat(self, user_message: str, customer_id: Optional[str] = None) -> str:
        """
        Process a user message and return agent response.
        
        Args:
            user_message: The user's input message
            customer_id: Optional customer scope for memory
            
        Returns:
            Agent response text
        """
        if customer_id:
            self.memory_scope = customer_id

        # Get or create agent
        agent = self.create_or_get_agent()

        # Create thread (conversation)
        thread = self.client.agents.create_thread()
        print(f"✓ Thread created: {thread.id}")

        # Create message
        self.client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=user_message,
        )
        print(f"✓ Message sent: {user_message[:50]}...")

        # Execute agent
        run = self.client.agents.create_run(
            thread_id=thread.id,
            agent_id=agent.id,
        )
        print(f"✓ Run started: {run.id}")

        # Wait for completion
        while run.status in ["queued", "in_progress"]:
            time.sleep(0.5)
            run = self.client.agents.get_run(thread_id=thread.id, run_id=run.id)

        if run.status != "completed":
            raise RuntimeError(f"Run failed with status: {run.status}")

        # Extract response
        messages = self.client.agents.list_messages(thread_id=thread.id)
        response_text = messages.data[0].content[0].text
        print(f"✓ Response received")

        return response_text

    def add_memory(self, content: str, customer_id: Optional[str] = None) -> None:
        """
        Add a memory entry for the customer.
        
        Args:
            content: Memory content to store
            customer_id: Optional customer scope
        """
        if not self.memory_store_name:
            print("⚠ MEMORY_STORE_NAME not configured, skipping memory storage")
            return

        if customer_id:
            self.memory_scope = customer_id

        try:
            poller = self.client.beta.memory_stores.begin_update_memories(
                name=self.memory_store_name,
                scope=self.memory_scope,
                items=[{"type": "message", "content": content}],
            )
            result = poller.result()
            print(f"✓ Memory added for {self.memory_scope}")
        except Exception as e:
            print(f"⚠ Error adding memory: {e}")

    def search_memories(self, query: Optional[str] = None, customer_id: Optional[str] = None) -> list:
        """
        Search memories for the customer.
        
        Args:
            query: Optional search query
            customer_id: Optional customer scope
            
        Returns:
            List of matching memories
        """
        if not self.memory_store_name:
            print("⚠ MEMORY_STORE_NAME not configured, skipping memory search")
            return []

        if customer_id:
            self.memory_scope = customer_id

        try:
            if query:
                response = self.client.beta.memory_stores.search_memories(
                    name=self.memory_store_name,
                    scope=self.memory_scope,
                    query=query,
                    options=MemorySearchOptions(max_memories=100),
                )
            else:
                response = self.client.beta.memory_stores.search_memories(
                    name=self.memory_store_name,
                    scope=self.memory_scope,
                    options=MemorySearchOptions(max_memories=100),
                )

            memories = [str(item) for item in response.results] if response.results else []
            print(f"✓ Found {len(memories)} memories")
            return memories
        except Exception as e:
            print(f"⚠ Error searching memories: {e}")
            return []
