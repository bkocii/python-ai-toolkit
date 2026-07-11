from pydantic import BaseModel

from ai.client import AIClient


class ProjectIdea(BaseModel):
    title: str
    difficulty: str
    reason: str


def main() -> None:
    ai = AIClient()

    result = (
        ai.request()
        .prompt("Recommend one beginner-friendly Python automation project.")
        .response_type(ProjectIdea)
        .execute()
    )

    print(result.data.title)
    print(result.data.difficulty)
    print(result.data.reason)


if __name__ == "__main__":
    main()
