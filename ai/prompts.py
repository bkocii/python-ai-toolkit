class PromptBuilder:
    """
    Small helper for building consistent prompts.

    This avoids messy f-strings spread across the whole project.
    """

    def __init__(self):
        self.sections: list[tuple[str, str]] = []

    def add(self, title: str, content: str) -> "PromptBuilder":
        self.sections.append((title.strip(), content.strip()))
        return self

    def build(self) -> str:
        return "\n\n".join(
            f"{title}:\n{content}" for title, content in self.sections
        )