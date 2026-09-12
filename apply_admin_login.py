#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""web_app.py'ye admin login endpointi ekleyen script."""

from pathlib import Path

WEB_APP = Path(r"C:\Huginn Data Projesi\Huginn Data Insights\web_app.py")

content = WEB_APP.read_text(encoding="utf-8")

# 1. import tomllib ekle
if "import tomllib" not in content:
    content = content.replace(
        "import time\n",
        "import time\nimport tomllib\n",
        1,
    )
    print("[1] import tomllib eklendi.")
else:
    print("[1] import tomllib zaten var, atlandi.")

# 2. @app.get("/api/admin/pending") onune endpoint ekle
NEW_ENDPOINT = '''

@app.get("/api/admin/login")
def api_admin_login(email: str = "", password: str = ""):
    """Admin girişi: email + sifre -> token (24 saat)."""
    if not email or not password:
        raise HTTPException(status_code=400, detail="email ve sifre zorunlu")
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT email, password_hash, role, status FROM users WHERE email = :e"),
            {"e": email},
        ).mappings().first()
    if row:
        if row["status"] != "onayli" or row["role"] != "admin":
            raise HTTPException(status_code=403, detail="admin yetkisi gerekli")
        if not _verify_password(password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="gecersiz sifre")
        return {"token": _user_token(row["email"])}
    # dev destegi: .streamlit/secrets.toml admin sifresi
    try:
        secrets_path = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"
        if secrets_path.exists():
            with secrets_path.open("rb") as f:
                secrets = tomllib.load(f)
            admin_pw = secrets.get("admin_password", "")
            if admin_pw and email == "admin@huginn.local" and admin_pw == password:
                return {"token": _user_token(email)}
    except Exception:
        pass
    raise HTTPException(status_code=401, detail="gecersiz email veya sifre")

'''

if "def api_admin_login" not in content:
    marker = '@app.get("/api/admin/pending")'
    idx = content.index(marker)
    content = content[:idx] + NEW_ENDPOINT + content[idx:]
    print("[2] admin login endpointi eklendi.")
else:
    print("[2] api_admin_login zaten var, atlandi.")

WEB_APP.write_text(content, encoding="utf-8")
print("[3] Dosya kaydedildi.")
