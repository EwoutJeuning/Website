"""
Recipe Generator — No Onion, No Garlic
Uses the Claude API to generate recipes that are completely free of onion and garlic.
"""

import anthropic

SYSTEM_PROMPT = """You are a professional chef who specializes in cooking without onion and garlic.
Your recipes MUST NEVER include any of the following ingredients or their derivatives:
- Onion (including green onions, scallions, shallots, leeks, chives)
- Garlic (including garlic powder, garlic salt, garlic oil)

When asked for a recipe, provide:
1. Recipe name
2. A brief description
3. Ingredients list (with quantities)
4. Step-by-step instructions
5. Optional: tips or substitutions

Use asafoetida (hing) as a flavor substitute when appropriate, and feel free to suggest
other aromatics like fennel, celery, or fresh herbs to add depth of flavor."""


def generate_recipe(client: anthropic.Anthropic, request: str) -> None:
    """Stream a recipe from Claude based on the user's request."""
    print("\n--- Recipe ---\n")

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": request}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print("\n\n--------------\n")


def main() -> None:
    client = anthropic.Anthropic()

    print("=" * 50)
    print("  Recipe Generator — Onion & Garlic Free")
    print("=" * 50)
    print("\nType what kind of recipe you'd like, or 'quit' to exit.")
    print("Examples:")
    print("  - A quick pasta dinner")
    print("  - A spicy curry for 4 people")
    print("  - A vegetarian soup using carrots and potatoes")
    print()

    while True:
        try:
            user_input = input("Your request: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        try:
            generate_recipe(client, user_input)
        except anthropic.AuthenticationError:
            print("Error: Invalid API key. Set your ANTHROPIC_API_KEY environment variable.")
            break
        except anthropic.RateLimitError:
            print("Error: Rate limit reached. Please wait a moment and try again.")
        except anthropic.APIError as e:
            print(f"API error: {e}")


if __name__ == "__main__":
    main()
