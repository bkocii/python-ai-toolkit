import base64
from pathlib import Path

from ai.client import AIClient
from ai.images import ImageInput, ImageInputType


def image_file_to_data_url(path: str) -> str:
    image_path = Path(path)
    suffix = image_path.suffix.lower()

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    mime_type = mime_types.get(suffix)

    if mime_type is None:
        raise ValueError(
            f"Unsupported image type '{suffix}'. " "Use .jpg, .jpeg, .png, or .webp."
        )

    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def main() -> None:
    ai = AIClient()

    image = ImageInput(
        source=image_file_to_data_url("examples/sketch.jpg"),
        type=ImageInputType.BASE64,
    )

    result = ai.ask_with_images(
        prompt="Describe this image in one short paragraph.",
        images=[image],
    )

    print(result.data)


if __name__ == "__main__":
    main()
