from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

__all__ = ["BaseAgent", "BaseAgentConfig"]


try:
    import structlog

    logger = structlog.get_logger(__name__)
except Exception:  # pragma: no cover
    logger = None  # fallback if structlog is not available


# Try to import centralized tracing; fall back to a no-op if not available
try:
    from src.observability.tracing import trace_agent_call  # type: ignore
except Exception:  # pragma: no cover
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

        if logger is not None:
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
        """
        Implement the core logic of the agent.

        Should return a dict like:
        {
            "output": <str or structured result>,
            "metadata": {...}
        }
        """
        raise NotImplementedError

    def _build_messages(
        self,
        user_input: str,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> List[BaseMessage]:
        rag_augmented = self.memory.rag_query(user_input)
        recent_context = self.memory.get_recent_context()

        messages: List[BaseMessage] = [SystemMessage(content=self.system_prompt)]

        if recent_context:
            messages.append(
                SystemMessage(
                    content="Previous conversation:\n" + str(recent_context)
                )
            )

        if extra_context:
            messages.append(
                SystemMessage(content="Extra context:\n" + str(extra_context))
            )

        messages.append(HumanMessage(content=rag_augmented))
        return messages

    def run(
        self,
        user_input: str,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        High-level entrypoint used by the CLI / router.

        - Retrieves semantic + recent context from memory (RAG).
        - Builds an augmented prompt for the LLM.
        - Invokes the LLM safely.
        - Logs and persists the exchange.
        """
        messages = self._build_messages(user_input=user_input, extra_context=extra_context)

        try:
            response_obj = self.llm.invoke(messages)
            response = (
                response_obj.content
                if hasattr(response_obj, "content")
                else str(response_obj)
            )
        except Exception as e:  # pragma: no cover
            response = f"(Error invoking LLM: {e})"
            if logger is not None:
                logger.error(
                    "agent_llm_error",
                    agent_id=self.agent_id,
                    name=self.name,
                    error=str(e),
                )

        try:
            recent_context = self.memory.get_recent_context()
        except Exception:  # pragma: no cover
            recent_context = None

        trace_agent_call(
            agent_name=self.name,
            agent_id=self.agent_id,
            user_input=user_input,
            response=response,
            context=recent_context,
            system_prompt=self.system_prompt,
        )

        try:
            self.memory.add_exchange("user", user_input)
            self.memory.add_exchange("assistant", response)
        except Exception:  # pragma: no cover
            if logger is not None:
                logger.warning(
                    "agent_memory_write_failed",
                    agent_id=self.agent_id,
                    name=self.name,
                )

        return response