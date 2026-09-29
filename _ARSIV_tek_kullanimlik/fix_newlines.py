from pathlib import Path

files = [
    "scripts/config_test.py",
    "scripts/rotate_secrets.py",
    "tests/test_secrets_rotation.py"
]

for f in files:
    path = Path(f)
    content = path.read_text(encoding="utf-8")
    if not content.endswith("\n"):
        content += "\n"
        path.write_text(content, encoding="utf-8")
        print(f"Fixed: {f}")
    else:
        print(f"Already OK: {f}")