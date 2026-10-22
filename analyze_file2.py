import ast
import os

filepath = "c:/Huginn Data Projesi/Huginn Data Insights/src/company_master/etl/gece_besleme.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

print("File length:", len(content))
print("First 200 chars:", repr(content[:200]))
print("Last 200 chars:", repr(content[-200:]))

try:
    tree = ast.parse(content)
    print("AST parsed successfully")
    # Find all function definitions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            print("Function:", node.name, "Line:", node.lineno)
        if isinstance(node, ast.ClassDef):
            print("Class:", node.name, "Line:", node.lineno)
except SyntaxError as e:
    print("Syntax error:", e)
except Exception as e:
    print("Error:", e)