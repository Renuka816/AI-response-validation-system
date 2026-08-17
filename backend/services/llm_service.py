import os
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

print("OpenAI API Key loaded:", bool(OPENAI_API_KEY))
print("Anthropic API Key loaded:", bool(ANTHROPIC_API_KEY))

openai_client = (
    OpenAI(api_key=OPENAI_API_KEY)
    if OPENAI_API_KEY
    else None
)

anthropic_client = (
    Anthropic(api_key=ANTHROPIC_API_KEY)
    if ANTHROPIC_API_KEY
    else None
)


class LLMService:

    @staticmethod
    def generate(prompt, model_name="gpt-4o"):

        if model_name == "gpt-4o":

            if not openai_client:
                raise ValueError(
                    "OPENAI_API_KEY is missing. "
                    "Check your .env file."
                )

            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert AI response "
                            "quality evaluator. "
                            "Evaluate responses objectively "
                            "and return only valid JSON."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )

            return response.choices[0].message.content

        elif model_name == "claude-sonnet-4":

            if not anthropic_client:
                raise ValueError(
                    "ANTHROPIC_API_KEY is missing. "
                    "Check your .env file."
                )

            response = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                temperature=0,
                system=(
                    "You are an expert AI response "
                    "quality evaluator. "
                    "Evaluate responses objectively "
                    "and return only valid JSON."
                ),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.content[0].text

        else:

            raise ValueError(
                f"Unsupported evaluation model: {model_name}"
            )