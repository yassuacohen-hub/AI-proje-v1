# AGENTS-MERGE-UU — Brif

**Tarih:** 2026-09-23
**Sahip:** İHSAN (Orkestratör/Yönetim)
**Öncelik:** P0
**Mod:** code

## Amaç

Kök `AGENTS.md` (n8n-as-code bloğu + kısaltılmış ajan kuralları) ile vault `Huginn Data Insights/AGENTS.md` (581 satır tam kural seti, D-48..D-186) arasındaki kopukluğu gider. İki dosya birbirinden habersiz; kök dosya vault kurallarının küçük bir özetini tutuyor ve tekrar ediyor.

## Kapsam

- Kök `AGENTS.md`: n8n-as-code üretim bloğu (`<!-- n8n-as-code-start -->` … `end`) **dokunulmaz** (üretilen içerik; `npx n8nac update-ai` yeniden yazar).
- n8n bloğu sonrası Türkçe kural özeti: tekrar yerine vault SSOT'a **yönlendirme** (pointer) olacak.
- Vault `AGENTS.md`: tek doğruluk kaynağı (SSOT); yeni karar buraya yazılır.
- KAHİN yeni kuralı (2026-09-23): **önce panoya yazılır, sonra tetik atılır** → D-188 olarak vault AGENTS.md'ye eklenir.

## Kabul Kriterleri

1. Kök `AGENTS.md` içinde n8n bloğu bozulmamış (start/end işaretleri yerinde).
2. Kök dosyadaki mükerrer kural metinleri tek pointer bölümüne indirilmiş.
3. Vault `AGENTS.md` içinde D-188 (pano-önce-tetik) kuralı yazılı.
4. Çatışma işaretleyicisi (`<<<<<<<`, `=======`, `>>>>>>>`) hiçbir dosyada yok.
5. UTF-8, BOM yok.

## Kısıt

- Commit yok (KAHİN onayı olmadan).
- Vault kural metinleri silinmez; yalnız kökteki kopya sadeleşir.
