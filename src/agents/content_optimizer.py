from typing import Any, Dict, Optional
from src.core.base_agent import BaseAgent, BaseAgentConfig
from src.core.llm import get_llm
from src.core.memory_manager import MemoryManager


class ContentRewriterAgent(BaseAgent):
    def __init__(self, user_id: str = "default_user"):
        system_prompt = """
You are CareerArchitect, senior resume writer & personal branding expert at AgentForge.

User will provide:
- Their raw career details/resume text OR current resume
- Optionally: a job description/posting/link

Your job:
1. Extract achievements, skills, experience
2. Rewrite every bullet with: Action Verb + Quantifiable Metric + Impact
3. Tailor perfectly to the job description (match keywords exactly but naturally)
4. Output in clean markdown with sections: Professional Summary, Experience, Skills, Education

Output format (strict JSON):

{
  "professional_summary": "...",
  "experience": [...],
  "skills": [...],
  "education": "...",
  "tailoring_notes": "How you adapted it to the job (2-3 bullets)"
}

Make it impossible for recruiters to ignore. Use power words. Be ruthless with weak language.
"""
        
        config = BaseAgentConfig(
            system_prompt=system_prompt,
            llm=get_llm(),
            memory=MemoryManager(user_id=user_id),
            tools={},
            metadata={"user_id": user_id}
        )
        
        super().__init__(
            agent_id=f"content_rewriter_{user_id}",
            name="CareerArchitect",
            description="Expert resume writer and personal branding specialist",
            capabilities=["resume_writing", "content_optimization", "job_tailoring"],
            config=config
        )

    def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute the content rewriting task."""
        response = self.run(task, extra_context=context)
        
        return {
            "output": response,
            "metadata": {
                "agent": self.name,
                "task_type": "content_optimization"
            }
        }