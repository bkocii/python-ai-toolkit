from pydantic import BaseModel
import pytest

from ai.client import AIClient
from ai.exceptions import AIProviderError
from ai.executor import RequestExecutor
from ai.images import ImageInput, ImageInputType
from ai.providers.base import BaseAIProvider
from ai.providers.openai_provider import OpenAIProvider
from ai.schemas import ProviderResponse


class ProductInfo(BaseModel):
    name: str
    color: str


class FakeImageProvider(BaseAIProvider):
    def __init__(self, response_text: str = "image response"):
        self.response_text = response_text
        self.received_prompt = None
        self.received_images = None

    def ask_text(self, prompt: str) -> ProviderResponse:
        return ProviderResponse(text="plain response")

    def ask_with_images(
        self,
        prompt: str,
        images: list[ImageInput],
    ) -> ProviderResponse:
        self.received_prompt = prompt
        self.received_images = images

        return ProviderResponse(text=self.response_text)


class FakeNonImageProvider(BaseAIProvider):
    def ask_text(self, prompt: str) -> ProviderResponse:
        return ProviderResponse(text="plain response")


def test_image_input_defaults_to_url_type():
    image = ImageInput(
        source="https://example.com/image.jpg",
    )

    assert image.source == "https://example.com/image.jpg"
    assert image.type == ImageInputType.URL
    assert image.detail is None


def test_image_input_supports_base64_type():
    image = ImageInput(
        source="data:image/png;base64,abc123",
        type=ImageInputType.BASE64,
        detail="low",
    )

    assert image.source == "data:image/png;base64,abc123"
    assert image.type == ImageInputType.BASE64
    assert image.detail == "low"


def test_base_provider_ask_with_images_raises_helpful_error():
    provider = FakeNonImageProvider()

    with pytest.raises(
        AIProviderError,
        match="does not support image inputs",
    ):
        provider.ask_with_images(
            prompt="Describe this image.",
            images=[
                ImageInput(
                    source="https://example.com/image.jpg",
                )
            ],
        )


def test_request_executor_execute_with_images_returns_text_result():
    provider = FakeImageProvider("A red product box.")
    executor = RequestExecutor(
        provider=provider,
        model="fake-model",
    )
    image = ImageInput(
        source="https://example.com/product.jpg",
    )

    result = executor.execute_with_images(
        prompt="Describe this image.",
        images=[image],
    )

    assert result.data == "A red product box."
    assert result.raw_response == "A red product box."
    assert provider.received_prompt == "Describe this image."
    assert provider.received_images == [image]


def test_request_executor_execute_with_images_returns_structured_result():
    provider = FakeImageProvider('{"name": "Bottle", "color": "green"}')
    executor = RequestExecutor(
        provider=provider,
        model="fake-model",
    )

    result = executor.execute_with_images(
        prompt="Extract product info.",
        images=[
            ImageInput(
                source="https://example.com/product.jpg",
            )
        ],
        response_type=ProductInfo,
    )

    assert isinstance(result.data, ProductInfo)
    assert result.data.name == "Bottle"
    assert result.data.color == "green"


def test_ai_client_ask_with_images_delegates_to_executor():
    class FakeExecutor:
        def execute_with_images(
            self,
            prompt,
            images,
            response_type=None,
        ):
            return {
                "prompt": prompt,
                "images": images,
                "response_type": response_type,
            }

    ai = AIClient.__new__(AIClient)
    ai.executor = FakeExecutor()

    image = ImageInput(
        source="https://example.com/image.jpg",
    )

    result = ai.ask_with_images(
        prompt="Describe this image.",
        images=[image],
        response_type=ProductInfo,
    )

    assert result["prompt"] == "Describe this image."
    assert result["images"] == [image]
    assert result["response_type"] is ProductInfo


def test_openai_provider_converts_image_input_to_openai_format():
    provider = OpenAIProvider.__new__(OpenAIProvider)

    image = ImageInput(
        source="https://example.com/image.jpg",
    )

    result = provider._to_openai_image_content(image)

    assert result == {
        "type": "input_image",
        "image_url": "https://example.com/image.jpg",
    }


def test_openai_provider_includes_image_detail_when_provided():
    provider = OpenAIProvider.__new__(OpenAIProvider)

    image = ImageInput(
        source="https://example.com/image.jpg",
        detail="low",
    )

    result = provider._to_openai_image_content(image)

    assert result == {
        "type": "input_image",
        "image_url": "https://example.com/image.jpg",
        "detail": "low",
    }
