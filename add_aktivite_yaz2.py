with open('web_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Exact pattern to find
old = """except Exception as exc:
        print(f"[DATA-LOG-01] search_event kayit hatasi: {exc}")


# ── X04: Üyelik yardımcıları (şifre sıfırlama, e-posta doğrulama, Telegram) ───
import secrets"""

new = """except Exception as exc:
        print(f"[DATA-LOG-01] search_event kayit hatasi: {exc}")


def aktivite_yaz(
    user_id: str,
    olay_tipi: str,
    detay: dict | None = None,
    basarili: bool = True,
    request: Request | None = None,
) -> None:
    \"\"\"API-ADMIN-AKTIVITE-YAZ-14: user_activity_log tablosuna kayit.
    
    Hata istek dusurmez (best-effort). Olay tipleri: 'giris', 'arama', 'ai_kullanim'.
    \"\"\"
    try:
        engine = get_engine()
        with engine.connect() as conn:
            ip = ""
            if request and request.client:
                ip = request.client.host
            
            import json
            conn.execute(
                text(
                    "INSERT INTO user_activity_log (user_id, olay_tipi, olay_zamani, detay, "
                    "basarili, ip_adresi, ulke_kodu) "
                    "VALUES (:uid, :tip, CURRENT_TIMESTAMP, :detay, :ok, :ip, :ulke)"
                ),
                {
                    "uid": user_id or "",
                    "tip": olay_tipi,
                    "detay": json.dumps(detay) if detay else None,
                    "ok": basarili,
                    "ip": ip or None,
                    "ulke": None,
                },
            )
            conn.commit()
    except Exception as exc:
        print(f"[API-ADMIN-AKTIVITE-YAZ-14] aktivite kayit hatasi: {exc}")


# ── X04: Üyelik yardımcıları (şifre sıfırlama, e-posta doğrulama, Telegram) ───
import secrets"""

if old in content:
    content = content.replace(old, new)
    with open('web_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Replaced successfully')
else:
    print('NOT FOUND - trying with box chars')
    old2 = old.replace('─', '\u2500')
    if old2 in content:
        content = content.replace(old2, new)
        with open('web_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print('Replaced with box chars')
    else:
        print('Still not found')
        # Show exact bytes around the area
        idx = content.find('search_event kayit hatasi')
        print(repr(content[idx:idx+300]))