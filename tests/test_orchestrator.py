import pytest

from ai.agent import AgentResponse, BaseAgent
from ai.memory import ConversationMessage, MessageRole
from ai.orchestrator import (
    AgentRunResult,
    MultiAgentOrchestrator,
    MultiAgentResponse,
)


class FakeAgent(BaseAgent):
    def __init__(self, output: str):
        self.output = output
        self.received_message = None
        self.received_metadata = None

    def run(
        self,
        message: str,
        metadata: dict[str, str] | None = None,
    ) -> AgentResponse:
        self.received_message = message
        self.received_metadata = metadata

        return AgentResponse(
            output=self.output,
            model="fake-model",
            request_id=f"request-{self.output}",
            messages=[
                ConversationMessage(
                    role=MessageRole.ASSISTANT,
                    content=self.output,
                )
            ],
        )


class FailingAgent(BaseAgent):
    def run(
        self,
        message: str,
        metadata: dict[str, str] | None = None,
    ) -> AgentResponse:
        raise RuntimeError("Agent failed")


def make_response(output: str) -> AgentResponse:
    return AgentResponse(
        output=output,
        model="fake-model",
        request_id="request-123",
        messages=[
            ConversationMessage(
                role=MessageRole.ASSISTANT,
                content=output,
            )
        ],
    )


def test_agent_run_result_stores_successful_response():
    response = make_response("Agent output")

    result = AgentRunResult(
        agent_name="technical",
        response=response,
    )

    assert result.agent_name == "technical"
    assert result.response == response
    assert result.success is True
    assert result.error is None


def test_agent_run_result_allows_failed_response_without_agent_response():
    result = AgentRunResult(
        agent_name="technical",
        response=None,
        success=False,
        error="Agent failed",
    )

    assert result.agent_name == "technical"
    assert result.response is None
    assert result.success is False
    assert result.error == "Agent failed"


def test_multi_agent_response_success_is_true_when_all_results_succeed():
    response = MultiAgentResponse(
        results=[
            AgentRunResult(
                agent_name="first",
                response=make_response("First"),
            ),
            AgentRunResult(
                agent_name="second",
                response=make_response("Second"),
            ),
        ]
    )

    assert response.success is True


def test_multi_agent_response_success_is_false_when_any_result_fails():
    response = MultiAgentResponse(
        results=[
            AgentRunResult(
                agent_name="first",
                response=make_response("First"),
            ),
            AgentRunResult(
                agent_name="second",
                response=None,
                success=False,
                error="Failed",
            ),
        ]
    )

    assert response.success is False


def test_multi_agent_response_final_output_returns_last_successful_output():
    response = MultiAgentResponse(
        results=[
            AgentRunResult(
                agent_name="first",
                response=make_response("First"),
            ),
            AgentRunResult(
                agent_name="second",
                response=make_response("Second"),
            ),
        ]
    )

    assert response.final_output == "Second"


def test_multi_agent_response_final_output_returns_none_without_successful_response():
    response = MultiAgentResponse(
        results=[
            AgentRunResult(
                agent_name="first",
                response=None,
                success=False,
                error="Failed",
            )
        ]
    )

    assert response.final_output is None


def test_orchestrator_registers_agents():
    orchestrator = MultiAgentOrchestrator()

    orchestrator.register_agent(
        "technical",
        FakeAgent("Technical output"),
    )

    assert orchestrator.agent_names() == ("technical",)


def test_orchestrator_accepts_initial_agents():
    orchestrator = MultiAgentOrchestrator(
        agents={
            "technical": FakeAgent("Technical output"),
            "reviewer": FakeAgent("Reviewer output"),
        }
    )

    assert orchestrator.agent_names() == ("reviewer", "technical")


def test_orchestrator_rejects_empty_agent_name():
    orchestrator = MultiAgentOrchestrator()

    with pytest.raises(
        ValueError,
        match="Agent name cannot be empty",
    ):
        orchestrator.register_agent(
            "   ",
            FakeAgent("Output"),
        )


def test_orchestrator_rejects_duplicate_agent_name():
    orchestrator = MultiAgentOrchestrator()

    orchestrator.register_agent(
        "technical",
        FakeAgent("First output"),
    )

    with pytest.raises(
        ValueError,
        match="Agent 'technical' is already registered",
    ):
        orchestrator.register_agent(
            "technical",
            FakeAgent("Second output"),
        )


def test_orchestrator_run_agent_runs_selected_agent():
    agent = FakeAgent("Technical output")

    orchestrator = MultiAgentOrchestrator(
        agents={
            "technical": agent,
        }
    )

    result = orchestrator.run_agent(
        agent_name="technical",
        message="Explain Redis.",
        metadata={"user_id": "123"},
    )

    assert result.success is True
    assert result.agent_name == "technical"
    assert result.response is not None
    assert result.response.output == "Technical output"
    assert agent.received_message == "Explain Redis."
    assert agent.received_metadata == {"user_id": "123"}


def test_orchestrator_run_agent_rejects_unknown_agent():
    orchestrator = MultiAgentOrchestrator()

    with pytest.raises(
        ValueError,
        match="Unknown agent: missing",
    ):
        orchestrator.run_agent(
            agent_name="missing",
            message="Hello",
        )


def test_orchestrator_run_agent_converts_agent_exception_to_failed_result():
    orchestrator = MultiAgentOrchestrator(
        agents={
            "failing": FailingAgent(),
        }
    )

    result = orchestrator.run_agent(
        agent_name="failing",
        message="Hello",
    )

    assert result.success is False
    assert result.agent_name == "failing"
    assert result.response is None
    assert result.error == "Agent failed"


def test_orchestrator_run_sequence_runs_agents_in_order():
    first_agent = FakeAgent("First output")
    second_agent = FakeAgent("Second output")

    orchestrator = MultiAgentOrchestrator(
        agents={
            "first": first_agent,
            "second": second_agent,
        }
    )

    response = orchestrator.run_sequence(
        agent_names=["first", "second"],
        message="Original message",
    )

    assert response.success is True
    assert len(response.results) == 2
    assert response.results[0].agent_name == "first"
    assert response.results[1].agent_name == "second"
    assert response.final_output == "Second output"


def test_orchestrator_run_sequence_passes_previous_output_to_next_agent():
    first_agent = FakeAgent("First output")
    second_agent = FakeAgent("Second output")

    orchestrator = MultiAgentOrchestrator(
        agents={
            "first": first_agent,
            "second": second_agent,
        }
    )

    orchestrator.run_sequence(
        agent_names=["first", "second"],
        message="Original message",
    )

    assert first_agent.received_message == "Original message"
    assert second_agent.received_message == "First output"


def test_orchestrator_run_sequence_passes_metadata_to_each_agent():
    first_agent = FakeAgent("First output")
    second_agent = FakeAgent("Second output")

    orchestrator = MultiAgentOrchestrator(
        agents={
            "first": first_agent,
            "second": second_agent,
        }
    )

    orchestrator.run_sequence(
        agent_names=["first", "second"],
        message="Original message",
        metadata={"workflow_id": "abc"},
    )

    assert first_agent.received_metadata == {"workflow_id": "abc"}
    assert second_agent.received_metadata == {"workflow_id": "abc"}


def test_orchestrator_run_sequence_stops_on_failure():
    first_agent = FakeAgent("First output")

    orchestrator = MultiAgentOrchestrator(
        agents={
            "first": first_agent,
            "failing": FailingAgent(),
            "third": FakeAgent("Third output"),
        }
    )

    response = orchestrator.run_sequence(
        agent_names=["first", "failing", "third"],
        message="Original message",
    )

    assert response.success is False
    assert len(response.results) == 2
    assert response.results[0].agent_name == "first"
    assert response.results[1].agent_name == "failing"
    assert response.results[1].error == "Agent failed"


def test_orchestrator_run_sequence_rejects_empty_sequence():
    orchestrator = MultiAgentOrchestrator(
        agents={
            "first": FakeAgent("First output"),
        }
    )

    with pytest.raises(
        ValueError,
        match="Agent sequence cannot be empty",
    ):
        orchestrator.run_sequence(
            agent_names=[],
            message="Original message",
        )


def test_orchestrator_run_sequence_rejects_empty_message():
    orchestrator = MultiAgentOrchestrator(
        agents={
            "first": FakeAgent("First output"),
        }
    )

    with pytest.raises(
        ValueError,
        match="Multi-agent message cannot be empty",
    ):
        orchestrator.run_sequence(
            agent_names=["first"],
            message="   ",
        )
