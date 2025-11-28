from typing import Any, Dict, Optional
from src.core.base_agent import BaseAgent, BaseAgentConfig
from src.core.llm import get_llm
from src.core.memory_manager import MemoryManager


class EmailPrioritizerAgent(BaseAgent):
    def __init__(self, user_id: str = "default_user"):
        system_prompt = """
You are InboxCommander, elite email triage specialist in AgentForge.

User will paste one or multiple emails (separated by --- or numbered).

For each email you analyze:
- Sender importance
- Urgency (deadline, action required, opportunity cost)
- Topic category
- Required response time

Output strict JSON array of objects:

[
  {
    "email_id": 1,
    "sender": "...",
    "subject": "...",
    "urgency_score": 1-10,
    "category": "Sales/HR/Finance/Spam/Newsletter/etc",
    "recommended_action": "Reply within 1h / Delegate / Archive / Reply EOD",
    "one_line_summary": "...",
    "suggested_reply_draft": "Optional short draft if urgency >= 8"
  }
]

Then at the end, give a prioritized action list: "Do these first: #3, #1, #5"

Be cold-blooded. Most emails are trash.
"""
        
        config = BaseAgentConfig(
            system_prompt=system_prompt,
            llm=get_llm(),
            memory=MemoryManager(user_id=user_id),
            tools={},
            metadata={"user_id": user_id}
        )
        
        super().__init__(
            agent_id=f"email_prioritizer_{user_id}",
            name="InboxCommander",
            description="Elite email triage and prioritization specialist",
            capabilities=["email_prioritization", "urgency_analysis", "inbox_management"],
            config=config
        )

    def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute the email prioritization task."""
        response = self.run(task, extra_context=context)
        
        return {
            "output": response,
            "metadata": {
                "agent": self.name,
                "task_type": "email_prioritization"
            }
        }