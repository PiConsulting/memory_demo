import os
from typing import Optional

from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential, ClientSecretCredential, DefaultAzureCredential
from dotenv import load_dotenv

from memory_demo.azure.agents.prompt_loader import load_prompt


load_dotenv()


class BaseAgent:
    def __init__(
        self,
        agent_name: str,
        instructions: Optional[str] = None,
        prompt_file: Optional[str] = None,
    ) -> None:
        self.agent_name = agent_name
        self.instructions = instructions or load_prompt(prompt_file or agent_name)
        self.client = self._build_client()
        self.agent_id = os.getenv(self._agent_id_env_var())
        self._assert_agents_v1_sdk()

    def _agent_id_env_var(self) -> str:
        return f"FOUNDRY_{self.agent_name.upper()}_AGENT_ID"

    def _build_client(self) -> AIProjectClient:
        endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT", "").strip()
        if not endpoint:
            raise ValueError("FOUNDRY_PROJECT_ENDPOINT is required")
        return AIProjectClient(
            credential=self._build_credential(),
            endpoint=endpoint,
        )

    def _build_credential(self):
        client_id = os.getenv("AZURE_CLIENT_ID", "").strip()
        client_secret = os.getenv("AZURE_CLIENT_SECRET", "").strip()
        tenant_id = os.getenv("AZURE_TENANT_ID", "").strip()
        if client_id and client_secret and tenant_id:
            return ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )
        try:
            return AzureCliCredential()
        except Exception:
            return DefaultAzureCredential(exclude_interactive_browser_credential=False)

    def _assert_agents_v1_sdk(self) -> None:
        if not hasattr(self.client, "agents"):
            raise RuntimeError(
                "The configured azure-ai-projects SDK does not expose client.agents. "
                "Use azure-ai-projects==1.0.0."
            )

    def create_or_get_agent(self):
        """Create a new agent or retrieve existing one by ID"""
        if self.agent_id:
            try:
                agent = self.client.agents.get_agent(self.agent_id)
                print(f"✓ Using existing agent: {self.agent_id}")
                return agent
            except Exception as e:
                print(f"⚠ Could not retrieve agent {self.agent_id}: {e}")
                print("  Creating new agent...")

        agent = self.client.agents.create_agent(
            model="gpt-4o",
            name=self.agent_name,
            instructions=self.instructions,
            temperature=0.1,
        )
        print(f"✓ Agent created with ID: {agent.id}")
        return agent
