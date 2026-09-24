with open('web_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "search_event kayit hatasi"
target_line_idx = None
for i, line in enumerate(lines):
    if 'search_event kayit hatasi' in line:
        target_line_idx = i
        break

print(f"Found at line {target_line_idx}: {lines[target_line_idx].strip()}")

# Find the next line that starts with "#" (section header) after some blank lines
insert_idx = None
for i in range(target_line_idx + 1, len(lines)):
    if lines[i].strip().startswith('#') and 'X04' in lines[i]:
        insert_idx = i
        break

print(f"Insert before line {insert_idx}: {lines[insert_idx].strip()}")

# Build new function lines
new_lines = [
    '\n',
    '\n',
    'def aktivite_yaz(\n',
    '    user_id: str,\n',
    '    olay_tipi: str,\n',
    '    detay: dict | None = None,\n',
    '    basarili: bool = True,\n',
    '    request: Request | None = None,\n',
    ') -> None:\n',
    '    """API-ADMIN-AKTIVITE-YAZ-14: user_activity_log tablosuna kayit.\n',
    '\n',
    '    Hata istek dusurmez (best-effort). Olay tipleri: \'giris\', \'arama\', \'ai_kullanim\'.\n',
    '    """\n',
    '    try:\n',
    '        engine = get_engine()\n',
    '        with engine.connect() as conn:\n',
    '            ip = ""\n',
    '            if request and request.client:\n',
    '                ip = request.client.host\n',
    '            \n',
    '            import json\n',
    '            conn.execute(\n',
    '                text(\n',
    '                    "INSERT INTO user_activity_log (user_id, olay_tipi, olay_zamani, detay, "\n',
    '                    "basarili, ip_adresi, ulke_kodu) "\n',
    '                    "VALUES (:uid, :tip, CURRENT_TIMESTAMP, :detay, :ok, :ip, :ulke)"\n',
    '                ),\n',
    '                {\n',
    '                    "uid": user_id or "",\n',
    '                    "tip": olay_tipi,\n',
    '                    "detay": json.dumps(detay) if detay else None,\n',
    '                    "ok": basarili,\n',
    '                    "ip": ip or None,\n',
    '                    "ulke": None,\n',
    '                },\n',
    '            )\n',
    '            conn.commit()\n',
    '    except Exception as exc:\n',
    '        print(f"[API-ADMIN-AKTIVITE-YAZ-14] aktivite kayit hatasi: {exc}")\n',
    '\n',
    '\n',
]

# Insert the new lines
for i, new_line in enumerate(new_lines):
    lines.insert(insert_idx + i, new_line)

# Write back
with open('web_app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Inserted successfully!')