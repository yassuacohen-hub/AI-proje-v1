"""Orkestrator - Merkezi Gorev Panosu ve dosya-lock takibi.

Eski sistemde "herkes herkesin ne yaptigini surekli bir listede takip ediyordu"
mekanizmasinin yeniden kurulumu:

- data/orchestrator/task_board.json   -> gorevler (atama, durum, sahiplik)
- data/orchestrator/file_locks.json   -> dosya sahiplik lock'lari (cakisma onleme)
- data/orchestrator/state.json        -> orkestrator canli durumu

Ajanlar (ic + dis) panoya gorev atar/ceker; iki ajan ayni dosyayi ayni anda
sahiplenemez.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
STATE_DIR = ROOT / "data" / "orchestrator"

TASK_BOARD = STATE_DIR / "task_board.json"
FILE_LOCKS = STATE_DIR / "file_locks.json"
STATE_JSON = STATE_DIR / "state.json"
TASK_MD = STATE_DIR / "gorev_panosu.md"

GOREV_DURUMLARI = ("plan", "aktif", "review", "done", "blocked")

# S-05: Pano kaydinda BULUNMASI ZORUNLU alanlar ve eksikse kullanilacak
# varsayilanlar. Tek bozuk kayit yuzunden TUM ajanlarin pano yazimi
# cokmemeli (bkz. WIKI-01 / KeyError 'oncelik', docs/ROO_ELESTIRI_NOTLARI.md).
ZORUNLU_ALANLAR: dict[str, Any] = {
    "task_id": "",
    "baslik": "-",
    "sahip": "-",
    "oncelik": "P2",
    "durum": "plan",
    "dosyalar": [],
}

# ORCH-03: Pano degistikce AGENT_SYNC otomatik tazelensin.
# Testlerde conftest.py bu bayragi False yapar (gercek dosyaya yazma engellenir).
AUTO_SYNC = True

# AGENT_SYNC konumlari (modul seviyesi: testler monkeypatch edebilir)
AGENT_SYNC_MD = ROOT / "AGENT_SYNC.md"
AGENT_SYNC_MD_KOPYA = STATE_DIR / "AGENT_SYNC.md"


def _ensure() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not TASK_BOARD.exists():
        TASK_BOARD.write_text("[]", encoding="utf-8")
    if not FILE_LOCKS.exists():
        FILE_LOCKS.write_text("{}", encoding="utf-8")
    if not STATE_JSON.exists():
        STATE_JSON.write_text("{}", encoding="utf-8")


def gorev_normalize(task: dict) -> dict:
    """S-05: Tek gorev kaydini zorunlu alan semasina tamamlar.

    Eksik alanlari varsayilanla doldurur, `None`/bos degerleri varsayilana
    cevirir. Kaydi YERINDE degistirir ve ayni sozlugu dondurur.
    """
    for alan, varsayilan in ZORUNLU_ALANLAR.items():
        if alan == "task_id":
            continue  # task_id uydurulamaz; cagiran taraf dogrulamali
        if task.get(alan) in (None, ""):
            task[alan] = list(varsayilan) if isinstance(varsayilan, list) else varsayilan
    # FIX-ID-01: id eksikse task_id alias olarak doldur
    if task.get("id") in (None, ""):
        task["id"] = task.get("task_id", "")
    if not isinstance(task.get("dosyalar"), list):
        task["dosyalar"] = []
    return task


def pano_normalize(board: list[dict]) -> tuple[list[dict], list[str]]:
    """S-05: Tum panoyu semaya gore onarir.

    Donen ikinci deger: onarilan gorev id'leri (denetim izi icin).
    """
    onarilan: list[str] = []
    for t in board:
        eksik = [a for a in ZORUNLU_ALANLAR if a != "task_id" and t.get(a) in (None, "")]
        if eksik or not isinstance(t.get("dosyalar"), list):
            gorev_normalize(t)
            onarilan.append(str(t.get("task_id", "?")))
    return board, onarilan


def sema_dogrula(task: dict) -> None:
    """S-05: Panoya YENI eklenecek kayit icin zorunlu alan dogrulamasi.

    Eksik/bos zorunlu alan varsa ValueError firlatir; boylece bozuk kayit
    panoya hic girmez (savunma degil, onleme).
    """
    eksik = [a for a in ZORUNLU_ALANLAR if task.get(a) in (None, "")]
    if eksik:
        raise ValueError(
            "Gorev semasi eksik alan iceriyor: " + ", ".join(sorted(eksik))
        )
    if task["durum"] not in GOREV_DURUMLARI:
        raise ValueError(f"Gecersiz durum: {task['durum']}")
    if not isinstance(task.get("dosyalar"), list):
        raise ValueError("'dosyalar' alani liste olmali")


def _read_json(path: Path) -> Any:
    _ensure()
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, data: Any) -> None:
    _ensure()
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2))


def atomic_write_text(path: Path, text: str) -> None:
    """Atomik metin yazma: once gizli .tmp dosyasina yaz, sonra os.replace.

    ORCH-01 devami: paralel ajanlar ayni dosyaya ayni anda yazarken yarim
    dosya kalmamasi icin (gozlemlenen arizalar: task_board.json'un 6 bayta
    dusmesi ve AGENT_SYNC.md basliginin ortadan bolunmesi).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f".{path.name}.{os.getpid()}.tmp"
    try:
        tmp.write_text(text, encoding="utf-8")
        # Windows'ta os.replace hedef dosya baska surec tarafindan aciksa
        # PermissionError verir (gozlemlendi: test/uretim ortaminda ariza).
        # Kisa araliklarla 3 deneme: yarisci yazim yerine gecici kilit.
        son_hata: Exception | None = None
        for deneme in range(3):
            try:
                os.replace(tmp, path)
                break
            except PermissionError as exc:
                son_hata = exc
                time.sleep(0.1 * (deneme + 1))
        else:
            raise son_hata  # 3 deneme de basarisiz: gorunur hata (sessiz kayip yasak)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def _sync_tetikle() -> None:
    """ORCH-03: Pano/lock degisikliginden sonra AGENT_SYNC'i sessizce tazele.

    - AUTO_SYNC=False ise hicbir sey yapmaz (test izolasyonu).
    - Windows'ta baska bir surec dosyayi okurken os.replace PermissionError
      verebilir -> kisa araliklarla 3 deneme yapilir.
    - Tum denemeler basarisizsa pano islemi BLOKLANMAZ; sadece stderr'a
      uyari yazilir (sessiz kayip yerine gorunur hata).
    """
    if not AUTO_SYNC:
        return
    son_hata: Exception | None = None
    for deneme in range(3):
        try:
            agent_sync_yaz()
            return
        except Exception as exc:  # noqa: BLE001 - pano islemi bloklanmamali
            son_hata = exc
            time.sleep(0.2 * (deneme + 1))
    print(
        f"[task_board] AGENT_SYNC otomatik tazeleme basarisiz "
        f"(pano etkilenmedi): {son_hata}",
        file=sys.stderr,
    )


def _pano_kilit() -> None:
    """Kontrolör-yazım kilit: pano.lock (O_EXCL). 30sn'den eski kilit bayat sayilir."""
    kilit = STATE_DIR / "pano.lock"
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    for _ in range(60):  # ~6 sn bekler
        try:
            fd = os.open(kilit, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("utf-8"))
            os.close(fd)
            return
        except FileExistsError:
            try:
                if time.time() - kilit.stat().st_mtime > 30:  # bayat kilit
                    kilit.unlink(missing_ok=True)
                    continue
            except OSError:
                pass
            time.sleep(0.1)
    raise TimeoutError("pano.lock beklenirken zaman asimi (baska surec yaziyor olabilir)")


def _pano_birak() -> None:
    (STATE_DIR / "pano.lock").unlink(missing_ok=True)


def _pano_korumali(fn):
    """Gorev panosu okuma-yazma tum islemlerini tek surecte kilitleyen dekorator.

    Gozlemlenen ariza: iki surec ayni anda gorev_guncelle yapinca, birinin
    ekledigi alan (orn. blokaj) digerinin bayat yedegiyle silinebiliyordu.
    Bu dekorator gorev_ekle/gorev_guncelle gibi tilde-aktif islemleri
    pano.lock altina alir (read-modify-write atomiklesir).
    """
    from functools import wraps

    @wraps(fn)
    def sarmal(*args, **kwargs):
        _pano_kilit()
        try:
            return fn(*args, **kwargs)
        finally:
            _pano_birak()

    return sarmal


# ---- Gorev Panosu ----
@_pano_korumali
def gorev_ekle(
    task_id: str,
    baslik: str,
    sahip: str,          # ic ajan id veya harici ajan id
    oncelik: str = "P1",
    baslangic: str | None = None,
    bitis: str | None = None,
    dosyalar: list[str] | None = None,
    source: str | None = None,
    from_agent: str | None = None,
) -> dict:
    """Panoya gorev ekle. dosyalar -> file-lock sahipligi de alir.

    source: "ic" veya "harici" (ad-hoc agent)
    """
    _ensure()
    board = _read_json(TASK_BOARD)
    if any(t.get("task_id") == task_id for t in board):
        raise ValueError(f"Gorev zaten var: {task_id}")
    task = {
        "task_id": task_id,
        "id": task_id,  # FIX-ID-01: task_id kanonik, id alias (consumer uyumlulugu)
        "baslik": baslik,
        "sahip": sahip,
        "oncelik": oncelik,
        "durum": "plan",
        "baslangic": baslangic or datetime.now().isoformat(timespec="seconds"),
        "bitis": bitis,
        "dosyalar": dosyalar or [],
        "not": "",
        "source": source or "ic",
        "from_agent": from_agent,
    }
    # S-05: Bozuk kayit panoya hic girmesin (onleme).
    sema_dogrula(task)
    # Atomik: once tum lock'lar denenir; hata olursa gorev eklenmez.
    if dosyalar:
        for d in dosyalar:
            _lock_alan(sahip, d, task_id)
    board.append(task)
    _write_json(TASK_BOARD, board)
    _md_yaz(board)
    agent_sync_yaz()
    return task


# ---- K7: Retry Context Decay ----
MAX_ATTEMPTS = 3


def retry_istatistikleri(task_id: str) -> dict:
    """Gorev icin retry istatistikleri (context decay icin)."""
    gorev = gorev_getir(task_id)
    if not gorev:
        return {"attempts": 0, "backoff_sn": 0, "context_mode": "full"}
    attempts = gorev.get("attempts", 0)
    # Exponential context decay: her retry'de context %50 azalir
    if attempts <= 1:
        mode = "full"       # ~3000 token
    elif attempts == 2:
        mode = "hatali"     # ~1000 token (sadece hata + dosyanin degisen kisimlari)
    else:
        mode = "handoff"    # ~500 token (sadece handoff)
    backoff_sn = 2 ** (attempts - 1) * 60  # 60s, 120s, 240s
    return {"attempts": attempts, "backoff_sn": backoff_sn, "context_mode": mode}


@_pano_korumali
def gorev_guncelle(task_id: str, durum: str | None = None, **fields) -> dict | None:
    board = _read_json(TASK_BOARD)
    for t in board:
        # S-05: bozuk kayitta KeyError yerine sessiz atlama
        if t.get("task_id") == task_id:
            if durum:
                if durum not in GOREV_DURUMLARI:
                    raise ValueError(f"Gecersiz durum: {durum}")
                t["durum"] = durum
                # K7: Failed durumunda attempts artir
                if durum == "failed":
                    t["attempts"] = t.get("attempts", 0) + 1
            t.update(fields)
            if durum in ("done", "blocked"):
                t["bitis"] = datetime.now().isoformat(timespec="seconds")
                # ORCH-05: done/blocked oldugunda bu göreve ait tum kilitleri otomatik birak.
                # ORCH-05b: Blok yalniz done/blocked'da calisir; onceden her guncellemede
                # (aktif/review/not) kilit dusuyordu -> file_locks.json surekli bos kaliyordu.
                locks = _read_json(FILE_LOCKS)
                kalan = {d: l for d, l in locks.items() if l.get("task_id") != task_id}
                if len(kalan) != len(locks):
                    _write_json(FILE_LOCKS, kalan)
            # S-05: her yazimda eski/bozuk kayitlar kendini onarir (self-healing).
            pano_normalize(board)
            _write_json(TASK_BOARD, board)
            _md_yaz(board)
            _sync_tetikle()
            return t
    return None


def gorev_getir(task_id: str) -> dict | None:
    """Tek görevi getir (delta-only okuma)."""
    for t in gorev_listesi():
        if t.get("task_id") == task_id:
            return t
    return None


def okuma_listesi_olustur(task_id: str) -> list[str]:
    """K6: Agent icin otomatik 'ne okunmalı' listesi.
    
    Agent bu listeden fazla dosya acamaz (exploration yasak).
    Tasarruf: ~1500-3000 token/oturum.
    """
    gorev = gorev_getir(task_id)
    if not gorev:
        return []
    
    # Gorevin dosyalari
    dosyalar = list(gorev.get("dosyalar", []))
    
    # Sahip ajana bagli dosya eslemesi
    sahip = gorev["sahip"]
    sahip_dosyalari = {
        "gelistirici": ["src/company_master/etl", "src/company_master/db", "scripts"],
        "mimar": ["src/company_master/schema", "src/company_master/db"],
        "kalite": ["tests", "data/kpi_raporu.md"],
        "arastirmaci": ["AI proje v1/V10/07_referanslar", "scripts/mersis_api_research.md"],
        "web_kazima": ["src/company_master/engine", "src/company_master/utils"],
        "koordinatör": ["AI proje v1/V10", "AGENT_SYNC.md"],
    }
    
    for dizin in sahip_dosyalari.get(sahip, []):
        if dizin not in dosyalar:
            dosyalar.append(dizin)
    
    # Mevcut olmayan dosyalari filtrele (token bosa harcanmasin)
    mevcut = []
    ROOT = Path(__file__).resolve().parents[3]
    for d in dosyalar:
        if (ROOT / d).exists():
            mevcut.append(d)
    
    return mevcut[:5]  # Maksimum 5 okunacak (token limiti)


def gorev_brief(task_id: str) -> str | None:
    gorev = gorev_getir(task_id)
    if not gorev:
        return None
    locks = locklar()

    brief = f"""## Gorev Brief: {gorev['task_id']}

**Gorev:** {gorev['baslik']}
**Sahip:** {gorev['sahip']}
**Oncelik:** {gorev['oncelik']}
**Durum:** {gorev['durum']}

### Dosyalar (sadece bunlari ac)
{chr(10).join(f"  - {d}" for d in gorev.get("dosyalar", [])) if gorev.get("dosyalar") else "  (dosya belirtilmemis)"}

### Aktif Lock'lar
{chr(10).join(f"  - {d} ({lk['sahip']})" for d, lk in locks.items()) if locks else "  (kilit yok)"}

### Kurallar
- Sadece yukaridaki dosyalari ac ve degistir
- Baska dosya acma (exploration yasak)
- Gorev bitince: gorev-guncelle {task_id} --durum done
- Basarisiz olursa: gorev-guncelle {task_id} --durum blocked --not "hata_aciklamasi"
"""
    return brief


# ---- K3: Session Handoff ----
HANDOFF_FILE = STATE_DIR / "handoffs.json"


def handoff_yaz(task_id: str, tamamlandi: str, sonraki_adim: str = "",
                dikkat_edilmesi: str = "") -> None:
    handoffs: dict = {}
    if HANDOFF_FILE.exists():
        handoffs = json.loads(HANDOFF_FILE.read_text(encoding="utf-8"))
    handoffs[task_id] = {
        "tamamlandi": tamamlandi,
        "sonraki_adim": sonraki_adim,
        "dikkat_edilmesi": dikkat_edilmesi,
        "tarih": datetime.now().isoformat(timespec="seconds"),
    }
    # ORCH-03: atomik yazma (paralel ajan yazma cakismasi onlemi)
    atomic_write_text(HANDOFF_FILE, json.dumps(handoffs, ensure_ascii=False, indent=2))
    _sync_tetikle()


def handoff_oku(task_id: str) -> dict | None:
    if not HANDOFF_FILE.exists():
        return None
    return json.loads(HANDOFF_FILE.read_text(encoding="utf-8")).get(task_id)


def handoff_tum() -> dict:
    if not HANDOFF_FILE.exists():
        return {}
    return json.loads(HANDOFF_FILE.read_text(encoding="utf-8"))


def agent_sync_olustur() -> str:
    """task_board.json'dan AGENT_SYNC.md icerigi olusturur."""
    board = gorev_listesi()
    handoffs = handoff_tum()
    lines = [
        "# AGENT_SYNC — Otomatik Olusturuldu (task_board'dan)",
        "",
        f"> Son guncelleme: {datetime.now().isoformat(timespec='seconds')}",
        f"> Kaynak: data/orchestrator/task_board.json",
        "",
        "## Aktif Isler",
        "",
        "| Gorev | Baslik | Sahip | Oncelik | Durum |",
        "|-------|--------|-------|---------|-------|",
    ]
    # Dayaniklilik: eksik alanli eski kayitlar (orn. WIKI-01'de 'oncelik' yok)
    # tum AGENT_SYNC uretimini cokertmemeli.
    for t in board:
        if t.get("durum") not in ("done",):
            lines.append(f"| {t.get('task_id', '-')} | {str(t.get('baslik', '-'))[:40]} | "
                         f"{t.get('sahip', '-')} | {t.get('oncelik', '-')} | {t.get('durum', '-')} |")
    lines += ["", "## Tamamlananlar (Son 10)", "",
              "| Gorev | Baslik | Sahip | Bitis |", "|-------|--------|-------|-------|"]
    done = [t for t in board if t.get("durum") == "done"][-10:]
    for t in done:
        lines.append(f"| {t.get('task_id', '-')} | {str(t.get('baslik', '-'))[:40]} | "
                     f"{t.get('sahip', '-')} | {(t.get('bitis') or '-')[:10]} |")
    if handoffs:
        lines += ["", "## Son Handoff'lar", ""]
        for tid, h in list(handoffs.items())[-5:]:
            lines.append(f"- **{tid}**: {h.get('tamamlandi', '')[:50]}")
    return "\n".join(lines) + "\n"


def agent_sync_yaz() -> None:
    """AGENT_SYNC.md'yi board'dan otomatik yeniden yazar.

    ORCH-03: KOK AGENT_SYNC.md + data/orchestrator/AGENT_SYNC.md kopyasi
    ayni icerikle atomik olarak yazilir (tek yazar: pano).
    """
    sync_path = AGENT_SYNC_MD
    icerik = agent_sync_olustur()
    if sync_path.exists():
        mevcut = sync_path.read_text(encoding="utf-8")
        # Eger dosya otomatik olusturulmus stile uyuyorsa tamamen yeniden yaz
        if "Otomatik Olusturuldu" in mevcut or mevcut.strip().startswith("# AGENT_SYNC"):
            final = icerik
        else:
            # Manuel icerik varsa, otomatik bolumu sona ekle
            if "## Otomatik Ozet (task_board)" not in mevcut:
                final = mevcut + "\n\n## Otomatik Ozet (task_board)\n\n" + icerik
            else:
                final = mevcut
        atomic_write_text(sync_path, final)
    else:
        final = icerik
        atomic_write_text(sync_path, final)
    # Kopyayi da esitle (ayni final icerik)
    try:
        atomic_write_text(AGENT_SYNC_MD_KOPYA, final)
    except Exception:
        pass


def gorev_listesi(durum: str | None = None) -> list[dict]:
    board = _read_json(TASK_BOARD)
    if durum:
        return [t for t in board if t["durum"] == durum]
    return board


# ---- Dosya Lock (cakisma onleme) ----
def _lock_alan(sahip: str, dosya: str, task_id: str) -> None:
    locks = _read_json(FILE_LOCKS)
    if dosya in locks and locks[dosya]["sahip"] != sahip:
        raise PermissionError(
            f"{dosya} zaten {locks[dosya]['sahip']} tarafindan kilitli "
            f"(gorev: {locks[dosya]['task_id']})"
        )
    locks[dosya] = {
        "sahip": sahip,
        "task_id": task_id,
        "kilitlendi": datetime.now().isoformat(timespec="seconds"),
    }
    _write_json(FILE_LOCKS, locks)


def lock_birak(dosya: str, sahip: str) -> bool:
    locks = _read_json(FILE_LOCKS)
    if locks.get(dosya, {}).get("sahip") == sahip:
        del locks[dosya]
        _write_json(FILE_LOCKS, locks)
        _sync_tetikle()
        return True
    return False


def handoff_ekle(task_id: str, agent_id: str, output_path: str, summary: str) -> None:
    """Handoff kaydetme: handoffs.json'a çıktı kaydı ekler.

    Aynı task_id ile tekrar çağrıldığında önceki kaydı koruyarak
    guncelleme geçmişi tutar (duplicate-safe).
    """
    HANDOFFS = STATE_DIR / "handoffs.json"
    _ensure()
    data = _read_json(HANDOFFS) if HANDOFFS.exists() else {}
    entry = {
        "tamamlandi": f"{agent_id} çıktı üretti",
        "sonraki_adim": "İnceleme ve entegrasyon",
        "dikkat_edilmesi": "",
        "tarih": datetime.now().isoformat(timespec="seconds"),
        "output_path": output_path,
        "summary": summary,
    }
    if task_id not in data:
        data[task_id] = entry
    else:
        existing = data[task_id]
        if "guncelleme_gecmisi" not in existing:
            existing["guncelleme_gecmisi"] = []
        existing["guncelleme_gecmisi"].append(entry)
    _write_json(HANDOFFS, data)
    _sync_tetikle()

def lock_durum(dosya: str) -> dict | None:
    return _read_json(FILE_LOCKS).get(dosya)


def locklar() -> dict:
    return _read_json(FILE_LOCKS)


# ---- Canli Durum ----
def durum_guncelle(key: str, **fields) -> None:
    state = _read_json(STATE_JSON)
    entry = state.get(key, {})
    entry.update(fields)
    entry["updated_at"] = datetime.now().isoformat(timespec="seconds")
    state[key] = entry
    _write_json(STATE_JSON, state)


def durum_getir(key: str | None = None) -> Any:
    state = _read_json(STATE_JSON)
    return state if key is None else state.get(key)


# ---- Markdown gorunum (Obsidian/AGENT_SYNC icin) ----
def _md_yaz(board: list[dict]) -> None:
    lines = [
        "# Gorev Panosu — Orkestrator",
        "",
        "> Merkezi gorev listesi: herkes herkesin ne yaptigini takip eder.",
        "> Kaynak: `data/orchestrator/task_board.json` — Obsidian okumasi icin disa aktarilir.",
        "",
        "## Aktif Isler",
        "",
        "| Gorev | Baslik | Sahip | Oncelik | Durum | Dosyalar |",
        "|-------|--------|-------|---------|-------|----------|",
    ]
    aktif = [t for t in board if t.get("durum") not in ("done",)]
    # Duplika görevleri engelle: aynı task_id daha önce görünüyorsa atla
    gorulen_ids = set()
    for t in aktif:
        task_id = t.get("task_id", "-")
        if task_id in gorulen_ids:
            continue
        gorulen_ids.add(task_id)
        # Dayaniklilik: eski/elle eklenmis kayitlarda alanlar eksik olabilir.
        # Tek eksik alan yuzunden TUM pano yazimi cokmemeli (bkz. WIKI-01 / KeyError 'oncelik').
        dosyalar = t.get("dosyalar") or []
        dos = ", ".join(dosyalar[:3]) if dosyalar else "-"
        lines.append(f"| {task_id} | {t.get('baslik', '-')} | {t.get('sahip', '-')} | "
                     f"{t.get('oncelik', '-')} | {t.get('durum', '-')} | {dos} |")
    lines += ["", "## Tamamlananlar", "",
              "| Görev | Baslik | Sahip | Bitis |", "|-------|--------|-------|-------|"]
    done = [t for t in board if t.get("durum") == "done"]
    for t in done:
        lines.append(f"| {t.get('task_id', '-')} | {t.get('baslik', '-')} | "
                     f"{t.get('sahip', '-')} | {(t.get('bitis') or '-')} |")
    atomic_write_text(TASK_MD, "\n".join(lines) + "\n")