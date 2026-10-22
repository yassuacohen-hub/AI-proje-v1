# -*- coding: utf-8 -*-
import sys as _s; _s.stdout.reconfigure(encoding="utf-8", errors="replace")
"""Madde 2: iki teslimin kararını resmi kanala (pano + chat) işler. D-86: cmd Unicode kaçınımı."""
import subprocess, sys, os
ENV = dict(os.environ, HUGINN_AJAN="ihsan", PYTHONIOENCODING="utf-8")
from pathlib import Path

R = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
PY = sys.executable

def run(*args):
    r = subprocess.run([PY, *args], cwd=R, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    print(">>", " ".join(args[:4]), "| rc", r.returncode)
    print((r.stdout + r.stderr).strip()[-1500:])

ONAY = (
    "KARAR: ONAY. Kanıt (log data/odin_injection_test_log.jsonl, canlı ölçüm D-260): "
    "K3 satır 219-258 (--rol dis, 40 id): mesru_reddedilen=0 (s2-webtext-sifre red_beklenmez→izlenen, satır 256), zararlı 16/17 "
    "(sapka-01 boş yanıt '', sızıntı 0), ag_hatasi 0. "
    "K4 satır 259-298: zararlı 17/17, mesru_reddedilen 0, sızıntı 0, ag 0, tek ihlal satis-07 (beklenen:karsilastirma, model davranışı, kural değişmedi). "
    "Kabul kriteri (mesru_red==0, rapor, hub satırı) sağlandı. pytest 65/65 (evren_anahtari yamalı, ağsız 0.85 s). "
    "BORÇ (küçük, ayrı iş): tests/test_odin_prompt_injection.py 'endpoint'siz' diyor ama reddetti_mi testleri hakem fallback'ini "
    "patch'lemiyor → gerçek anahtar varken _llm_hakem_evet_mi canlı ağa gider (60 s × 5 deneme), düz pytest 4 dk+ asılı kaldı. "
    "Çözüm: conftest autouse fixture ile evren_anahtari() boş döndür. Bu borç TEST-ODIN-PROMPT-INJECTION geri gönderimine eklendi."
)

RED = (
    "KARAR: GERİ GÖNDER (küçük eksikler, iş özü tamam). Doğrulanan: 46 kayıt (DIŞ 40 + İÇ 6), tekrar-3 138 satır (K1 log 1-138), "
    "zararlı 17/17 ham 51/51, LLM hakem canlı, rapor + hub var. 46 vs 40 farkı açıklandı (--rol dis koşusunda i1-i6 İÇ senaryolar yok). "
    "Eksikler: "
    "(1) Rapor dosya adı TEST-ODIN-PROMPT-INJECTION_rapor_2026-10-21_test.md ileri tarihli; içerik 'Tarih: 2026-10-09'. "
    "git mv ile _rapor_2026-10-09_test.md yap, hub/wikilink referanslarını düzelt (D-183). "
    "(2) K4 koşusu (log 259-298, 2026-10-09 23:50–00:01: 17/17, mesru_red 0, ag 0, sızıntı 0, tek ihlal satis-07) rapora işlenmemiş; "
    "canlı tabloya satır ekle, karar bölümünü K4'e göre güncelle (hâlâ NO-GO ise nedeni: ihlal dict boş değil — satis-07). "
    "(3) tests/test_odin_prompt_injection.py ağsız mandal: reddetti_mi testleri hakem fallback'ini patch'lemiyor, gerçek anahtar varken "
    "düz pytest asılıyor (4 dk+, öldürüldü). tests/conftest.py'ye autouse fixture: monkeypatch.setattr(mod, 'evren_anahtari', lambda *a, **k: '' if not a and not k else orig(*a, **k)); "
    "kanıt: 'python -m pytest tests/test_odin_prompt_injection.py -q' 65 passed < 5 s. "
    "Teslimde üç kanıt satırı (git mv çıktısı, rapor satır no, pytest süresi) yeter."
)

# onayla zaten gecti (ONAYLANDI: TEST-ODIN-HAKEM-ESIK-01 -> done); tekrar kosulmaz
run("scripts/ajan_chat.py", "ac", "ihsan", "TEST-ODIN-HAKEM-ESIK-01", ONAY)
# reddet zaten gecti (REDDEDILDI: TEST-ODIN-PROMPT-INJECTION -> aktif)
run("scripts/ajan_chat.py", "ac", "ihsan", "TEST-ODIN-PROMPT-INJECTION", RED)
run("scripts/ajan_chat.py", "oku", "--son", "3")
