import os
import sys
from typing import Optional
from groq import Groq

BASE_PROMPT = """
You are a customer support chatbot.
Your goals:
- Be polite, empathetic, and professional.
- Understand the customers main issue.
- Provide step-by-step resolution.
- Avoid hallucinations or unsupported claims.
- Ask one simple clarification question if key details are missing.
- End with a self-check that confirms the response solves the issue.
User message:
{user_message}
Response structure:
1. Greeting and empathy
2. Confirm the issue
3. Solution steps
4. Closing reassurance
5. Self-check summary
"""

SCENARIO_PROMPTS = {
    "default": "Handle the user issue as a standard support request.",
    "angry": "Handle the user issue with extra empathy and calm reassurance.",
    "confused": "Explain the solution in simple, non-technical language.",
    "simple": "Give a short, direct answer for a simple request.",
}

def build_prompt(user_message: str, scenario: str = "default") -> str:
    scenario_instruction = SCENARIO_PROMPTS.get(scenario, SCENARIO_PROMPTS["default"])
    return BASE_PROMPT.format(user_message=user_message) + "\n" + scenario_instruction + "\n"

def generate_response(prompt: str, model: str = "llama-3.3-70b-versatile", max_tokens: int = 400) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY is not set.")
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a professional customer support assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

def run_chatbot(user_message: Optional[str] = None, scenario: str = "default") -> None:
    if user_message is None:
        print("Customer Support Chatbot (Groq)")
        print("Enter a user message, or type 'exit' to quit.")
        while True:
            user_message = input("\nUser: ").strip()
            if not user_message or user_message.lower() == "exit":
                print("Goodbye.")
                break
            prompt = build_prompt(user_message, scenario)
            try:
                response = generate_response(prompt)
                print("\nSupport Bot:\n" + response)
            except Exception as exc:
                print(f"Error: {exc}")
                break
    else:
        prompt = build_prompt(user_message, scenario)
        response = generate_response(prompt)
        print(response)

def main() -> None:
    if len(sys.argv) >= 2:
        user_message = " ".join(sys.argv[1:])
        run_chatbot(user_message)
    else:
        run_chatbot()

if __name__ == "__main__":
    main()
