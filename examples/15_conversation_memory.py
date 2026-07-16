from ai.memory import (
    InMemoryConversationMemory,
    format_conversation_messages,
)


def main() -> None:
    memory = InMemoryConversationMemory()

    memory.add_system_message("You are a helpful AI assistant.")
    memory.add_user_message("What is Redis?")
    memory.add_assistant_message("Redis is often used as a cache and message broker.")
    memory.add_user_message("Can it help with Django apps?")

    print("All messages:")
    print(format_conversation_messages(memory.messages()))
    print()

    print("Recent messages:")
    print(format_conversation_messages(memory.recent_messages(limit=2)))


if __name__ == "__main__":
    main()
