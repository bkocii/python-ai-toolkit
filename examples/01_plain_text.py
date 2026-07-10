from ai.client import AIClient


def main() -> None:
    ai = AIClient()

    result = ai.ask(
        "Explain what dependency injection is in one short paragraph."
    )

    print(result.data)
    print()
    print(f"Model: {result.model}")
    print(f"Request ID: {result.request_id}")


if __name__ == "__main__":
    main()
