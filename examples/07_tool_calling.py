from ai.client import AIClient
from ai.tools import ToolDefinition


def main() -> None:
    ai = AIClient()

    weather_tool = ToolDefinition(
        name="get_weather",
        description="Get the current weather for a city.",
        parameters={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name, for example Paris or London.",
                }
            },
            "required": ["location"],
            "additionalProperties": False,
        },
    )

    response = ai.ask_with_tools(
        prompt="What is the weather in Paris?",
        tools=[weather_tool],
    )

    if response.text:
        print(response.text)

    for tool_call in response.tool_calls:
        print("Tool requested:")
        print(f"Name: {tool_call.name}")
        print(f"Arguments: {tool_call.arguments}")
        print(f"Call ID: {tool_call.call_id}")


if __name__ == "__main__":
    main()
