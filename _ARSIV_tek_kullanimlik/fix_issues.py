from pathlib import Path

files = [
    "tests/test_admin_pano_board_view.py",
]

for f in files:
    path = Path(f)
    content = path.read_text(encoding="utf-8")
    if not content.endswith("\n"):
        content += "\n"
        path.write_text(content, encoding="utf-8")
        print(f"Fixed newline: {f}")
    else:
        print(f"Already OK newline: {f}")

# Fix trailing whitespace in admin_panel.py
path = Path("web_dashboard/tabs/admin_panel.py")
content = path.read_text(encoding="utf-8")
lines = content.splitlines()
fixed_lines = [line.rstrip() for line in lines]
new_content = "\n".join(fixed_lines) + "\n"
path.write_text(new_content, encoding="utf-8")
print("Fixed trailing whitespace: admin_panel.py")