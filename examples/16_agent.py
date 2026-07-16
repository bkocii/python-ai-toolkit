from ai.agent import Agent
from ai.client import AIClient
from ai.memory import InMemoryConversationMemory


def main() -> None:
    ai = AIClient()
    memory = InMemoryConversationMemory()

    agent = Agent(
        ai_client=ai,
        instructions=(
            "You are a concise technical assistant. "
            "Answer clearly and remember the previous conversation."
        ),
        memory=memory,
        memory_limit=6,
    )

    first_response = agent.run("What is Redis?")
    print("First response:")
    print(first_response.output)
    print()

    second_response = agent.run("Can it help with Django apps?")
    print("Second response:")
    print(second_response.output)
    print()

    print("Conversation memory:")

    for message in second_response.messages:
        print(f"- {message.role}: {message.content}")


if __name__ == "__main__":
    main()
