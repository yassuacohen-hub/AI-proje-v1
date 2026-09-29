from pathlib import Path

files = [
    "src/company_master/admin_audit.py",
    "src/company_master/churn.py",
    "web_dashboard/tabs/musteri_yonetimi.py",
    "tests/test_admin_audit.py",
    "tests/test_churn.py",
    "tests/test_api_aktivite.py",
    "tests/test_ui_upsell.py",
    "scripts/db_migrate.py",
]

for f in files:
    path = Path(f)
    content = path.read_text(encoding="utf-8")
    # Fix trailing whitespace
    lines = content.splitlines()
    fixed_lines = [line.rstrip() for line in lines]
    # Fix missing newline at end
    new_content = "\n".join(fixed_lines) + "\n"
    path.write_text(new_content, encoding="utf-8")
    print(f"Fixed: {f}")

print("Done!")