# Chain-of-Thought Math Solver

This repository contains a structured Chain-of-Thought math solver using the OpenAI API and Python.

## Files
- `cot_math_system_design.md` - Design document describing the CoT system architecture and prompt template.
- `cot_math_solver.py` - Working Python script that sends math problems to OpenAI with CoT prompting.
- `self_reflecting_code_review_agent.md` - Framework design for a self-reflecting Python code review agent.
- `code_review_agent.py` - Implementation of the self-reflecting code review agent using AST analysis.
- `requirements.txt` - Minimal dependency list.

## Setup
1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
   If `pip` is not recognized on Windows, use:
   ```powershell
   py -m pip install -r requirements.txt
   ```
2. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```
   or on Windows PowerShell:
   ```powershell
   $env:OPENAI_API_KEY = "your_api_key_here"
   ```

## Usage
Run a math problem directly:
```bash
python cot_math_solver.py "A rectangle has a perimeter of 26 meters and a length of 8 meters. What is the width?"
```

Run interactively:
```bash
python cot_math_solver.py
```

Run the built-in example:
```bash
python cot_math_solver.py --example
```

## Code Review Agent

This repository also includes a self-reflecting code review agent that analyzes Python code for issues.

### Usage
Review a Python file:
```bash
python code_review_agent.py your_file.py
```

Example (reviewing the math solver itself):
```bash
python code_review_agent.py cot_math_solver.py
```

The agent performs:
1. AST-based structural analysis
2. Initial code review
3. Self-reflection to validate findings
4. Refined feedback with actionable suggestions

## Notes
The script uses a structured Chain-of-Thought prompt to generate step-by-step reasoning and a clear final answer. Adjust the `model` parameter in `cot_math_solver.py` if you want to use a different OpenAI model.
