import argparse
import os
import sys

import openai

DEFAULT_MODEL = "gpt-4.1"


def get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. Set it in your environment before running the script."
        )
    return api_key


def validate_problem(problem: str) -> str:
    if not problem or not isinstance(problem, str):
        raise ValueError("Problem must be a non-empty string.")
    cleaned = problem.strip()
    if len(cleaned) < 10:
        raise ValueError("Problem description is too short. Provide a complete math problem.")
    return cleaned


def build_cot_math_prompt(problem: str) -> str:
    return (
        "You are a precise math reasoning assistant. "
        "Solve the following problem using Chain-of-Thought reasoning. "
        "Show your intermediate steps as a numbered list and provide a clear final answer.\n\n"
        f"Problem: {problem}\n\n"
        "Output format:\n"
        "Problem: <restate the problem>\n"
        "Reasoning:\n"
        "1. <first step>\n"
        "2. <next step>\n"
        "...\n"
        "Final Answer: <numeric result or expression>\n"
    )


def solve_math_problem(problem: str, model: str = DEFAULT_MODEL, max_tokens: int = 600, temperature: float = 0.0) -> str:
    api_key = get_api_key()
    client = openai.OpenAI(api_key=api_key)

    prompt = build_cot_math_prompt(problem)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert math solver."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=1.0,
    )

    if not response or not hasattr(response, 'choices') or len(response.choices) == 0:
        raise RuntimeError("OpenAI returned an unexpected response format.")

    return response.choices[0].message.content.strip()


def print_solution(output: str) -> None:
    print("\n=== Chain-of-Thought Math Solution ===\n")
    print(output)
    print("\n======================================\n")


def prompt_for_problem() -> str:
    print("Enter a multi-step math problem, then press Enter:")
    problem = input("> ").strip()
    if not problem:
        raise ValueError("No problem entered. Please type a math problem.")
    return problem


def parse_args():
    parser = argparse.ArgumentParser(
        description="Chain-of-Thought math solver using the OpenAI API."
    )
    parser.add_argument(
        "problem",
        nargs="*",
        help="The math problem to solve. If omitted, you will be prompted interactively."
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="OpenAI model to use (default: gpt-4.1)."
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=600,
        help="Maximum completion tokens for the OpenAI response."
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature for deterministic reasoning."
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Solve a built-in example problem."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.example:
        problem = (
            "A rectangle has a perimeter of 26 meters and a length of 8 meters. "
            "What is the width?"
        )
    elif args.problem:
        problem = " ".join(args.problem)
    else:
        problem = prompt_for_problem()

    try:
        validated_problem = validate_problem(problem)
        solution = solve_math_problem(
            validated_problem,
            model=args.model,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )
        print_solution(solution)
    except ValueError as ve:
        print(f"Input Error: {ve}")
        sys.exit(1)
    except EnvironmentError as ee:
        print(f"Environment Error: {ee}")
        sys.exit(1)
    except openai.OpenAIError as oe:
        print(f"OpenAI API Error: {oe}")
        sys.exit(1)
    except RuntimeError as re:
        print(f"Runtime Error: {re}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
