from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

__all__ = ["BaseAgent", "BaseAgentConfig"]

try:
    import structlog
    logger = structlog.get_logger(__name__)
except Exception:  # fallback if structlog not available
    logger = None

# Try to import centralized tracing; fall back to no-op
try:
    from src.observability.tracing import trace_agent_call  # type: ignore
except Exception:
    def trace_agent_call(**kwargs: Any) -> None:  # type: ignore
        return


@dataclass
class BaseAgentConfig:
    system_prompt: str
    llm: Any
    memory: Any
    tools: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        capabilities: Optional[List[str]],
        config: BaseAgentConfig,
    ) -> None:
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities or []
        self.config = config

        self.llm = config.llm
        self.memory = config.memory
        self.tools = config.tools
        self.metadata = config.metadata
        self.system_prompt: str = config.system_prompt

        if logger:
            logger.info(
                "agent_initialized",
                agent_id=self.agent_id,
                name=self.name,
                capabilities=self.capabilities,
            )

    @abstractmethod
    def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Implement the core logic of the agent."""
        raise NotImplementedError

    def _build_messages(
        self,
        user_input: str,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> List[BaseMessage]:
        # Retrieve semantic context
        retrieved_docs = self.memory.semantic_search(user_input, n_results=3)
        recent_context = self.memory.get_recent_context()

        messages: List[BaseMessage] = [SystemMessage(content=self.system_prompt)]

        if recent_context:
            messages.append(SystemMessage(content="Previous conversation:\n" + str(recent_context)))

        if extra_context:
            messages.append(SystemMessage(content="Extra context:\n" + str(extra_context)))

        if retrieved_docs:
            formatted = "\n".join(f"- {doc}" for doc in retrieved_docs)
            messages.append(SystemMessage(content="Retrieved context:\n" + formatted))

        # Finally, the user query itself
        messages.append(HumanMessage(content=user_input))
        return messages

    def run(
        self,
        user_input: str,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """High-level entrypoint with RAG augmentation and provenance."""
        messages = self._build_messages(user_input=user_input, extra_context=extra_context)

        try:
            response_obj = self.llm.invoke(messages)
            response = response_obj.content if hasattr(response_obj, "content") else str(response_obj)
        except Exception as e:
            response = f"(Error invoking LLM: {e})"
            if logger:
                logger.error("agent_llm_error", agent_id=self.agent_id, name=self.name, error=str(e))

        # Provenance
        retrieved = self.memory.semantic_search(user_input, n_results=3)
        recent_context = self.memory.get_recent_context()

        trace_agent_call(
            agent_name=self.name,
            agent_id=self.agent_id,
            user_input=user_input,
            response=response,
            context=recent_context,
            retrieved_docs=retrieved,
            system_prompt=self.system_prompt,
        )

        try:
            self.memory.add_exchange("user", user_input)
            self.memory.add_exchange("assistant", response)
        except Exception:
            if logger:
                logger.warning("agent_memory_write_failed", agent_id=self.agent_id, name=self.name)

        return {
            "output": response,
            "metadata": {
                "agent": self.name,
                "retrieved_context": retrieved,
                "recent_context": recent_context,
            },
        }
