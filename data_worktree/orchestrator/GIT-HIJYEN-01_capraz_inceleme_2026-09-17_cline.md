# GIT-HIJYEN-01 — Çapraz İnceleme (cline, 2026-09-17)

**İncelenen:** kilo'nun GIT-HIJYEN-01 teslimi (panoda `review`)
**Karar önerisi: KABUL** — brifin ana kabul kriteri sağlanmış, kapsam dışı mantık değişikliği yok.

## Doğrulama (komut + ham çıktı)
```
python -X utf8 scripts/kodlama_denetim.py --kapsam kod
→ "temiz: kodlama ihlali yok / allowlist dışı ihlal yok"  EXIT=0  ✓ (brif ana kriter)

.gitattributes: BOM yok (önceden efbbbf vardı — kilo strip etmiş, raporda açıkça yazılmış ✓)
İçerik: "* text=auto eol=lf" + tür bazlı encoding=utf-8 kuralları mevcut ✓
Önceki tarama notum (SEC-AUTH-01 öncesi): 153 dosya crlf_karisik → şimdi 0 (düzeltme gerçek ✓)
```

## Küçük notlar (blokaj değil)
1. **Rapor içi sayı tutarsızlığı:** "970 satır trailing whitespace temizlendi" vs kapsamda "87 WS"; "Tam suite: 3791 passed, 4 failed" — o anki gerçek sayı bendeki ölçümle 3829 civarıydı. Kilinin "4 failed (pre-existing)" teşhisi doğruydu (o an admin_quality kırığıydı) ve bugün süit **3843 passed / 0 failed** — sorun kapanmış durumda.
2. **`src/company_master/api/core/normalize.py` untracked:** kilo mojibake düzeltmesini "normalize.py'de duzeltildi" yazmış; dosya (ve tüm `src/company_master/api/` altı) git'te **hiç versiyonlanmamış** (`?? src/company_master/api/core/`). Düzeltme gerçek ama roo commit aşamasında bu klasörü eklemeli — aksi halde "düzeltildi" denilen dosya repoda olmayacak.
3. **Geçici scriptler kökte kaldı:** `fix_encoding.py`, `fix_encoding2.py`, `fix_final.py` (?? durumda). roo'nun ELESTIRI-01 listesindeki "kök dizinde 18+ geçici script" maddesini besliyor — temizlik görevine eklensin.
4. **Ortak sorun (yeni girdi):** `data/dummy/firmalar.jsonl` test koşularında büyüyor — her tam süitte "Test Firma" kayıtları kalıcı olarak ekleniyor (bugün +24 satır, 06:33→20:26 damgaları). Test izolasyon eksikliği; dummy veri testleri tmp_path'e yazmalı. Ayrı küçük görev önerisi.
5. `test_write.txt` kök silinmiş (D) — test artifact, sorun değil.

**Sonuç:** GIT-HIJYEN-01 kabulü önerilir; madde 2 (untracked api/core) roo commit listesine alınsın, madde 3-4 panoya küçük iş olarak düşsün.
