file_path = r"C:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\WORKFLOW_OPTIMIZATION.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

new_sections = """

---

## 7. Darboğaz Listesi

Mevcut süreçteki ana darboğazlar ve etkileri:

| # | Darboğaz | Etki | Çözüm |
|---|---|---|---|
| 1 | Görev teslimi doğrudan `done` yapılması | Onaysız tamamlanma, denetim kaybı | `gorev_kutusu.py teslim` zorunlu, `done` YASAK |
| 2 | AST bekçi testi eksikliği | Yasak importlar (streamlit/auth) tenant paketine girebilir | `test_tenant_bekci.py` ile tarama zorunlu |
| 3 | Cache tazeliği testlerde tutarsız | Stale veri ile yanlış test sonuçları | Autouse fixture'da `_CACHE.clear()` |
| 4 | Dosya kilitleme kontrolü eksikliği | Paralel değişiklik çakışması | `gorev_ekle(dosyalar=[...])` ile otomatik kilit |
| 5 | Onay kuyruğu doluluk | Görevler onaysız kalabilir | `onay-bekleyen` periyodik kontrol; `onayla`/`reddet` |

---

## 8. Önerilen Akış

Her görev için zorunlu akış:

```
Tetik → Al → Çalış → Teslim → Onay → Done
```

Aşağıda adım adım detay:

| Adım | Komut | Açıklama |
|---|---|---|
| 1. Tetik | `gorev_at.py at --task-id X` veya otomatik | Görev panoya eklenir, kilit düşer |
| 2. Al | `gorev_kutusu.py al --ajan A --task-id X` | Durum: `aktif` |
| 3. Çalış | (ajen tarafından) | Görevi görerek implementasyon |
| 4. Teslim | `gorev_kutusu.py teslim --ajan A --task-id X --ozet "..."` | Durum: `review` (onay bekliyor) |
| 5. Onay | `gorev_kutusu.py onayla --task-id X --ben orkestrator` | Durum: `done`, kilitler düşer |
| 5b. Reddet | `gorev_kutusu.py reddet --task-id X --neden "..."` | Durum: `aktif` (düzeltme) |

---

## 9. Ölçüm KPI'ları

İş akışı performansını ölçen KPI'lar:

| # | KPI | Tanım | Hedef | Ölçüm Yeri |
|---|---|---|---|---|
| 1 | Ortalama teslim süresi | Görev `al` → `teslim` arası ortalama süre | ≤4 saat | `task_board.json` `baslangic`/`bitis` zamanları |
| 2 | Ret oranı | `reddetilen` / `toplam teslim` oranı | ≤20% | `onay-bekleyen` geçmişi |
| 3 | Onay süreci süresi | `teslim` → `onayla` arası ortalama süre | ≤2 saat | `decision_log.jsonl` zaman damgaları |
| 4 | Test geçer oranı | `pytest` geçen / toplam test oranı | ≥%99 | `python -m pytest tests/ -q` |
| 5 | Bekçi test % kapsamı | AST bekçi testleri ile ele geçen dosya oranı | %100 (tenant/health/aktarım modülleri) | `test_tenant_bekci.py`, `test_i18n_disa_aktar.py` |

**KPI Hesaplama Formülleri:**
- Ortalama teslim süresi = SUM(teslim_tarihi - al_tarihi) / COUNT(gorevler)
- Ret oranı = COUNT(ret_detilenler) / COUNT(teslimler) * 100
- Onay süreci süresi = SUM(onay_tarihi - teslim_tarihi) / COUNT(onaylananlar)

"""

lines = content.split("\n")
marker_index = -1
for i, line in enumerate(lines):
    if line.strip() == "---":
        j = i + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1
        if j < len(lines) and lines[j].strip().startswith("*Son"):
            marker_index = i
            break

if marker_index == -1:
    print("Marker not found!")
else:
    new_lines = lines[:marker_index] + [new_sections.strip()] + lines[marker_index:]
    new_content = "\n".join(new_lines)
    
    with open(file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
    
    print(f"Inserted at line {marker_index + 1}")
    print(f"New line count: {len(new_lines)}")
