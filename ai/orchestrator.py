from pydantic import BaseModel, Field
from ai.agent import BaseAgent
from ai.agent import AgentResponse


class AgentRunResult(BaseModel):
    """
    Result from running one named agent.
    """

    agent_name: str
    response: AgentResponse | None = None
    success: bool = True
    error: str | None = None


class MultiAgentResponse(BaseModel):
    """
    Response returned by a multi-agent orchestrator.
    """

    results: list[AgentRunResult] = Field(default_factory=list)

    @property
    def success(self) -> bool:
        """
        Return True only if all agent runs succeeded.
        """
        return all(result.success for result in self.results)

    @property
    def final_output(self) -> str | None:
        """
        Return the output from the last successful agent response.
        """
        successful_results = [
            result
            for result in self.results
            if result.success and result.response is not None
        ]

        if not successful_results:
            return None

        return successful_results[-1].response.output


class MultiAgentOrchestrator:
    """
    Explicit multi-agent orchestrator.

    The orchestrator runs named agents either individually or sequentially.
    It does not perform autonomous routing or recursive agent loops.
    """

    def __init__(
        self,
        agents: dict[str, BaseAgent] | None = None,
    ):
        self._agents: dict[str, BaseAgent] = {}

        for name, agent in (agents or {}).items():
            self.register_agent(name, agent)

    def register_agent(
        self,
        name: str,
        agent: BaseAgent,
    ) -> None:
        """
        Register one named agent.
        """
        if not name.strip():
            raise ValueError("Agent name cannot be empty.")

        if name in self._agents:
            raise ValueError(f"Agent '{name}' is already registered.")

        self._agents[name] = agent

    def agent_names(self) -> tuple[str, ...]:
        """
        Return registered agent names.
        """
        return tuple(sorted(self._agents.keys()))

    def run_agent(
        self,
        agent_name: str,
        message: str,
        metadata: dict[str, str] | None = None,
    ) -> AgentRunResult:
        """
        Run one selected agent by name.
        """
        agent = self._agents.get(agent_name)

        if agent is None:
            raise ValueError(f"Unknown agent: {agent_name}")

        try:
            response = agent.run(
                message=message,
                metadata=metadata,
            )

            return AgentRunResult(
                agent_name=agent_name,
                response=response,
                success=True,
            )

        except Exception as exc:
            return AgentRunResult(
                agent_name=agent_name,
                response=None,
                success=False,
                error=str(exc),
            )

    def run_sequence(
        self,
        agent_names: list[str],
        message: str,
        metadata: dict[str, str] | None = None,
    ) -> MultiAgentResponse:
        """
        Run multiple agents sequentially.

        The output from each successful agent becomes the input message
        for the next agent.
        """
        if not agent_names:
            raise ValueError("Agent sequence cannot be empty.")

        if not message.strip():
            raise ValueError("Multi-agent message cannot be empty.")

        results: list[AgentRunResult] = []
        current_message = message

        for agent_name in agent_names:
            result = self.run_agent(
                agent_name=agent_name,
                message=current_message,
                metadata=metadata,
            )

            results.append(result)

            if not result.success:
                break

            if result.response is not None:
                current_message = result.response.output

        return MultiAgentResponse(results=results)
