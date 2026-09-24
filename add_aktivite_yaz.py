with open('web_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """except Exception as exc:
        print(f"[DATA-LOG-01] search_event kayit hatasi: {exc}")


# â”€â”€ X04: Ãœyelik yardÄ±mcÄ±larÄ± (ÅŸifre sÄ±fÄ±rlama, e-posta doÄŸrulama, Telegram) â”€â”€â”€
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


# â”€â”€ X04: Ãœyelik yardÄ±mcÄ±larÄ± (ÅŸifre sÄ±fÄ±rlama, e-posta doÄŸrulama, Telegram) â”€â”€â”€
import secrets"""

if old in content:
    content = content.replace(old, new)
    with open('web_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Replaced successfully')
else:
    print('NOT FOUND')
    idx = content.find('search_event kayit hatasi')
    if idx >= 0:
        print(f'Found at {idx}: {repr(content[idx:idx+200])}')