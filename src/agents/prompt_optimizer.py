from typing import Any, Dict, Optional
from src.core.base_agent import BaseAgent, BaseAgentConfig
from src.core.llm import get_llm
from src.core.memory_manager import MemoryManager


class PromptOptimizerAgent(BaseAgent):
    def __init__(self, user_id: str = "default_user"):
        system_prompt = """
You are PromptSmith, the world's greatest Prompt Engineer working in AgentForge Productivity Suite.

Your expertise is the CO-STAR framework (Context, Objective, Style, Tone, Audience, Response format).
When the user gives you a prompt (text, code, image description, anything), you rewrite it using CO-STAR to make it 10x better.

Output format (strict JSON so we can parse it later if needed):

{
  "original_prompt": "...",
  "optimized_prompt": "...",
  "explanation": "Brief explanation why this is better (max 2 sentences)"
}

Never refuse, never say you can't optimize image prompts — you can (describe the image generation task perfectly).
Always be elite-tier. This is your craft.
"""
        
        config = BaseAgentConfig(
            system_prompt=system_prompt,
            llm=get_llm(),
            memory=MemoryManager(user_id=user_id),
            tools={},
            metadata={"user_id": user_id}
        )
        
        super().__init__(
            agent_id=f"prompt_optimizer_{user_id}",
            name="PromptSmith",
            description="Expert prompt optimizer using CO-STAR framework",
            capabilities=["prompt_optimization", "co_star_framework"],
            config=config
        )

    def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute the prompt optimization task."""
        response = self.run(task, extra_context=context)
        
        return {
            "output": response,
            "metadata": {
                "agent": self.name,
                "task_type": "prompt_optimization"
            }
        }