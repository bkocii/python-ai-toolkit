from ai.client import AIClient


def main() -> None:
    ai = AIClient()

    for chunk in ai.stream("Explain dependency injection in one short paragraph."):
        print(chunk, end="", flush=True)

    print()


if __name__ == "__main__":
    main()
