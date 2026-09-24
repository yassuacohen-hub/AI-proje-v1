İlgili: [[README]]

# VAULT_AUTOMATION_TEMPLATE

> Multi-ajan / multi-repo Obsidian vault otomasyonu için başlangıç şablonu.
> Kaynak: Huginn Data Projesi sprint 2026-09-21 deneyimi (VAULT-XREF-DUBLO, ORCH-SENKRON-01, DUBLO-MERGE-01).
> Sürüm: 1.0 · Tarih: 2026-09-21

---

## 1. Genel Bakış

### Bu şablon ne için?

Birden fazla AI ajanının ortak hafıza olarak tek bir Obsidian vault'u kullandığı projelerde,
ilk günden kurulması gereken minimum otomasyon iskeletini verir.

### Hangi proje türlerine uygun?

| Proje türü | Uygunluk | Not |
|---|---|---|
| Multi-ajan (Roo, Claude, Cline, Kilo aynı repo) | ✓ Birebir | Ana hedef |
| Multi-repo / git worktree ikiz ağaçlar | ✓ Birebir | İkiz yönetimi kritik |
| Tek ajan + tek repo vault | ~ Kısmi | Bölüm 3 Adım 1-3 yeterli, senkron gereksiz |
| Salt insan kullanımlı kişisel vault | ✗ Fazla ağır | Hub not + sağlık script'i yeter |

### Temel ilke

**Vault = ajanların ortak hafızası.** Hafıza bozulursa ajan kararı bozulur.
Bu yüzden üç şey kural haline gelmeli:

1. **SSOT (Single Source of Truth):** Tek canonical ağaç seç, diğerleri türev.
2. **Silme yasağı:** Hiçbir otomasyon dosya silmez. Arşivler, yedekler, taşır.
3. **Append-only:** Karar defteri ve pano birleşmeleri ekleme yönünde, üzerine yazmaz.

---

## 2. Bu Sprint Deneyimi (2026-09-21)

### 2.1 Başarılar

| Alan | Yapılan | Ölçülen sonuç |
|---|---|---|
| **Vault temizliği** | Obsidian native `userIgnoreFilters` ile paralel git ağaçları indeksten çıkarıldı | 1114 → 408 dosya (%63 ↓), ikiz 955 → 25 (%97 ↓) |
| **Hub not otomasyonu** | `vault_saglik.py --harita` ile dizin bazlı `VAULT_HARITA.md` üretimi | Orphan 916 → 2 (%99 ↓) |
| **Kırık link tespiti** | Path normalizasyonu (`as_posix().lower()` + çapa kesme) | 455 sahte → 46 gerçek kırık link |
| **Senkronizasyon** | `senkron_append.py` + `pano_merge.py`, append-only strateji | +106 karar, +50 görev, **0 silme, 0 veri kaybı** |
| **İkiz birleştirme** | `ikiz_birlestir.py` dry-run → uygula, yedek + arşiv | 2 ikiz çift birleşti, kırık link artışı 0 |
| **Yedek rotasyonu** | `kilo_backup_rotate.py`, haftalık scheduler, silme yok | En yeni 3 yedek, kalan arşive |

**Çalışan desenler (bir sonraki projede aynen taşınmalı):**

- **Ladder yaklaşımı:** Önce native platform özelliği (Obsidian ignore filter), sonra script.
  v1 planı 955 redirect notu yazacaktı; v2 tek ayar dosyasıyla çözdü → ~%85 token tasarrufu.
- **Dry-run zorunluluğu:** Her yıkıcı işlem önce `--dry-run`, çıktısı dosyaya yazılıp incelendi.
- **Pre/post doğrulama:** Merge öncesi satır sayımı, sonrası `--rapor` ile metrik karşılaştırması.
- **Karar defteri:** Her otomasyon adımı JSONL karar kaydıyla kapandı (D-171…D-176).

### 2.2 Sınırlar (çözülemeyenler)

| Sınır | Açıklama | Sonraki projede ne yapılmalı |
|---|---|---|
| **Xref tam otomatik olamadı** | 46 kırık link kaldı; hedefleri silinmiş/taşınmış eski raporlara ait. Otomatik "tahmin et ve düzelt" veri bozma riski taşıdığı için elle incelemeye bırakıldı (D-175 beklemede). | Link kırılmasını **önle**: pre-commit hook'ta `--kontrol` çalıştır, kırık link ile commit engelle. |
| **Submodule cleanup manuel** | `.gitmodules` içeren ağaçların temizliği elle adım gerektirdi; submodule mü, düz klasör mü kararı baştan verilmemişti. | Gün 0'da karar ver ve karar defterine yaz (bkz. Bölüm 5.3). |
| **Push upstream tracking eksik** | Worktree branch'lerinde upstream set edilmediği için `git push` elle `-u` istedi, scheduler'dan çalışan push script'i sessizce başarısız oldu. | Worktree kurulumunda `--track` zorunlu (bkz. Bölüm 3 Adım 1). |
| **Paralel evrim** | Merkez ve worktree panoları bağımsız evrilip 261 alanda çelişti. Merge dürüst yapıldı ama "kim hak sahibi" kuralı sonradan yazıldı. | SSOT kuralını **ilk gün** yaz, senkron tek yönlü olsun. |
| **Orphan sınıflandırması kaba** | Arşive taşınan ikizler "yeni orphan" olarak raporlandı (1 → 3). Gerçek orphan ile taşınmış dosya ayırt edilemedi. | Arşiv klasörlerini sağlık taramasında ayrı kategori yap. |

---

## 3. Şablon Rehberi — Adım Adım

### Adım 1: Repo Yapısı

```
proje-kok/
├── .obsidian/
│   └── app.json              # userIgnoreFilters — ÖNCE bu
├── vault/                    # veya repo kökü = vault
│   ├── VAULT_HARITA.md       # otomatik üretim, hub not
│   └── gorev_panosu.md       # insan okunur pano
├── scripts/
│   ├── vault_saglik.py       # tarama + rapor + harita
│   ├── senkron_fark.py       # iki ağaç arası fark
│   ├── pano_merge.py         # append-only pano birleştirme
│   └── karar_yaz.py          # decision_log.jsonl'e kayıt
├── data/orchestrator/
│   ├── decision_log.jsonl    # append-only karar defteri
│   ├── task_board.json       # makine okunur pano (SSOT)
│   └── *_rapor_*.md          # sprint raporları
├── _ARSIV_<konu>_<tarih>/    # silme yok, buraya taşı
└── AGENTS.md                 # ajan kuralları
```

**Gün 0 komutları:**

```bash
git init
git config core.autocrlf false          # Windows'ta satır sonu kirliliğini önler
mkdir -p scripts data/orchestrator plans
printf '{"userIgnoreFilters": [".venv/", ".git/", "node_modules/", ".obsidian/"]}' > .obsidian/app.json
touch data/orchestrator/decision_log.jsonl

# Worktree açarken upstream tracking ZORUNLU (bu sprintte unutuldu):
git worktree add ../proje-worktree -b feature/x --track origin/main
git -C ../proje-worktree push -u origin feature/x
```

---

### Adım 2: Script Şablonları

Dört script yeter. Hepsi tek dosya, stdlib-only, argümansız da çalışır.

#### 2.1 `scripts/vault_saglik.py` — tarama, kırık link, ikiz, orphan, hub not

```python
#!/usr/bin/env python3
"""Vault saglik taramasi: kirik link, ikiz dosya, orphan, hub not uretimi.

Kullanim:
    python scripts/vault_saglik.py --rapor       # JSON rapor
    python scripts/vault_saglik.py --harita      # VAULT_HARITA.md uret
    python scripts/vault_saglik.py --kontrol     # kirik link varsa exit 1 (CI/hook)
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# KRITIK: __file__ tabanli kok. Scheduler'dan calisirken cwd guvenilmez.
ROOT = Path(__file__).resolve().parent.parent
YOKSAY = {".git", ".obsidian", ".venv", "node_modules", "__pycache__", ".pytest_cache"}
WIKILINK = re.compile(r"\[\[([^\]|#]+)")  # [[hedef#capa|etiket]] -> hedef


def md_dosyalari(kok: Path):
    for p in kok.rglob("*.md"):
        if any(parca in YOKSAY or parca.startswith("_ARSIV") for parca in p.parts):
            continue
        yield p


def tara(kok: Path = ROOT) -> dict:
    dosyalar = list(md_dosyalari(kok))
    # KRITIK: as_posix() — wikilink'ler '/' kullanir, Windows Path '\' verir.
    harita = {p.relative_to(kok).as_posix().lower(): p for p in dosyalar}
    isim_harita = {p.stem.lower(): p for p in dosyalar}

    kirik, referans_alan = [], set()
    isim_gruplari = defaultdict(list)

    for p in dosyalar:
        isim_gruplari[p.stem.lower()].append(p.relative_to(kok).as_posix())
        metin = p.read_text(encoding="utf-8", errors="replace")
        for ham in WIKILINK.findall(metin):
            hedef = ham.strip().lower()
            bulunan = harita.get(f"{hedef}.md") or harita.get(hedef) or isim_harita.get(hedef)
            if bulunan is None:
                kirik.append({"kaynak": p.relative_to(kok).as_posix(), "hedef": ham.strip()})
            else:
                referans_alan.add(bulunan)

    return {
        "tarandi": len(dosyalar),
        "kirik_link": kirik,
        "ikiz_gruplar": {k: v for k, v in isim_gruplari.items() if len(v) > 1},
        "orphan": sorted(p.relative_to(kok).as_posix() for p in dosyalar if p not in referans_alan),
    }


def harita_uret(kok: Path = ROOT) -> str:
    dizinler = defaultdict(list)
    for p in md_dosyalari(kok):
        rel = p.relative_to(kok)
        dizinler[rel.parent.as_posix() if rel.parent.as_posix() != "." else "(kok)"].append(rel)

    satirlar = ["# VAULT_HARITA", "",
                "> Otomatik uretim: `python scripts/vault_saglik.py --harita`", ""]
    for dizin in sorted(dizinler):
        yollar = sorted(dizinler[dizin])
        satirlar += [f"## {dizin} ({len(yollar)})", ""]
        satirlar.append(", ".join(f"[[{y.with_suffix('').as_posix()}]]" for y in yollar))
        satirlar.append("")
    return "\n".join(satirlar)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapor", action="store_true")
    ap.add_argument("--harita", action="store_true")
    ap.add_argument("--kontrol", action="store_true")
    a = ap.parse_args()

    if a.harita:
        hedef = ROOT / "VAULT_HARITA.md"
        hedef.write_text(harita_uret(), encoding="utf-8")
        print(f"yazildi: {hedef}")
        return 0

    sonuc = tara()
    if a.kontrol:
        n = len(sonuc["kirik_link"])
        print(f"kirik link: {n}")
        return 1 if n else 0

    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())


def _self_check():
    """Calistir: python -c "import scripts.vault_saglik as m; m._self_check()" """
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        k = Path(d)
        (k / "a.md").write_text("[[b]] ve [[yok#capa]]", encoding="utf-8")
        (k / "b.md").write_text("bos", encoding="utf-8")
        r = tara(k)
        assert r["tarandi"] == 2, r
        assert [x["hedef"] for x in r["kirik_link"]] == ["yok"], r
        assert r["orphan"] == ["a.md"], r
    print("self-check OK")
```

#### 2.2 `scripts/senkron_fark.py` — iki ağaç arası fark

```python
#!/usr/bin/env python3
"""Iki vault agaci arasindaki fark: sadece A'da, sadece B'de, icerik farkli.

Kullanim:
    python scripts/senkron_fark.py "C:/proje/merkez" "C:/proje/worktree"
"""
import hashlib
import sys
from pathlib import Path

YOKSAY = {".git", ".obsidian", ".venv", "node_modules", "__pycache__"}


def imza(kok: Path) -> dict[str, str]:
    cikti = {}
    for p in kok.rglob("*.md"):
        if any(parca in YOKSAY for parca in p.parts):
            continue
        cikti[p.relative_to(kok).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()[:12]
    return cikti


def fark(a: Path, b: Path) -> dict:
    ia, ib = imza(a), imza(b)
    return {
        "sadece_a": sorted(set(ia) - set(ib)),
        "sadece_b": sorted(set(ib) - set(ia)),
        "farkli": sorted(y for y in set(ia) & set(ib) if ia[y] != ib[y]),
    }


if __name__ == "__main__":
    r = fark(Path(sys.argv[1]), Path(sys.argv[2]))
    for baslik, yollar in r.items():
        print(f"\n## {baslik} ({len(yollar)})")
        for y in yollar[:50]:
            print("  ", y)
```

#### 2.3 `scripts/pano_merge.py` — append-only pano birleştirme

```python
#!/usr/bin/env python3
"""Pano birlestirme: APPEND-ONLY. Silme yok, catisma varsa HEDEF degeri korunur.

Kullanim:
    python scripts/pano_merge.py hedef.json kaynak.json --dry-run
    python scripts/pano_merge.py hedef.json kaynak.json --uygula
"""
import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ANAHTAR = "id"  # gorev kimlik alani


def birlestir(hedef: list[dict], kaynak: list[dict]) -> tuple[list[dict], dict]:
    indeks = {g[ANAHTAR]: g for g in hedef}
    sayac = {"yeni_gorev": 0, "dolan_alan": 0, "korunan_catisma": 0}

    for g in kaynak:
        mevcut = indeks.get(g[ANAHTAR])
        if mevcut is None:
            hedef.append(g)
            indeks[g[ANAHTAR]] = g
            sayac["yeni_gorev"] += 1
            continue
        for alan, deger in g.items():
            if alan not in mevcut or mevcut[alan] in (None, "", []):
                mevcut[alan] = deger          # bos alani doldur
                sayac["dolan_alan"] += 1
            elif mevcut[alan] != deger:
                sayac["korunan_catisma"] += 1  # HEDEF kazanir, uzerine YAZMA
    return hedef, sayac


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("hedef"); ap.add_argument("kaynak")
    ap.add_argument("--uygula", action="store_true")
    a = ap.parse_args()

    hp, kp = Path(a.hedef), Path(a.kaynak)
    hedef = json.loads(hp.read_text(encoding="utf-8"))
    kaynak = json.loads(kp.read_text(encoding="utf-8"))
    once = len(hedef)
    sonuc, sayac = birlestir(hedef, kaynak)

    print(f"gorev: {once} -> {len(sonuc)} | {sayac}")
    if not a.uygula:
        print("DRY-RUN — yazilmadi. Uygulamak icin --uygula")
        return 0

    damga = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    shutil.copy2(hp, hp.with_suffix(f".json.yedek_{damga}"))  # YEDEK once
    hp.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"yazildi. yedek: {hp.name}.yedek_{damga}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def _self_check():
    h = [{"id": "A", "durum": "aktif", "not": ""}]
    k = [{"id": "A", "durum": "bitti", "not": "x"}, {"id": "B", "durum": "yeni"}]
    sonuc, s = birlestir(h, k)
    assert len(sonuc) == 2 and s["yeni_gorev"] == 1
    assert sonuc[0]["durum"] == "aktif", "catisma hedef lehine korunmali"
    assert sonuc[0]["not"] == "x", "bos alan dolmali"
    print("self-check OK")
```

#### 2.4 `scripts/karar_yaz.py` — karar defterine kayıt

```python
#!/usr/bin/env python3
"""decision_log.jsonl'e APPEND-ONLY karar kaydi. Ayni id varsa yazmaz (idempotent).

Kullanim:
    python scripts/karar_yaz.py D-001 "Canonical agac secimi" "worktree/ canonical kabul edildi" --veren orkestrator
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

DEFTER = Path(__file__).resolve().parent.parent / "data/orchestrator/decision_log.jsonl"


def yaz(kimlik: str, baslik: str, karar: str, veren: str = "orkestrator",
        defter: Path = DEFTER, **ek) -> bool:
    defter.parent.mkdir(parents=True, exist_ok=True)
    defter.touch(exist_ok=True)
    mevcut = {json.loads(s)["id"] for s in defter.read_text(encoding="utf-8").splitlines() if s.strip()}
    if kimlik in mevcut:
        return False  # idempotent: tekrar yazma
    kayit = {"id": kimlik, "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "title": baslik, "decision": karar, "implemented_by": veren, **ek}
    with defter.open("a", encoding="utf-8") as f:
        f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
    return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("kimlik"); ap.add_argument("baslik"); ap.add_argument("karar")
    ap.add_argument("--veren", default="orkestrator")
    a = ap.parse_args()
    print("yazildi" if yaz(a.kimlik, a.baslik, a.karar, a.veren) else "zaten var (atlandi)")


def _self_check():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "log.jsonl"
        assert yaz("D-1", "t", "k", defter=p) is True
        assert yaz("D-1", "t", "k", defter=p) is False, "idempotent olmali"
        assert len(p.read_text(encoding="utf-8").strip().splitlines()) == 1
    print("self-check OK")
```

---

### Adım 3: Görev Panosu Şablonu

`gorev_panosu.md` — insan okunur görünüm. Makine kaynağı `task_board.json`.

```markdown
# Görev Panosu

> Kaynak: `data/orchestrator/task_board.json` (SSOT)
> Üretim: `python scripts/pano_render.py`  · Son güncelleme: YYYY-MM-DD

## Aktif

| Kod | Başlık | Sahip | Durum | Başlangıç | Kanıt |
|-----|--------|-------|-------|-----------|-------|
| PRJ-001 | Vault sağlık altyapısı | orkestrator | aktif | 2026-09-21 | [[data/orchestrator/PRJ-001_rapor]] |

## İncelemede

| Kod | Başlık | Sahip | Bekleyen onay |
|-----|--------|-------|---------------|

## Tamamlanan

| Kod | Başlık | Bitiş | Karar |
|-----|--------|-------|-------|

## Bloke

| Kod | Başlık | Engel | Sorumlu |
|-----|--------|-------|---------|

---
### Durum sözlüğü
`yeni` → `aktif` → `review` → `done` · yan durumlar: `blocked`, `iptal`, `archive`
```

---

### Adım 4: Karar Defteri (`decision_log.jsonl`)

Her satır bağımsız JSON. Append-only. Düzenleme yok — yanlış karar yeni kararla iptal edilir.

```jsonl
{"id": "D-001", "timestamp": "2026-01-01T00:00:00Z", "title": "Canonical agac secimi", "status": "implemented", "context": "Birden fazla git agaci ayni vault'ta indeksleniyordu", "decision": "worktree klasoru/ canonical kabul edildi; digerleri .obsidian ignore filtresine alindi", "details": {"canonical": "worktree/", "ignore_filter": [".venv/", "node_modules/"]}, "implemented_by": "orkestrator", "related_decisions": []}
{"id": "D-002", "timestamp": "2026-01-01T00:05:00Z", "title": "Silme yasagi", "status": "implemented", "context": "Otomasyon veri kaybi riski", "decision": "Hicbir script dosya silmez; _ARSIV_<konu>_<tarih>/ klasorune tasir ve .yedek_<tarih> kopyasi alir", "details": {"arsiv_deseni": "_ARSIV_{konu}_{YYYY-MM-DD}", "yedek_uzantisi": ".yedek_{YYYY-MM-DD}"}, "implemented_by": "orkestrator", "related_decisions": ["D-001"]}
```

**Zorunlu alanlar:** `id`, `timestamp` (UTC, ISO 8601), `title`, `decision`, `implemented_by`
**Önerilen:** `status` (`proposed` | `implemented` | `superseded`), `context`, `details`, `related_decisions`

---

## 4. Checklist — Yeni Proje Başlangıcı

### Git kurulumu
- [ ] `git init` + ilk commit yapıldı
- [ ] `.gitignore`: `.venv/`, `node_modules/`, `__pycache__/`, `*.yedek_*`, `_ARSIV_*/`
- [ ] `core.autocrlf false` (Windows'ta satır sonu kirliliği önlenir)
- [ ] `submodule` mü düz klasör mü kararı verildi **ve karar defterine yazıldı**

### Worktree
- [ ] `git worktree add <yol> -b <branch> --track origin/<base>`
- [ ] **Upstream tracking set edildi:** `git push -u origin <branch>` (bu sprintte atlandı, sorun çıkardı)
- [ ] `git worktree list` çıktısı doğrulandı
- [ ] `.worktreeinclude` / ignore dosyaları her ağaçta tutarlı

### Obsidian vault
- [ ] `.obsidian/app.json` → `userIgnoreFilters` dolduruldu (**script yazmadan önce**)
- [ ] Her paralel ağaç birbirini ignore ediyor
- [ ] `VAULT_HARITA.md` üretildi, orphan sayısı kabul edilebilir
- [ ] Baseline metrik kaydedildi (tarandı / ikiz / orphan / kırık link)

### Otomasyon
- [ ] 4 script kuruldu: `vault_saglik`, `senkron_fark`, `pano_merge`, `karar_yaz`
- [ ] Her script `ROOT = Path(__file__).resolve().parent.parent` kullanıyor (cwd'ye güvenmiyor)
- [ ] Her yıkıcı script `--dry-run` varsayılan, `--uygula` açık bayrak
- [ ] `_self_check()` fonksiyonları çalıştırıldı ve geçti

### Arşiv ve yedek
- [ ] `_ARSIV_<konu>_<tarih>/` deseni kararlaştırıldı
- [ ] Yedek rotasyonu kuruldu (en yeni N tut, kalan arşive — **silme yok**)
- [ ] Rollback prosedürü yazıldı ve bir kez denendi

### Scheduler
- [ ] Görev mutlak Python yolu ile tanımlandı (`C:\...\python.exe`)
- [ ] `Start in` / working directory alanı dolduruldu
- [ ] Çıktı log dosyasına yönlendirildi (`> log.txt 2>&1`)
- [ ] Scheduler ile elle çalıştırma aynı sonucu veriyor (unicode, encoding, yol)

### Kurallar
- [ ] `AGENTS.md` yazıldı: SSOT, silme yasağı, rapor formatı, karar id şeması
- [ ] Pre-commit hook: `python scripts/vault_saglik.py --kontrol`

---

## 5. Risk Noktaları

### 5.1 Relative vs. absolute path (scheduler'dan çalışan scriptler)

**Risk:** Task Scheduler / cron script'i beklenmedik cwd ile başlatır. Relative path sessizce yanlış dosyaya yazar veya hiç yazmaz.

```python
# YANLIS — cwd'ye bagimli
DEFTER = Path("data/orchestrator/decision_log.jsonl")

# DOGRU — dosya konumuna bagimli
ROOT = Path(__file__).resolve().parent.parent
DEFTER = ROOT / "data/orchestrator/decision_log.jsonl"
```

**Ek:** Windows'ta boşluklu klasör adları (`worktree klasoru`) tırnak ister; `Path` nesnesi kullan, string birleştirme yapma. Çıktıda Türkçe karakter varsa `encoding="utf-8"` her `read_text`/`write_text`/`open` çağrısında açık yazılmalı — Windows varsayılanı `cp1252`.

### 5.2 Worktree branch upstream tracking

**Risk:** Upstream set edilmemiş branch'te `git push` argümansız çalışmaz. Scheduler'dan çalışan otomasyon hata kodunu yutarsa commit'ler sessizce lokalde kalır.

```bash
git worktree add ../wt -b feature/x --track origin/main   # kurulumda
git -C ../wt push -u origin feature/x                     # ilk push
git -C ../wt rev-parse --abbrev-ref @{upstream}           # dogrulama
```

Otomasyon push script'i çıkış kodunu kontrol etmeli: `if not ok: raise` — sessiz başarısızlık yasak.

### 5.3 Submodule vs. klasör kararı

**Risk:** Submodule bağımsız versiyonlama verir ama her ajan için ek adım, detached HEAD tuzağı ve temizlikte manuel iş çıkarır (bu sprintte yaşandı).

| Kriter | Submodule | Düz klasör |
|---|---|---|
| Bağımsız sürüm/release | ✓ | ✗ |
| Ajan iş akışı basitliği | ✗ | ✓ |
| Temizlik / taşıma maliyeti | Yüksek (manuel) | Düşük |
| Ayrı repoda kullanılacak mı | ✓ gerekli | gereksiz |

**Kural:** "Bu kod başka bir projede bağımsız kullanılacak mı?" Hayırsa düz klasör.
Kararı gün 0'da `karar_yaz.py` ile deftere yaz.

### 5.4 Xref yönetimi — manuel inceleme zaruri mi?

**Evet, kısmen.** Kırık link iki sınıfa ayrılır:

| Sınıf | Örnek | Otomatik düzeltilebilir mi |
|---|---|---|
| Path/format hatası | `data\x` vs `data/x`, `[[a#capa]]` | ✓ Evet — normalizasyon |
| Hedef gerçekten yok | `[[00-Home]]` silinmiş | ✗ Hayır — tahmin veri bozar |

**Doğru strateji önlemedir:** `--kontrol` bayrağını pre-commit hook'a bağla, kırık link ile commit engelle. Mevcut 46 kırık link gibi birikmiş borçlar ancak elle kapanır.

```bash
# .git/hooks/pre-commit
python scripts/vault_saglik.py --kontrol || { echo "Kirik link var, commit iptal"; exit 1; }
```

### 5.5 Paralel evrim (SSOT ihlali)

**Risk:** İki ağaç aynı panoyu bağımsız günceller, çelişki birikir. Bu sprintte 261 alan çatıştı.

**Kural:** Senkron **tek yönlü** olmalı. Canonical → türev. Türevden canonical'a yazım ancak açık merge adımıyla, `--dry-run` + yedek + çatışma raporu ile.

### 5.6 Silme yasağı

Hiçbir otomasyon `unlink`/`rmtree` çağırmaz. Taşı + yedekle. Arşiv klasörü tarih damgalı, sağlık taramasında ayrı kategori.

---

## 6. İleride İyileştirmeler

Bu sprinte yetişmedi; sonraki sürümde eklenmeli:

| # | İyileştirme | Neden | Tahmini efor |
|---|---|---|---|
| 1 | **Pre-commit hook standardı** | Kırık linki oluşmadan engeller; en yüksek getirili tek madde | S |
| 2 | **`--duzelt --uygula` modu** (sadece path/format sınıfı) | 46 kırık linkin bir kısmı güvenle otomatik düzelir | M |
| 3 | **Arşiv-farkındalıklı orphan tespiti** | `_ARSIV_*` dosyaları sahte orphan üretiyor | S |
| 4 | **CI senkron trigger** | Merge sonrası otomatik append; elle çalıştırma unutuluyor | M |
| 5 | **Çatışma raporu ayrı dosya** | 261 çatışma stdout'ta kayboldu; inceleme için kalıcı çıktı gerek | S |
| 6 | **Karar defteri şema doğrulaması** | Alan adları karışık (`baslik` vs `title`, `veren` vs `implemented_by`) — tek şemaya oturt | S |
| 7 | **Metrik zaman serisi** | Her taramanın sonucu `vault_metrik.jsonl`'e; regresyon grafik olarak görülür | M |
| 8 | **Arşiv sıkıştırma + versiyonlama** | Arşiv klasörleri büyüyor; zip + git LFS | M |
| 9 | **Push wrapper (exit kodu kontrollü)** | Sessiz push başarısızlığı tekrarlamasın | S |
| 10 | **Dual-view dosya beyanı** | `gorev_panosu.md` gibi kasıtlı ikizler `.twinignore` ile beyan edilsin, elle atlanmasın | S |

---

## Ek: Hızlı Başlangıç

```bash
# 1. Iskelet
mkdir -p scripts data/orchestrator plans .obsidian
printf '{"userIgnoreFilters":[".venv/","node_modules/",".git/"]}' > .obsidian/app.json
touch data/orchestrator/decision_log.jsonl

# 2. Scriptleri Bolum 3.2'den kopyala, self-check calistir
python -c "import sys; sys.path.insert(0,'scripts'); import vault_saglik, pano_merge, karar_yaz; \
vault_saglik._self_check(); pano_merge._self_check(); karar_yaz._self_check()"

# 3. Baseline metrik
python scripts/vault_saglik.py --rapor > data/orchestrator/baseline_$(date +%Y-%m-%d).json
python scripts/vault_saglik.py --harita

# 4. Ilk kararlari yaz
python scripts/karar_yaz.py D-001 "Canonical agac" "<yol> canonical kabul edildi"
python scripts/karar_yaz.py D-002 "Silme yasagi" "Otomasyon silmez; arsivler ve yedekler"

# 5. Hook
echo 'python scripts/vault_saglik.py --kontrol || exit 1' > .git/hooks/pre-commit
```

---

**Şablon sürümü:** 1.0 · **Kaynak sprint:** 2026-09-21 · **İlgili kararlar:** D-171 … D-176
