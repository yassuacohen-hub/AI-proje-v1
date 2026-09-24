# DOC-ADMIN-V9-KUTUCUK-24 — Brief (utku)

**Başlık:** [DOC] V9 §16.5 kutucuklarını düzelt → 6 madde (1s)
**Öncelik:** P2 · **Kit:** ADMIN-KİT (AGENTS.md D-196)
**Kilitli dosya:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — kapanista "Kapanan isler" bolumune task_id satiri yazilir (B-14).

## Neden
SSOT v2.6 §16.5 (Admin-Kit bağlı belge) V9 analiz dokümanında "6 madde" kutucuk formatı bozuk — madde işaretleri yanlış, boş satırlar fazla, metin kesik. KAHİN incelemesinde (2026-09-24) format düzeltmesi istendi.

## Doğrulanacak varsayım
- Dosya: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` satır ~1500-1600 civarında §16.5 bölümü var
- 6 madde listesi: her biri `- ` ile başlıyor, tek paragraf, boş satır yok
- Madde içerikleri V9 orijinal analizden korunuyor, sadece format düzeltiliyor

## Adımlar
1. SSOT dosyasını aç, §16.5 bölümü bul
2. 6 maddeyi temiz formatta yeniden yaz:
   - Her madde `- ` ile başlar
   - Tek satır paragraf (kesme yok)
   - Madde arası tek boş satır
   - Sondan sonra boş satır bırakılmaz
3. Dosyayı kaydet

## Kabul kriteri
- [ ] §16.5 altında tam 6 madde var, hepsi `- ` ile başlıyor
- [ ] Madde arası tek boş satır, fazladan boşluk yok
- [ ] Markdown lint (kodlama_denetim) temiz
- [ ] Hub'a kayıt yapıldı (B-14)

## Kurallar (ADMIN-KİT · D-196)
- Görev başında SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- Görev sonunda ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan utku --task-id DOC-ADMIN-V9-KUTUCUK-24 --ozet "<özet>"`

## Ilgili Nodlar
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]