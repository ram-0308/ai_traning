# Self-Reflecting Code Review Agent Framework

## Overview

### Concept of Self-Reflecting Agent
A self-reflecting code review agent is an AI system that not only analyzes code for issues but also evaluates and improves its own analysis through iterative reasoning. This approach mimics human expert review processes where initial assessments are followed by critical self-examination and refinement.

### Why Iterative Refinement Improves Quality
Iterative refinement enhances code review quality by:
- **Reducing false positives**: Self-reflection identifies over-cautious suggestions
- **Increasing accuracy**: Multiple passes catch nuanced issues missed initially
- **Improving specificity**: Refinement makes feedback more actionable and precise
- **Building confidence**: Structured reasoning validates conclusions before final output

## Architecture

The system follows a pipeline architecture:

```
Input Code → AST Parsing → Initial Review → Self-Reflection → Improved Review → Final Output
```

### Components:
1. **Input Processor**: Accepts Python code as string or file
2. **AST Analyzer**: Uses Python's `ast` module for structural analysis
3. **LLM Reviewer**: Claude API-powered review engine with self-reflection
4. **Refinement Loop**: Iterative improvement mechanism
5. **Output Formatter**: Structured feedback presentation

## AST Usage

Python's Abstract Syntax Tree (AST) module provides static code analysis capabilities:

### Key Analysis Techniques:

```python
import ast

def analyze_code(code: str) -> dict:
    tree = ast.parse(code)
    
    # Syntax errors are caught during parsing
    issues = []
    
    # Traverse AST for structural issues
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check function complexity
            if len(node.body) > 20:
                issues.append(f"Function '{node.name}' is too complex")
        
        elif isinstance(node, ast.Name):
            # Track variable usage (requires symbol table)
            pass
    
    return {"ast_issues": issues}
```

### AST-Based Detection:
- **Syntax Errors**: Automatic during `ast.parse()`
- **Unused Variables**: Track `ast.Name` nodes and their contexts
- **Complexity Metrics**: Count statements, nesting levels
- **Import Issues**: Analyze `ast.Import` and `ast.ImportFrom` nodes
- **Control Flow**: Examine loops, conditionals for potential issues

## Prompt Template

### Claude API Integration Structure:

```
You are an expert Python code reviewer. Analyze the provided code and provide structured feedback.

CODE TO REVIEW:
{code}

AST ANALYSIS RESULTS:
{ast_findings}

INSTRUCTION: Perform a 3-stage review process:

STAGE 1 - INITIAL REVIEW:
- Identify potential issues in the code
- Focus on code quality, bugs, and best practices
- Be specific about line numbers and code sections

STAGE 2 - SELF-REFLECTION:
- Critically evaluate your initial review
- Identify any false positives or missed issues
- Assess the accuracy and relevance of each suggestion
- Consider if suggestions are verifiable from the code

STAGE 3 - IMPROVED REVIEW:
- Provide refined feedback incorporating self-reflection insights
- Remove any uncertain or unverifiable suggestions
- Enhance clarity and actionability of remaining feedback
- Structure output as: ISSUE, LOCATION, SEVERITY, DESCRIPTION, SUGGESTION

FINAL OUTPUT FORMAT:
## Code Review Summary
- Total issues found: X
- Issues by severity: High: X, Medium: X, Low: X

## Detailed Issues
1. **Issue Title**
   - **Location**: line X, function Y
   - **Severity**: High/Medium/Low
   - **Description**: Detailed explanation
   - **Suggestion**: Specific improvement recommendation
```

## Iteration Flow

The agent operates in a controlled iteration loop:

1. **Parse Input**: Accept code and run AST analysis
2. **Initial Review**: Generate first-pass feedback using base prompt
3. **Self-Reflection**: Apply critical analysis to initial findings
4. **Refinement Check**: Verify all suggestions are code-derived
5. **Improved Review**: Generate enhanced feedback
6. **Finalization**: Output structured, verified results

### Loop Control:
- Maximum 3 iterations to prevent over-analysis
- Exit early if no improvements identified
- Track changes between iterations for convergence

## Example

### Sample Python Code:
```python
def calculate_average(numbers):
    total = 0
    count = 0
    for num in numbers:
        total += num
        count += 1
    return total / count if count > 0 else 0

# Usage
result = calculate_average([1, 2, 3, 4, 5])
print(f"Average: {result}")
```

### Agent Analysis Process:

**Stage 1 - Initial Review:**
- Potential division by zero (though guarded)
- Manual loop could use built-in `sum()` and `len()`
- No input validation for `numbers` parameter

**Stage 2 - Self-Reflection:**
- Division by zero guard is actually present, so not an issue
- Built-in functions suggestion is valid and improves readability
- Input validation is a good practice but not strictly necessary for this simple function

**Stage 3 - Improved Review:**

## Code Review Summary
- Total issues found: 2
- Issues by severity: High: 0, Medium: 1, Low: 1

## Detailed Issues

1. **Use Built-in Functions for Better Readability**
   - **Location**: lines 2-6, function `calculate_average`
   - **Severity**: Medium
   - **Description**: Manual accumulation loop can be replaced with `sum()` and `len()` for cleaner code
   - **Suggestion**: Replace loop with `return sum(numbers) / len(numbers) if numbers else 0`

2. **Add Input Validation**
   - **Location**: function `calculate_average` parameter
   - **Severity**: Low
   - **Description**: Function assumes `numbers` is iterable, but doesn't validate
   - **Suggestion**: Add type checking: `if not isinstance(numbers, (list, tuple)): raise ValueError("Input must be a list or tuple")`</content>
<parameter name="filePath">C:\Users\rammi\OneDrive\Desktop\git hub\ai_traning\self_reflecting_code_review_agent.md