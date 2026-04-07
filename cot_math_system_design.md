# Chain-of-Thought Math Solver System Design

## Overview
This document describes a structured system for solving multi-step math problems using Chain-of-Thought (CoT) reasoning and the OpenAI API. The design focuses on clarity, strong prompt alignment, and a repeatable programmatic workflow.

## What is Chain-of-Thought Reasoning?
Chain-of-Thought reasoning is a prompting technique that encourages an LLM to generate intermediate reasoning steps explicitly before producing a final answer. For math problems, CoT improves performance by:
- breaking complex problems into smaller logical steps,
- making the reasoning process transparent,
- reducing calculation and inference errors,
- allowing verification of each intermediate result.

## Why CoT Improves Math Problem Solving
Multi-step math problems often require sequencing reasoning, defining variables, and performing arithmetic in order. CoT helps because it:
1. forces the model to structure its logic,
2. exposes intermediate values for validation,
3. avoids jumping directly to the answer,
4. reduces hallucination by grounding each step in explicit reasoning.

## Architecture
The solution architecture follows a clear workflow:

1. **User Input**
   - User provides a math problem in natural language.
   - Example: "A rectangle has perimeter 26 and length 8. What is its width?"

2. **Prompt Design**
   - A prompt template instructs the model to solve the problem using numbered reasoning steps.
   - The template requires a structured output:
     - Problem restatement,
     - Step-by-step reasoning,
     - Final answer.

3. **OpenAI API Call**
   - The Python script constructs the prompt and sends it to OpenAI using the ChatCompletion API.
   - The request uses low temperature for deterministic reasoning and a suitable model.

4. **Response Handling**
   - The script receives the model response,
   - validates the structure,
   - prints the reasoning trace and final answer,
   - handles API or input errors gracefully.

## Prompt Template
Use a prompt template that is explicit and structured. Example:

```text
You are a math reasoning assistant.

Problem: {problem}

Solve this problem using Chain-of-Thought reasoning.
Provide the output in the exact structure below:

Problem: <restate the problem>
Reasoning:
1. <first calculation or logical step>
2. <next step>
...
Final Answer: <numeric result or expression>
```

### Key prompt principles
- Use explicit numbered steps.
- Ask the model to restate the problem briefly.
- Request a clean `Final Answer` section.
- Keep the instructions concise but unambiguous.
- Prefer deterministic settings (`temperature=0.0`).

## Python Script: `cot_math_solver.py`
The working script implements:
- environment validation,
- prompt construction,
- OpenAI API invocation,
- result display,
- basic error handling.

It uses the OpenAI Python client and expects `OPENAI_API_KEY` in the environment.

## Example Problem
**Input:**
"A rectangle has a perimeter of 26 meters and a length of 8 meters. What is the width?"

**Expected CoT flow:**
1. Restate the problem.
2. Define the perimeter formula: `P = 2 * (length + width)`.
3. Substitute values: `26 = 2 * (8 + width)`.
4. Solve for width: `13 = 8 + width`, so `width = 5`.
5. Provide the final answer.

## Validation and Error Handling
The script includes:
- validation for non-empty problem statements,
- an API key presence check,
- OpenAI API exception handling,
- user-friendly error messages.

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the API key:
   ```bash
   export OPENAI_API_KEY="your_key_here"
   ```
   or on Windows:
   ```powershell
   $env:OPENAI_API_KEY = "your_key_here"
   ```
3. Run the solver:
   ```bash
   python cot_math_solver.py "A rectangle has a perimeter of 26 meters and a length of 8 meters. What is the width?"
   ```

## Notes
This design is intentionally focused on math problem solving and avoids unrelated features. It can be extended later to support more structured output formats, additional validation, or richer parsing of intermediate reasoning.
