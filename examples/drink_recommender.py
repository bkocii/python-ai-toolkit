import json

from pydantic import BaseModel

from ai.client import AIClient


class DrinkRecommendation(BaseModel):
    recommended_item: str
    reason: str


MENU = [
    {
        "name": "Strawberry Mojito",
        "price": 2.5,
        "alcoholic": False,
        "taste": ["sweet", "fruity", "mint", "refreshing"],
        "available": True,
    },
    {
        "name": "Genius Green",
        "price": 2.5,
        "alcoholic": False,
        "taste": ["kiwi", "fresh", "fruity", "refreshing"],
        "available": True,
    },
    {
        "name": "Vodka Sour",
        "price": 7.5,
        "alcoholic": True,
        "taste": ["kiwi", "fresh", "fruity", "refreshing"],
        "available": True,
    },
]


def main():
    ai = AIClient()

    prompt = f"""
You are a bar recommendation assistant.

User wants:
Fresh, fruity, with alcohol, around 5 euros.

Candidate products:
{json.dumps(MENU, indent=2)}

Recommend exactly one product from the candidate list.
Do not invent products.
"""

    result = ai.ask(prompt, response_type=DrinkRecommendation)

    print(result.data.model_dump_json(indent=2))
    print(result.token_usage)


if __name__ == "__main__":
    main()
