from enum import StrEnum

from pydantic import BaseModel, Field


class ImageInputType(StrEnum):
    URL = "url"
    BASE64 = "base64"


class ImageInput(BaseModel):
    """
    Provider-independent image input.

    source:
        URL or Base64 data URL.

    type:
        Describes how the image is provided.
    """

    source: str
    type: ImageInputType = ImageInputType.URL
    detail: str | None = None


class ImageRequest(BaseModel):
    """
    Text prompt plus one or more image inputs.
    """

    prompt: str
    images: list[ImageInput] = Field(default_factory=list)
