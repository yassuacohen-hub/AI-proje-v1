# BRIEF - KILO - DOC-HIBRIT-01: Hibrit geçiş planı dosyasını repo içine yaz

Hazırlayan: roo (orkestratör)
Hedef ajan: kilo
Öncelik: P0
Bağımlılık: YOK.

---

## BÖLÜM 0 - SORUN

Ürün Sahibi, kilo'nun son çalışmasının (UI-CHART-01 hibrit geçiş planı / brief metni)
`docs/plans/UI-CHART-01_hibrit_gecis_plani.md` olarak kaydedildiğini bildirdi.

roo denetimi (2026-09-16 15:54, Europe/Istanbul):
- `docs/plans/` içeriği: yalnız `grafik_ve_chart_kutphanesi_arastirma.md` ve `UI-CHART-01_arastirma.md`
- Repo geneli arama (`hibrit_gecis`, `UI-CHART-01_hibrit`, "hibrit geçiş"): **0 sonuç**
- Üst dizin `C:\Huginn Data Projesi\` ve `.kilo/`: dosya yok
- `data/orchestrator/triggers/roo.jsonl`: yok

Sonuç: dosya **hiçbir yerde** yok. Büyük olasılıkla yanlış çalışma dizinine
(üst dizin) ya da hiç yazılmadı.

## BÖLÜM 1 - YAPILACAK (tek iş)

1. Hibrit geçiş planı metnini **tam yola** yaz:
   `C:\Huginn Data Projesi\Huginn Data Insights\docs\plans\UI-CHART-01_hibrit_gecis_plani.md`
   - Python ile: `open(Path(__file__).resolve().parents[..] / "docs/plans/...", "w", encoding="utf-8")`
   - **Yasak:** PowerShell `Out-File -Encoding utf8` / `Set-Content -Encoding utf8` (BOM yazar)
   - Türkçe karakterler bozulmamış olmalı; 0 bayt / NUL bayt teslim edilemez
2. Dosyanın başına şu meta bloğu koy:
   ```
   # UI-CHART-01 Hibrit Geçiş Planı
   Hazırlayan: kilo · Tarih: 2026-09-16 · Durum: taslak (roo sentezi bekliyor)
   ```
3. Teslim: `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id DOC-HIBRIT-01 --ozet "..."`
   - Özette dosyanın **mutlak yolu** ve **bayt boyutu** yazılacak (`dir` çıktısı).

## BÖLÜM 2 - KAPSAM DIŞI (dokunma)

- `app.py`, `web_dashboard/**`, `src/**` — kod değişikliği YOK
- Streamlit yeniden başlatma gerekmez (yalnız doküman)

## BÖLÜM 3 - PROJE SINIRI HATIRLATMASI (ZORUNLU)

Üst dizinde (`C:\Huginn Data Projesi\`) kilo'ya ait kalıntılar tespit edildi:
`fix_breadcrumb*.py`, `fix_extras*.py`, `fix_mvp_kul_02.py`, `insert_stcaption.py`,
`modify_topbar*.py`, `replace_app_functions.*`, `temp_script.py`, `update_and_submit*.py`, `dummy`.

Kural (AGENTS.md → Proje Sınırı): repo kökü dışına **hiçbir şey** yazılmaz.
Geçici script için `data/_tmp/` veya `_trash/` kullan; iş bitince sil.
Bu görevde üst dizine dokunma; temizlik ayrı görevle (ORCH-TEMIZLIK-02) yapılacak.

## BÖLÜM 4 - İLETİŞİM PROTOKOLÜ DÜZELTMESİ (ZORUNLU — Ürün Sahibi emri, 2026-09-16)

Kilo'nun yazdığı şu cümle **GEÇERSİZDİR** ve uygulanmayacaktır:

> "Roo dönüşünde decision_log.jsonl son satırını okuyacak — orada tüm kararlardan
> haberdar edecek. Eğer Roo 24 saat içinde onay vermezse, Faz 1 (ECharts prototype)
> otomatik başlar."

Neden geçersiz:
1. `data/orchestrator/decision_log.jsonl` **roo'nun karar defteridir**; kilo→roo
   haberleşme kanalı değildir. Kilo bu dosyaya yazamaz (AGENTS.md → Subagent Kuralları).
   Nitekim son 44 kaydın tamamı roo'ya aittir; kilo'nun "haberdarlık" notu orada yok.
2. Projede **"sessizlik = onay" / zaman aşımlı onay kuralı yoktur.** Onay yalnızca
   roo'nun açık `onayla` kararıyla verilir (AGENTS.md → ORCH-08). 24 saat geçmesi
   hiçbir işi başlatmaz.
3. ECharts **onaylı kütüphane değildir.** Onaylı chart kütüphanesi Plotly'dir
   (`web_dashboard/charts.py`, fallback'li). ECharts/Cytoscape yalnız senaryo bağlı
   araştırma maddesidir (`docs/plans/grafik_ve_chart_kutphanesi_arastirma.md`).
   "Faz 1 ECharts prototipi" roo onayı olmadan **başlamaz**; başlarsa teslim reddedilir
   ve kapsam dışı dosya değişikliği geri alınır.

Doğru kanal (tek yol):
| Adım | Komut / Yer |
|---|---|
| Postayı oku | `python scripts/gorev_kutusu.py bak --ajan kilo` |
| İşi al | `python scripts/gorev_kutusu.py al --ajan kilo --task-id <ID>` |
| Teslim | `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id <ID> --ozet "..."` → görev `review` |
| Roo'ya bilgi/öneri | Teslim özetine yaz **veya** `data/orchestrator/<ID>_rapor_<tarih>_kilo.md`; roo `onay-bekleyen` ile görür |
| Karar | Yalnız roo: `onayla` / `reddet --neden`. Kilo `decision_log.jsonl`'e yazmaz, roo adına karar üretmez |

Kilo bu bölümü okuduğunu DOC-HIBRIT-01 teslim özetinde tek satırla teyit eder:
`"BÖLÜM 4 okundu; otomatik başlama yok, ECharts onay bekliyor."`
