import io, sys
p = 'src/company_master/orchestrator/task_board.py'
s = io.open(p).read()
old = (
    '                if durum in ("done", "blocked"):\n'
    '                    t["bitis"] = datetime.now().isoformat(timespec="seconds")\n'
    '                _write_json(TASK_BOARD, board)\n'
    '                _md_yaz(board)\n'
)
new = (
    '                if durum in ("done", "blocked"):\n'
    '                    t["bitis"] = datetime.now().isoformat(timespec="seconds")\n'
    '                    # ORCH-05: done/blocked oldugunda bu göreve ait tüm kilitleri otomatik birak\n'
    '                    locks = _read_json(FILE_LOCKS)\n'
    '                    kalan = {d: l for d, l in locks.items() if l.get("task_id") != task_id}\n'
    '                    if len(kalan) != len(locks):\n'
    '                        _write_json(FILE_LOCKS, kalan)\n'
    '                _write_json(TASK_BOARD, board)\n'
    '                _md_yaz(board)\n'
)
cnt = s.count(old)
if cnt != 1:
    print(f'FATAL: match={cnt}', file=sys.stderr); sys.exit(1)
io.open(p, 'w').write(s.replace(old, new))
print('task_board.py patched OK')