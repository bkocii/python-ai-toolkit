from pydantic import BaseModel

from ai.client import AIClient


class Contact(BaseModel):
    name: str
    email: str
    company: str


def main() -> None:
    ai = AIClient()

    prompt = """
    Extract the person's information from the following text.

    John Smith works at OpenAI.
    His email is john@example.com.
    """

    result = ai.ask(
        prompt=prompt,
        response_type=Contact,
    )

    print(result.data)
    print()
    print(result.data.name)
    print(result.data.email)
    print(result.data.company)


if __name__ == "__main__":
    main()
