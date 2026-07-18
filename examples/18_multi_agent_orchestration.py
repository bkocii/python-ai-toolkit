from ai.agent import Agent
from ai.client import AIClient
from ai.memory import InMemoryConversationMemory
from ai.orchestrator import MultiAgentOrchestrator


def main() -> None:
    ai = AIClient()

    technical_agent = Agent(
        ai_client=ai,
        instructions=(
            "You are a technical assistant. "
            "Explain the concept clearly and accurately."
        ),
        memory=InMemoryConversationMemory(),
    )

    reviewer_agent = Agent(
        ai_client=ai,
        instructions=(
            "You are a reviewer. "
            "Improve the previous answer for clarity and correctness. "
            "Return only the improved answer. "
            "Do not include review notes, scoring, commentary, or bullet-by-bullet critique."
        ),
        memory=InMemoryConversationMemory(),
    )

    summary_agent = Agent(
        ai_client=ai,
        instructions=(
            "You are a summarizer. "
            "Make the previous answer shorter and easier for a beginner. "
            "Return only the final user-facing answer. "
            "Do not mention that you are summarizing, reviewing, or improving anything."
        ),
        memory=InMemoryConversationMemory(),
    )

    orchestrator = MultiAgentOrchestrator(
        agents={
            "technical": technical_agent,
            "reviewer": reviewer_agent,
            "summary": summary_agent,
        }
    )

    response = orchestrator.run_sequence(
        agent_names=[
            "technical",
            "reviewer",
            "summary",
        ],
        message="Explain how Redis can help a Django application.",
        metadata={
            "workflow": "technical_review_summary",
        },
    )

    print("Success:")
    print(response.success)
    print()

    print("Final output:")
    print(response.final_output)
    print()

    print("Agent results:")

    for result in response.results:
        print(f"- Agent: {result.agent_name}")
        print(f"  Success: {result.success}")

        if result.response is not None:
            print(f"  Output: {result.response.output[:200]}...")

        if result.error:
            print(f"  Error: {result.error}")


if __name__ == "__main__":
    main()
