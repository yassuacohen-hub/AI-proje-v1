# -*- coding: utf-8 -*-
"""AST tabanlı `st.metric` tespiti — UI-CHART-01 uyumlulugu.

Admin sekmelerinde `st.metric` kullanımı yerine `web_dashboard.charts.kpi_karti`
kullanılması gerekir. Bu script hedef dosyalardaki `st.metric` cagrilari tespit eder.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
# Hedef dosyalar: ADMIN-KPI-KART-02 kapsamindaki dosyalar
TARGET_FILES = [
    ROOT / "web_dashboard" / "tabs" / "webhook_monitor.py",
    ROOT / "web_dashboard" / "tabs" / "tenant_health_dashboard.py",
]


class StMetricVisitor(ast.NodeVisitor):
    """AST visitor to find `st.metric` calls."""

    def __init__(self):
        self.st_metric_calls: list[dict[str, Any]] = []

    def visit_Call(self, node: ast.Call):
        # Check if this is a `st.metric` call
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "st"
            and node.func.attr == "metric"
        ):
            self.st_metric_calls.append({
                "lineno": node.lineno,
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "type": "st_metric",
                "message": "`st.metric` cagrisi tespit edildi — `kpi_karti` kullanılmalı",
            })

        self.generic_visit(node)


def find_st_metric_in_file(file_path: Path) -> list[dict[str, Any]]:
    """Find `st.metric` calls in a Python file."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
        visitor = StMetricVisitor()
        visitor.visit(tree)
        return visitor.st_metric_calls
    except SyntaxError:
        return [{"error": "Syntax error", "file": str(file_path)}]
    except Exception as exc:
        return [{"error": str(exc), "file": str(file_path)}]


def find_all_st_metric() -> dict[str, list[dict[str, Any]]]:
    """Find `st.metric` calls in all target files."""
    results = {}
    for target_file in TARGET_FILES:
        if not target_file.exists():
            continue
        results_list = find_st_metric_in_file(target_file)
        if results_list:
            results[str(target_file.relative_to(ROOT))] = results_list
    return results


def main() -> int:
    """Main entry point for CLI."""
    results = find_all_st_metric()

    total_count = sum(len(v) for v in results.values())
    if total_count == 0:
        print("✅ `st.metric` cagrisi bulunamadı — tum dosyalar `kpi_karti` kullaniyor.")
        return 0

    print(f"❌ {total_count} `st.metric` cagrisi bulundu (UI-CHART-01 ihlali):\n")
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
