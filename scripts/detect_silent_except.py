# -*- coding: utf-8 -*-
"""AST tabanlı sessiz `except Exception: pass` tespiti.

Admin sekmelerindeki sessiz exception yakalama kalıplarını tespit eder.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = [
    ROOT / "web_dashboard" / "tabs",
]


class SilentExceptVisitor(ast.NodeVisitor):
    """AST visitor to find silent `except Exception: pass` patterns."""

    def __init__(self):
        self.silent_excepts: list[dict[str, Any]] = []

    def visit_Try(self, node: ast.Try):
        for handler in node.handlers:
            # Check if handler catches Exception (or bare except)
            is_exception_handler = (
                handler.type is None  # bare except:
                or (
                    isinstance(handler.type, ast.Name)
                    and handler.type.id == "Exception"
                )
                or (
                    isinstance(handler.type, ast.Tuple)
                    and any(
                        isinstance(elt, ast.Name) and elt.id == "Exception"
                        for elt in handler.type.elts
                    )
                )
            )

            if is_exception_handler:
                # Check if body is just `pass` or only contains pass statements
                if self._is_silent_pass(handler.body):
                    self.silent_excepts.append({
                        "lineno": handler.lineno,
                        "end_lineno": getattr(handler, "end_lineno", handler.lineno),
                        "type": "silent_except_pass",
                        "message": "Sessiz `except Exception: pass` tespit edildi",
                    })

        self.generic_visit(node)

    def _is_silent_pass(self, body: list[ast.stmt]) -> bool:
        """Check if body only contains pass statements."""
        if not body:
            return False
        return all(
            isinstance(stmt, ast.Pass)
            or (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is None)
            for stmt in body
        )


def find_silent_excepts_in_file(file_path: Path) -> list[dict[str, Any]]:
    """Find silent except: pass patterns in a Python file."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
        visitor = SilentExceptVisitor()
        visitor.visit(tree)
        return visitor.silent_excepts
    except SyntaxError:
        return [{"error": "Syntax error", "file": str(file_path)}]
    except Exception as exc:
        return [{"error": str(exc), "file": str(file_path)}]


def find_all_silent_excepts() -> dict[str, list[dict[str, Any]]]:
    """Find silent except patterns in all target directories."""
    results = {}
    for target_dir in TARGET_DIRS:
        if not target_dir.exists():
            continue
        for py_file in target_dir.rglob("*.py"):
            # Skip test files and error handling module
            if "test_" in py_file.name or "admin_error_handling" in py_file.name:
                continue
            results_list = find_silent_excepts_in_file(py_file)
            if results_list:
                results[str(py_file.relative_to(ROOT))] = results_list
    return results


def main() -> int:
    """Main entry point for CLI."""
    results = find_all_silent_excepts()

    total_count = sum(len(v) for v in results.values())
    if total_count == 0:
        print("✅ Sessiz `except Exception: pass` kalıbı bulunamadı.")
        return 0

    print(f"❌ {total_count} sessiz `except Exception: pass` kalıbı bulundu:\n")
    for file_path, issues in results.items():
        print(f"📄 {file_path}")
        for issue in issues:
            if "error" in issue:
                print(f"  ⚠️  {issue['error']}")
            else:
                print(f"  Line {issue['lineno']}: {issue['message']}")
        print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
