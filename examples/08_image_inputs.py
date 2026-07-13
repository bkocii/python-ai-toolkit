from ai.client import AIClient
from ai.images import ImageInput


def main() -> None:
    ai = AIClient()

    image = ImageInput(
        source="https://api.nga.gov/iiif/a2e6da57-3cd1-4235-b20e-95dcaefed6c8/full/!800,800/0/default.jpg",
    )

    result = ai.ask_with_images(
        prompt="Describe this image in one short paragraph.",
        images=[image],
    )

    print(result.data)
    print()
    print(f"Model: {result.model}")
    print(f"Request ID: {result.request_id}")


if __name__ == "__main__":
    main()
