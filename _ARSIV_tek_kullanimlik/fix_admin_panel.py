from pathlib import Path

path = Path("web_dashboard/tabs/admin_panel.py")
content = path.read_text(encoding="utf-8")
lines = content.splitlines()
fixed_lines = [line.rstrip() for line in lines]
new_content = "\n".join(fixed_lines) + "\n"
path.write_text(new_content, encoding="utf-8")
print("Fixed trailing whitespace in admin_panel.py")