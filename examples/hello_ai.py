from ai.client import AIClient


def main():
    ai = AIClient()
    response = ai.ask_text("Reply with exactly: AI toolkit is working")
    print(response)


if __name__ == "__main__":
    main()
