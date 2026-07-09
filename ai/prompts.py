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
        return "\n\n".join(f"{title}:\n{content}" for title, content in self.sections)


class PromptTemplate:
    """
    Reusable prompt template based on Python format strings.
    """

    def __init__(self, template: str):
        if not template.strip():
            raise ValueError("Prompt template cannot be empty.")

        self.template = template

    def render(self, **values: object) -> str:
        try:
            return self.template.format(**values)
        except KeyError as exc:
            missing_key = exc.args[0]
            raise ValueError(
                f"Missing value for prompt template variable: {missing_key}"
            ) from exc

