# D-190: MIMIR Architect Rapor Yazma — Otomatik Flow

**Karar**: D-190 MIMIR Seviye 1 architect hakkı → ölçüm/rapor görevlerini MIMIR otomatik yazacak.

**Hedef**: İnsan müdahalesi sıfır. Görev tamamlandığında MIMIR rapor yazar, pano güncellenir.

---

## 1. Mevcut Durum (El ile)

- Görev tamamlanır (task durum = done)
- **İnsan (ihsan vb.)** → rapor yazması 1-2 saat kaybı
- Rapor: `data/orchestrator/{TASK_ID}_rapor_{TARIH}_{AJAN}.md`
- Pano: not alanına rapor yolu yazılır

**Problem**: 3-5 görev/sprint = 10+ saat boşa gidiyor.

---

## 2. D-190 Otomatik Flow

### 2.1 Tetikleme: task durum → done

```
task_board.json [görev X, durum=done, mod=architect]
↓
trigger.py tetik_al() → durum check
↓
trigger.py teslim_et() [durum_guncelle(task_id, durum="done")]
↓
(NEW) mimir_rapor_trigger() — MIMIR tetik
```

### 2.2 MIMIR Rapor Yazma (Yeni Akış)

```python
# src/company_master/intelligence/mimir_rapor.py (YENİ)

from datetime import datetime, timezone
from pathlib import Path
from src.company_master.orchestrator import task_board as tb

class MimirRaporYazici:
    """MIMIR architect rapor otomasyonu."""
    
    def __init__(self):
        self.data_dir = Path("Huginn Data Insights/data/orchestrator")
    
    def rapor_yazmayi_tetikle(self, task_id: str) -> bool:
        """Görev done olunca MIMIR rapor yaz (insan müdahalesi yok)."""
        gorev = tb.gorev_getir(task_id)
        if not gorev or gorev.get("durum") != "done":
            return False
        
        # 1. Rapor taslağı: görev + brief + talimat oku
        rapor_icerik = self._rapor_hazirla(gorev)
        
        # 2. Dosya yaz: {TASK_ID}_rapor_{TARIH}_{AJAN}.md
        rapor_dosya = self._rapor_dosyasini_yaz(task_id, rapor_icerik)
        
        # 3. Pano güncelle: not alanına rapor path ekle
        tb.gorev_guncelle(task_id, not=f"Rapor: {rapor_dosya}")
        
        return True
    
    def _rapor_hazirla(self, gorev: dict) -> str:
        """Görev + brief → rapor taslağı."""
        task_id = gorev["task_id"]
        sahip = gorev.get("sahip", "?")
        baslik = gorev.get("baslik", "")
        baslangic = gorev.get("baslangic", "")
        bitis = gorev.get("bitis", "")
        
        # Brief yolundan dosya oku (brief path pano'da)
        brief_path = gorev.get("talimat") or self._brif_dosya_bul(task_id)
        brief_icerik = self._dosya_oku(brief_path) if brief_path else "Brief bulunamadı"
        
        rapor = f"""# {task_id} Raporu

- **Sahip**: {sahip}
- **Tarih**: {datetime.now(timezone.utc).isoformat(timespec='seconds')}
- **Durum**: ✅ Tamamlandı

## Görev Özeti

**Başlık**: {baslik}
**Başlangıç**: {baslangic}
**Bitiş**: {bitis}

## Brief İçerik

```
{brief_icerik}
```

## Bulgular & Öneriler

(MIMIR Seviye 1 — otomatik oluşturuldu)

### Başarı Kriterleri
- ✅ Test regresyonu temiz
- ✅ Brief uyumlu implentasyon
- ✅ Kod incelemesi bekleniyor

## Sonraki Adım

Rapor review → approve/reject (insan karar verir, MIMIR yazı).
"""
        return rapor
    
    def _rapor_dosyasini_yaz(self, task_id: str, icerik: str) -> Path:
        """Rapor dosyasını yaz → path döner."""
        tarih = datetime.now(timezone.utc).isoformat(timespec='seconds').split('T')[0]
        dosya_adi = f"{task_id}_rapor_{tarih}_mimir.md"
        dosya_yolu = self.data_dir / dosya_adi
        
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            f.write(icerik)
        
        return dosya_yolu
    
    def _brif_dosya_bul(self, task_id: str) -> Path | None:
        """Task ID'den brief dosyasını ara."""
        plans_dir = Path("Huginn Data Insights/plans")
        for brif in plans_dir.glob(f"brief_*_{task_id}.md"):
            return brif
        return None
    
    def _dosya_oku(self, yol: Path | str) -> str:
        """Dosya içeriğini oku; başarısızsa empty string."""
        try:
            with open(yol, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
```

### 2.3 Tetikleyici Entegrasyon

**File: `src/company_master/orchestrator/trigger.py`** — teslim_et() güncellemesi

```python
from src.company_master.intelligence.mimir_rapor import MimirRaporYazici

def teslim_et(task_id: str, ajan: str, output_path: str, summary: str) -> dict[str, Any]:
    """Görev teslimi + (NEW) MIMIR rapor yazma tetiklemesi."""
    
    # Orijinal akış: tetik → durum update
    result = _teslim_et_eski(task_id, ajan, output_path, summary)
    
    # (NEW) D-190: Architect görevse MIMIR rapor yaz
    if result.get("durum") == "done":
        gorev = tb.gorev_getir(task_id)
        if gorev and gorev.get("mod") == "architect":
            yazici = MimirRaporYazici()
            yazici.rapor_yazmayi_tetikle(task_id)
    
    return result
```

---

## 3. Test Senaryoları

### Test 1: Architect görev tamamlandı → Rapor yazıldı mı?

```python
# tests/test_d190_mimir_rapor.py

def test_architect_gorev_rapor_auto_yazilir(tmp_path, monkeypatch):
    """Architect görev done → rapor otomatik yazılır."""
    task_id = "RESEARCH-PONYTALE"
    
    # 1. Pano'da görev kur
    gorev = {
        "task_id": task_id,
        "baslik": "Test araştırması",
        "sahip": "ihsan",
        "durum": "active",
        "mod": "architect",  # ← KEY
        "talimat": "plans/brief_ihsan_RESEARCH-PONYTALE.md",
    }
    tb.gorev_ekle(gorev)
    
    # 2. Görev tamamla
    tb.gorev_guncelle(task_id, durum="done")
    
    # 3. Tetikle: teslim_et() → MIMIR rapor yaz
    trigger.teslim_et(
        task_id=task_id,
        ajan="ihsan",
        output_path="rapor_path",
        summary="Test tamamlandı"
    )
    
    # 4. Rapor dosyası oluştu mu?
    rapor_dosya = Path("Huginn Data Insights/data/orchestrator") / f"{task_id}_rapor_*_mimir.md"
    assert list(Path.cwd().glob(str(rapor_dosya))), "Rapor dosyası yazılmadı!"
    
    # 5. Pano'da not alanında rapor path yazılı mı?
    guncel = tb.gorev_getir(task_id)
    assert "rapor" in guncel.get("not", "").lower()
```

### Test 2: Code görev done → Rapor yazılmadı (architect değil)

```python
def test_code_gorev_rapor_yazilmaz(tmp_path, monkeypatch):
    """Code görev → MIMIR rapor yazılmaz (mod != architect)."""
    task_id = "UI-01"
    
    gorev = {
        "task_id": task_id,
        "mod": "code",  # ← CODE
        "durum": "active",
    }
    tb.gorev_ekle(gorev)
    tb.gorev_guncelle(task_id, durum="done")
    trigger.teslim_et(task_id, "ihsan", "", "")
    
    # Rapor dosyası yazılmadı
    rapor_dosya = Path("Huginn Data Insights/data/orchestrator") / f"{task_id}_rapor_*_mimir.md"
    assert not list(Path.cwd().glob(str(rapor_dosya)))
```

### Test 3: Brief bulunamadı → Rapor "Brief bulunamadı" yazar

```python
def test_brief_yoksa_rapor_hala_yazilir(tmp_path, monkeypatch):
    """Brief dosyası yok → rapor yine yazılır (empty brief uyarısı)."""
    task_id = "GHOST-01"  # Brief yok
    
    gorev = {
        "task_id": task_id,
        "mod": "architect",
        "durum": "active",
        "talimat": None,
    }
    tb.gorev_ekle(gorev)
    tb.gorev_guncelle(task_id, durum="done")
    trigger.teslim_et(task_id, "mimir", "", "")
    
    # Rapor yazıldı mı?
    rapor_dosya = Path("Huginn Data Insights/data/orchestrator") / f"{task_id}_rapor_*_mimir.md"
    rapor = list(Path.cwd().glob(str(rapor_dosya)))
    assert rapor, "Rapor yazılmadı!"
    
    # İçerinde "Brief bulunamadı" var mı?
    with open(rapor[0]) as f:
        assert "Brief bulunamadı" in f.read()
```

---

## 4. Admin Panel: Rapor Erişimi

### 4.1 Rapor Listesi Sekmesi (Admin Panel)

**Lokasyon**: `web_dashboard/tabs/admin_panel.py` — rapor sekmesi ekle

```python
def render_rapor_listesi_tab() -> None:
    """Admin panel → raporlar sekmesi (orkestrator her zaman, KAHIN gerektiğinde)."""
    
    # Erişim denetimi
    aktif_rol = st.session_state.get("rol", "")
    if aktif_rol not in ["orkestrator", "kahin"]:
        st.error("❌ Erişim reddedildi. Orkestrator veya KAHIN gerekli.")
        return
    
    st.header("📊 MIMIR Raporları")
    
    # 1. Filtreleme
    col1, col2 = st.columns(2)
    with col1:
        rapor_tipi = st.selectbox(
            "Rapor türü:",
            ["Tümü", "Architect", "Ölçüm", "Tasarım", "Bulgu"]
        )
    with col2:
        siralay = st.selectbox(
            "Sıralama:",
            ["En yeni", "En eski", "Görev ID'si"]
        )
    
    # 2. Raporları oku
    data_dir = Path("Huginn Data Insights/data/orchestrator")
    raporlar = sorted(
        data_dir.glob("*_rapor_*_mimir.md"),
        key=lambda x: x.stat().st_mtime,
        reverse=(siralay == "En yeni")
    )
    
    if not raporlar:
        st.info("📭 Rapor bulunamadı.")
        return
    
    # 3. Tablo: görev → rapor → tarih → sahip
    rapor_listesi = []
    for rapor_dosya in raporlar:
        # Dosya adından parse: {TASK_ID}_rapor_{TARIH}_mimir.md
        parts = rapor_dosya.stem.split("_rapor_")
        if len(parts) == 2:
            task_id = parts[0]
            tarih = parts[1].replace("_mimir", "")
            
            # Pano'dan görev oku (sahip, durum bilgisi)
            gorev = tb.gorev_getir(task_id)
            sahip = gorev.get("sahip", "?") if gorev else "?"
            durum = gorev.get("durum", "?") if gorev else "?"
            
            rapor_listesi.append({
                "task_id": task_id,
                "tarih": tarih,
                "sahip": sahip,
                "durum": durum,
                "dosya": rapor_dosya.name,
                "yol": str(rapor_dosya)
            })
    
    # 4. Görüntüle
    if st.checkbox("📖 Rapor ayrıntılarını göster"):
        for r in rapor_listesi:
            with st.expander(f"🔹 {r['task_id']} ({r['tarih']}) — {r['sahip']}"):
                try:
                    with open(r["yol"], "r", encoding="utf-8") as f:
                        icerik = f.read()
                    st.markdown(icerik)
                    
                    # İndir butonu
                    st.download_button(
                        label="⬇️ İndir (Markdown)",
                        data=icerik,
                        file_name=r["dosya"],
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"❌ Rapor okunamadı: {e}")
    
    # Tablo görünümü
    df_rapor = pd.DataFrame(rapor_listesi)
    st.dataframe(
        df_rapor[["task_id", "tarih", "sahip", "durum"]],
        use_container_width=True,
        hide_index=True
    )
```

### 4.2 Erişim Kontrolü

**Kural**:
- **Orkestrator** (her zaman): Tüm raporları oku + indir
- **KAHIN** (gerektiğinde): Tüm raporları oku + indir
- **Diğer roller** (ihsan/yasu/mimar vb.): Sadece kendi raporlarını oku (future: granular)

**Uygulama**:
```python
# web_dashboard/tabs/admin_panel.py

def rapor_erisisim_denetimi(rol: str, rapor_task_id: str) -> bool:
    """Rol + rapor → erişim izni (orkestrator = her zaman, kahin = her zaman)."""
    if rol in ["orkestrator", "kahin"]:
        return True  # Her zaman oku
    return False
```

### 4.3 Admin Panel Tab'ı Ekle

**Dosya**: `web_dashboard/tabs/__init__.py` — TabTanimi ekle

```python
TabTanimi(
    anahtar="rapor_listesi",
    baslik="📊 Raporlar (MIMIR)",
    icon="📊",
    path="admin/rapor_listesi",
    render_fn=admin_panel.render_rapor_listesi_tab,
    roller_yesil={"orkestrator", "kahin"},
    tur="yonetim"
)
```

---

## 5. İmplementasyon Planı

| # | Görev | Dosya | Test | Tahmini |
|---|-------|-------|------|---------|
| 1 | MimirRaporYazici sınıfı + rapor_yazmayi_tetikle() | src/company_master/intelligence/mimir_rapor.py | test_d190_mimir_rapor.py (3 test) | 2h |
| 2 | trigger.py teslim_et() entegrasyonu | src/company_master/orchestrator/trigger.py | trigger regresyonu (12 test) | 1h |
| 3 | Regresyon testi | tests/ | full suite | 1h |
| 4 | AGENTS.md D-190 güncelleme | Huginn Data Insights/AGENTS.md | - | 30m |

**Toplam: 4.5 saat kod + test**

---

## 5. Yararlar

- ✅ İnsan müdahalesi sıfır: Architect görev done → rapor otomatik
- ✅ Hız: 1-2 saat/görev boşa gitmiyor
- ✅ Tutarlılık: MIMIR rapor template → standart format
- ✅ Denetlenebilir: Rapor review → approve/reject (insan karar)

---

## 6. Risk & Mitigation

| Risk | Etki | Mitigation |
|------|------|-----------|
| Brief bulunamadı | Eksik rapor | "Brief bulunamadı" yazması yeterli; manuel düzeltme |
| Rapor dosyası düşerse | Data loss | decision_log.jsonl ile audit trail + yedek |
| MIMIR hata yazarsa | Yanlış rapor | Review aşamasında catch; auto-reject seçeneği |

---

## Sonraki Adımlar

1. Görev kurgula: ALTYAPI-MIMIR-RAPOR-OTOMASYONU-01 (P2, mimar/yasu)
2. Brief yaz: plans/brief_mimar_ALTYAPI-MIMIR-RAPOR-OTOMASYONU-01.md
3. Pano'ya ekle + tetik
