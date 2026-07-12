import asyncio

from ai.async_client import AsyncAIClient


async def main() -> None:
    ai = AsyncAIClient()

    result = await ai.ask("Explain dependency injection in one short paragraph.")

    print(result.data)
    print()
    print(f"Model: {result.model}")
    print(f"Request ID: {result.request_id}")


if __name__ == "__main__":
    asyncio.run(main())
