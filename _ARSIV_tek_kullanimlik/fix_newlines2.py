from pathlib import Path

files = [
    "scripts/db_migrate.py",
    "tests/test_db_migration.py",
    "scripts/db_migrate_prod.sh",
    "monitoring/alertmanager/migration_rules.yml"
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