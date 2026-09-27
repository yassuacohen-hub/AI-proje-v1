# Brif — ORKESTRA-D65-ISDURMAZ-01

## Görev Özeti
D-65 "İş Durmaz" kuralı **fiilen işlemiyor**. Kural metin olarak [`AGENTS.md:167-175`](../AGENTS.md:167) içinde var,
ama hiçbir kod yolu onu uygulamıyor. Bu görev: ihlali ölç, kök nedeni belgele, uygulanabilir tek bir mekanizma öner.

## Kanıt (ürün sahibi teyit etti)
- Görevler `plan` durumunda günlerce bekliyor; ajan `al` çalıştırmadıkça hiçbir şey ilerlemiyor.
- Pano taraması: 22 açık görevin 10'u brief alanı boş bırakılmış kayıtlardı (D-66 kapısı öncesi dönem).
- `blocked` durumundaki görevler için bypass/eskalasyon tetikleyen kod yok — `pano_denetim.py` sadece rapor veriyor.

## Yapılacaklar
1. `blocked` + `plan` durumunda **son hareketi N saatten eski** görevleri listeleyen ölçüm çıkar
   (`pano_denetim._son_hareket` zaten var, yeniden yazma).
2. D-65'in metinsel vaadi ile mevcut davranış arasındaki farkı tablola.
3. **Tek** mekanizma öner (en fazla biri seçilecek):
   - (a) `pano_denetim`'e bayat-görev exit kodu + eskalasyon satırı,
   - (b) `gorev_kutusu bakim` içinde otomatik `blocked → plan` düşürme,
   - (c) orkestratör oturum açılışında zorunlu bayat-görev raporu (D-168 ile aynı yere takılır).
4. Öneriyi KAHİN kararı taslağı olarak yaz (D-NN formatı, henüz numara verme).

## Çıktı
`data/orchestrator/ORKESTRA-D65-ISDURMAZ-01_rapor_<tarih>_ihsan.md`

## Kurallar
- D-48 token verimliliği: yeni script yazma, mevcut `pano_denetim.py` fonksiyonlarını kullan.
- D-86: Windows cmd.exe, geçici script `data/_tmp/` altına.
- **Kod değişikliği bu görevin kapsamı değil.** Ölçüm + öneri. Uygulama ayrı görev olacak.

## Süre Tahmini
3s

## Ilgili Nodlar
- [[AGENTS]]
- [[data/orchestrator/SPRINT_KAPANIS_2026-09-23]]
