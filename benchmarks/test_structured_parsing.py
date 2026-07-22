from pydantic import BaseModel

from ai.structured import parse_structured_response


class BenchmarkContact(BaseModel):
    name: str
    email: str
    age: int
    active: bool
    tags: list[str]


STRUCTURED_RESPONSE = """
{
    "name": "Benchmark User",
    "email": "benchmark@example.com",
    "age": 35,
    "active": true,
    "tags": [
        "python",
        "automation",
        "ai"
    ]
}
""".strip()


def test_structured_response_parsing(benchmark):
    result = benchmark(
        parse_structured_response,
        STRUCTURED_RESPONSE,
        BenchmarkContact,
    )

    assert isinstance(result, BenchmarkContact)
    assert result.name == "Benchmark User"
    assert result.email == "benchmark@example.com"
    assert result.age == 35
    assert result.active is True
    assert result.tags == [
        "python",
        "automation",
        "ai",
    ]
