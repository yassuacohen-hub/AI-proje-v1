with open('web_app.py', 'rb') as f:
    content_bytes = f.read()

# Exact byte pattern to find
old_bytes = (
    b'except Exception as exc:\n'
    b'        print(f"[DATA-LOG-01] search_event kayit hatasi: {exc}")\n'
    b'\n'
    b'\n'
    b'# \xe2\x94\x82\xe2\x94\x82 X04: \xc3\x9cyelik yard\xc4\xb1mc\xc4\xb1lar\xc4\xb1 '
    b'(\xc5\x9fifre s\xc4\xb1f\xc4\xb1rlama, e-posta do\xc4\x9frulama, Telegram) '
    b'\xe2\x94\x82\xe2\x94\x82\xe2\x94\x82\xe2\x94\x82\n'
    b'import secrets\n'
)

# New content as bytes
new_bytes = (
    b'except Exception as exc:\n'
    b'        print(f"[DATA-LOG-01] search_event kayit hatasi: {exc}")\n'
    b'\n'
    b'\n'
    b'def aktivite_yaz(\n'
    b'    user_id: str,\n'
    b'    olay_tipi: str,\n'
    b'    detay: dict | None = None,\n'
    b'    basarili: bool = True,\n'
    b'    request: Request | None = None,\n'
    b') -> None:\n'
    b'    """API-ADMIN-AKTIVITE-YAZ-14: user_activity_log tablosuna kayit.\n'
    b'\n'
    b'    Hata istek dusurmez (best-effort). Olay tipleri: \'giris\', \'arama\', \'ai_kullanim\'.\n'
    b'    """\n'
    b'    try:\n'
    b'        engine = get_engine()\n'
    b'        with engine.connect() as conn:\n'
    b'            ip = ""\n'
    b'            if request and request.client:\n'
    b'                ip = request.client.host\n'
    b'            \n'
    b'            import json\n'
    b'            conn.execute(\n'
    b'                text(\n'
    b'                    "INSERT INTO user_activity_log (user_id, olay_tipi, olay_zamani, detay, "\n'
    b'                    "basarili, ip_adresi, ulke_kodu) "\n'
    b'                    "VALUES (:uid, :tip, CURRENT_TIMESTAMP, :detay, :ok, :ip, :ulke)"\n'
    b'                ),\n'
    b'                {\n'
    b'                    "uid": user_id or "",\n'
    b'                    "tip": olay_tipi,\n'
    b'                    "detay": json.dumps(detay) if detay else None,\n'
    b'                    "ok": basarili,\n'
    b'                    "ip": ip or None,\n'
    b'                    "ulke": None,\n'
    b'                },\n'
    b'            )\n'
    b'            conn.commit()\n'
    b'    except Exception as exc:\n'
    b'        print(f"[API-ADMIN-AKTIVITE-YAZ-14] aktivite kayit hatasi: {exc}")\n'
    b'\n'
    b'\n'
    b'# \xe2\x94\x82\xe2\x94\x82 X04: \xc3\x9cyelik yard\xc4\xb1mc\xc4\xb1lar\xc4\xb1 '
    b'(\xc5\x9fifre s\xc4\xb1f\xc4\xb1rlama, e-posta do\xc4\x9frulama, Telegram) '
    b'\xe2\x94\x82\xe2\x94\x82\xe2\x94\x82\xe2\x94\x82\n'
    b'import secrets\n'
)

if old_bytes in content_bytes:
    new_content = content_bytes.replace(old_bytes, new_bytes)
    with open('web_app.py', 'wb') as f:
        f.write(new_content)
    print('Replaced successfully!')
else:
    print('NOT FOUND - checking...')
    # Find what's different
    idx = content_bytes.find(b'search_event kayit hatasi')
    print(f"Found at {idx}")
    print(content_bytes[idx:idx+150])