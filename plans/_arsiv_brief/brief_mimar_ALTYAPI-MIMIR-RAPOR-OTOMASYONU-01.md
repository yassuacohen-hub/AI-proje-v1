# ALTYAPI-MIMIR-RAPOR-OTOMASYONU-01 — Brief

## Görev Özeti

D-190 KAHİN kararı: MIMIR Seviye 1 architect mode'da tasarım/ölçüm raporları otomatik yazacak.

**Mevcut durum**: Architect görev tamamlandığında İnsan (ihsan vb.) → rapor yazması 1-2 saat boşa gidiyor.

**Hedef**: Görev done → MIMIR rapor otomatik yazar (insan müdahalesi sıfır). Review aşamasında insan approve/reject karar verir.

---

## Bağımlılıklar

- D-182: MIMIR Seviye 1 tanımı (zaten yapılmış)
- D-63: Architect kapısı (zaten yapılmış)
- D-190: MIMIR architect hakkı kararı (karar_veren: KAHIN, 2026-09-23)

---

## Çıktı

### 1. Kod: `src/company_master/intelligence/mimir_rapor.py` (YENİ)

**Sınıf**: `MimirRaporYazici`

**Metodlar**:
- `rapor_yazmayi_tetikle(task_id: str) -> bool` — Görev done olunca MIMIR rapor yaz
  - Pano'dan görev oku (task_board)
  - Brief dosyasını bul ve oku
  - Rapor taslağı hazırla (template)
  - `{TASK_ID}_rapor_{TARIH}_mimir.md` dosyasını yaz
  - Pano not alanına rapor path ekle
  - True döner (başarılı)

- `_rapor_hazirla(gorev: dict) -> str` — Rapor taslağı üret
  - Input: görev dict (task_id, sahip, baslik, baslangic, bitis)
  - Brief oku, markdown template, "Bulgular & Öneriler" section boş
  - Output: rapor metni

- `_rapor_dosyasini_yaz(task_id: str, icerik: str) -> Path` — Rapor dosyası yaz
  - Tarih: ISO format'tan YYYY-MM-DD çıkar
  - Dosya adı: `{TASK_ID}_rapor_{TARIH}_mimir.md`
  - Path: `Huginn Data Insights/data/orchestrator/`
  - Return: Path object

- `_brif_dosya_bul(task_id: str) -> Path | None` — Task ID'den brief bul
  - `Huginn Data Insights/plans/` → `brief_*_{TASK_ID}.md` glob
  - İlk eşleşeni döner; yoksa None

- `_dosya_oku(yol: Path | str) -> str` — Dosya okuma (safe)
  - Try/except: başarısızsa empty string

---

### 2. Entegrasyon: `src/company_master/orchestrator/trigger.py` (GÜNCELLEME)

**Fonksiyon**: `teslim_et(task_id, ajan, output_path, summary) -> dict`

**Değişiklik**:
```python
# Orijinal teslim_et() sonunda:
result = _teslim_et_eski(...)

# (NEW) D-190: Architect görevse MIMIR rapor yaz
if result.get("durum") == "done":
    gorev = tb.gorev_getir(task_id)
    if gorev and gorev.get("mod") == "architect":
        from src.company_master.intelligence.mimir_rapor import MimirRaporYazici
        yazici = MimirRaporYazici()
        yazici.rapor_yazmayi_tetikle(task_id)

return result
```

**Mantık**: 
- Sadece architect görevler için tetikle
- Code/debug/ask modları: rapor yazılmaz
- Exception handling: rapor yazma hatasında görev proceed (don't fail)

---

### 3. Test: `tests/test_d190_mimir_rapor.py` (YENİ)

**3 test case**:

1. **test_architect_gorev_rapor_auto_yazilir**
   - Setup: architect görev + brief dosyası
   - Action: teslim_et() çağır
   - Assert: rapor dosyası yazıldı + pano'da not güncellenmiş

2. **test_code_gorev_rapor_yazilmaz**
   - Setup: code görev (mod="code")
   - Action: teslim_et()
   - Assert: rapor dosyası yazılmadı

3. **test_brief_yoksa_rapor_hala_yazilir**
   - Setup: architect görev, brief yok (talimat=None)
   - Action: teslim_et()
   - Assert: rapor yazıldı + "Brief bulunamadı" içeriyor

---

## Kurallar

- **D-190 Architect Hakkı**: Architect görev done → MIMIR rapor yazabilir (keine human intervention)
- **D-63 Architect Kapısı**: Sadece ihsan/utku architect mode atayabilir (kuralı ezmeyen)
- **D-60 Kanonik Ad Geçişi**: Rapor dosya adı template'i standart (TASK_ID_rapor_TARIH_AJAN)
- **D-88 Rapor Format**: Markdown, başlık + summary + bulgular bölümleri

---

## Teslim

- [ ] Kod yazıldı: mimir_rapor.py + trigger.py integration
- [ ] Test yazıldı + passed: test_d190_mimir_rapor.py (3/3)
- [ ] Regresyon: full test suite pass
- [ ] Rapor: ALTYAPI-MIMIR-RAPOR-OTOMASYONU-01_rapor_{TARIH}_mimar.md

---

## Tahmini Zaman

- Kod: 2h (MimirRaporYazici + entegrasyon)
- Test: 1.5h (3 test case + mock setup)
- Regresyon: 1h
- **Toplam: 4.5h**

---

## Notlar

- Brief dosyası yoksa rapor yine yazılır ("Brief bulunamadı" uyarısı)
- Rapor yazma hatasında görev done kalıyor (rapor yazması görev bloke etmesin)
- Review aşaması: MIMIR rapor → insan approve/reject (ayrı görev değil)
- Admin panel'de rapor çıkış noktası gösterilebilir (future: CUSTOMER-PANEL-RAPOR-02)
