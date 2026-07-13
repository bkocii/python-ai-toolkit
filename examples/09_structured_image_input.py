from pydantic import BaseModel

from ai.client import AIClient
from ai.images import ImageInput


class ImageDescription(BaseModel):
    subject: str
    colors: list[str]
    visible_text: str | None = None


def main() -> None:
    ai = AIClient()

    image = ImageInput(
        source="https://api.nga.gov/iiif/a2e6da57-3cd1-4235-b20e-95dcaefed6c8/full/!800,800/0/default.jpg",
    )

    result = ai.ask_with_images(
        prompt="Extract structured information from this image.",
        images=[image],
        response_type=ImageDescription,
    )

    print(result.data)
    print()
    print(f"Subject: {result.data.subject}")
    print(f"Colors: {', '.join(result.data.colors)}")
    print(f"Visible text: {result.data.visible_text}")


if __name__ == "__main__":
    main()
