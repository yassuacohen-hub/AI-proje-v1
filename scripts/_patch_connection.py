"""Geçici: connection.py dotenv fallback yaması."""
import re
from pathlib import Path

p = Path("AI proje v1/src/company_master/db/connection.py")
s = p.read_text(encoding="utf-8")

old_block = re.compile(
    r"try:\s+from dotenv import load_dotenv\s+"
    r"project_root = Path\(__file__\)\.resolve\(\)\.parents\[3\]\s+"
    r"load_dotenv\(project_root / \".env\"\)\s+"
    r"except ImportError:\s+pass",
    re.DOTALL,
)

new_block = '''def _load_env() -> None:
    """.env dosyasını yükler (python-dotenv yoksa kendi parser'ı)."""
    project_root = Path(__file__).resolve().parents[3]
    env_path = project_root / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


try:
    from dotenv import load_dotenv
    project_root = Path(__file__).resolve().parents[3]
    load_dotenv(project_root / ".env")
except ImportError:
    _load_env()

_load_env()'''

s2, n = old_block.subn(new_block, s)
assert n == 1, f"blok bulunamadı (n={n})"
p.write_text(s2, encoding="utf-8")
print("OK: connection.py yamalandı")