from ai.client import AIClient
from ai.prompts import PromptTemplate


def main() -> None:
    ai = AIClient()

    template = PromptTemplate(
        "Summarize the following text in {language} using {tone} tone:\n\n{text}"
    )

    prompt = template.render(
        language="Chinese",
        tone="complicated",
        text=(
            "Dependency injection is a software design technique where an object "
            "receives the dependencies it needs from the outside instead of "
            "creating them internally."
        ),
    )

    result = ai.ask(prompt)

    print(result.data)


if __name__ == "__main__":
    main()
