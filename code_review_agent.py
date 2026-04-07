#!/usr/bin/env python3
"""
Self-Reflecting Code Review Agent
Implements the framework described in self_reflecting_code_review_agent.md
"""

import ast
import sys
import os
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

@dataclass
class Issue:
    title: str
    location: str
    severity: Severity
    description: str
    suggestion: str

@dataclass
class CodeReviewResult:
    total_issues: int
    issues_by_severity: Dict[str, int]
    detailed_issues: List[Issue]

class ASTAnalyzer:
    """Analyzes Python code using Abstract Syntax Tree"""

    def analyze(self, code: str) -> Dict[str, Any]:
        """Perform AST-based analysis of the code"""
        try:
            tree = ast.parse(code)
            issues = []

            # Analyze function complexity
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.body) > 20:
                        issues.append({
                            'type': 'complexity',
                            'message': f"Function '{node.name}' has {len(node.body)} statements (consider breaking down)",
                            'line': node.lineno,
                            'severity': Severity.MEDIUM
                        })

            # Check for potential issues
            issues.extend(self._check_imports(tree))
            issues.extend(self._check_variables(tree))

            return {
                'syntax_valid': True,
                'ast_issues': issues
            }

        except SyntaxError as e:
            return {
                'syntax_valid': False,
                'ast_issues': [{
                    'type': 'syntax_error',
                    'message': f"Syntax error: {e.msg}",
                    'line': e.lineno,
                    'severity': Severity.HIGH
                }]
            }

    def _check_imports(self, tree: ast.AST) -> List[Dict]:
        """Check import statements"""
        issues = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                else:
                    module = node.module or ''
                    imports.extend(f"{module}.{alias.name}" if module else alias.name for alias in node.names)

        # Check for unused imports (simplified - would need symbol table for full analysis)
        # This is a basic check
        return issues

    def _check_variables(self, tree: ast.AST) -> List[Dict]:
        """Check variable usage patterns"""
        issues = []

        # This is a simplified check - full analysis would require symbol table
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                # Check for potential undefined variables
                pass

        return issues

class SelfReflectingReviewer:
    """Simulates the self-reflecting review process using structured reasoning"""

    def __init__(self):
        self.ast_analyzer = ASTAnalyzer()

    def review_code(self, code: str) -> CodeReviewResult:
        """Perform the complete review process"""
        print("🔍 Analyzing code with AST...")
        ast_results = self.ast_analyzer.analyze(code)

        print("📝 Performing initial review...")
        initial_issues = self._initial_review(code, ast_results)

        print("🤔 Self-reflecting on initial review...")
        refined_issues = self._self_reflect_and_refine(code, initial_issues, ast_results)

        print("✅ Generating final review...")
        return self._format_final_review(refined_issues)

    def _initial_review(self, code: str, ast_results: Dict) -> List[Dict]:
        """Stage 1: Initial review - identify potential issues"""
        issues = []

        # Add AST-based issues
        for issue in ast_results['ast_issues']:
            issues.append({
                'title': self._categorize_issue(issue),
                'location': f"line {issue.get('line', 'unknown')}",
                'severity': issue['severity'],
                'description': issue['message'],
                'confidence': self._assess_confidence(issue)
            })

        # Add code-style issues (simplified)
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 88:
                issues.append({
                    'title': 'Line too long',
                    'location': f"line {i}",
                    'severity': Severity.LOW,
                    'description': f"Line exceeds 88 characters ({len(line)} chars)",
                    'confidence': 0.9
                })

            # Check for print statements (could indicate debug code)
            if 'print(' in line and not line.strip().startswith('#'):
                issues.append({
                    'title': 'Print statement found',
                    'location': f"line {i}",
                    'severity': Severity.LOW,
                    'description': "Print statement may be debug code left in production",
                    'confidence': 0.7
                })

        return issues

    def _self_reflect_and_refine(self, code: str, initial_issues: List[Dict], ast_results: Dict) -> List[Dict]:
        """Stage 2-3: Self-reflection and refinement"""
        refined_issues = []

        for issue in initial_issues:
            # Self-reflection: assess if issue is real and actionable
            if self._validate_issue(issue, code, ast_results):
                # Refine the issue description and suggestion
                refined_issue = self._refine_issue(issue, code)
                refined_issues.append(refined_issue)

        return refined_issues

    def _validate_issue(self, issue: Dict, code: str, ast_results: Dict) -> bool:
        """Validate if an issue is real and not a false positive"""
        confidence = issue.get('confidence', 0.5)

        # Remove low-confidence issues
        if confidence < 0.6:
            return False

        # Additional validation logic could go here
        return True

    def _refine_issue(self, issue: Dict, code: str) -> Dict:
        """Refine issue description and add specific suggestions"""
        refined = issue.copy()

        # Add more specific suggestions based on issue type
        if 'complexity' in issue['title'].lower():
            refined['suggestion'] = "Consider breaking this function into smaller, more focused functions"
        elif 'line too long' in issue['title'].lower():
            refined['suggestion'] = "Break the line into multiple lines or use parentheses for line continuation"
        elif 'print' in issue['title'].lower():
            refined['suggestion'] = "Replace print statements with proper logging using the logging module"
        else:
            refined['suggestion'] = "Review and refactor this code section for better practices"

        return refined

    def _categorize_issue(self, issue: Dict) -> str:
        """Categorize the issue type"""
        issue_type = issue.get('type', 'general')
        if issue_type == 'syntax_error':
            return 'Syntax Error'
        elif issue_type == 'complexity':
            return 'Code Complexity'
        else:
            return 'Code Quality Issue'

    def _assess_confidence(self, issue: Dict) -> float:
        """Assess confidence level for the issue"""
        if issue['type'] == 'syntax_error':
            return 1.0
        elif issue['type'] == 'complexity':
            return 0.8
        else:
            return 0.7

    def _format_final_review(self, issues: List[Dict]) -> CodeReviewResult:
        """Format the final review results"""
        severity_counts = {'High': 0, 'Medium': 0, 'Low': 0}

        detailed_issues = []
        for issue in issues:
            severity_str = issue['severity'].value
            severity_counts[severity_str] += 1

            detailed_issues.append(Issue(
                title=issue['title'],
                location=issue['location'],
                severity=issue['severity'],
                description=issue['description'],
                suggestion=issue['suggestion']
            ))

        return CodeReviewResult(
            total_issues=len(issues),
            issues_by_severity=severity_counts,
            detailed_issues=detailed_issues
        )

def print_review_result(result: CodeReviewResult):
    """Print the formatted review result"""
    print("\n" + "="*60)
    print("🔍 CODE REVIEW SUMMARY")
    print("="*60)
    print(f"Total issues found: {result.total_issues}")
    print(f"Issues by severity: High: {result.issues_by_severity['High']}, "
          f"Medium: {result.issues_by_severity['Medium']}, "
          f"Low: {result.issues_by_severity['Low']}")
    print()

    if result.detailed_issues:
        print("📋 DETAILED ISSUES")
        print("-"*60)
        for i, issue in enumerate(result.detailed_issues, 1):
            print(f"{i}. **{issue.title}**")
            print(f"   - **Location**: {issue.location}")
            print(f"   - **Severity**: {issue.severity.value}")
            print(f"   - **Description**: {issue.description}")
            print(f"   - **Suggestion**: {issue.suggestion}")
            print()
    else:
        print("✅ No issues found! Code looks good.")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python code_review_agent.py <python_file>")
        print("Example: python code_review_agent.py my_script.py")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        print(f"📖 Reading file: {file_path}")
        print(f"📏 Code length: {len(code)} characters")

        reviewer = SelfReflectingReviewer()
        result = reviewer.review_code(code)

        print_review_result(result)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()