# -*- coding: utf-8 -*-
"""SON-12: MODEL_SECIMI_KILAVUZU.md kanoniklesti + D-423 karari + amac etiketi.
Tavan 700; asarsa YAZMAZ."""
from pathlib import Path

HEDEF = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\ihsan_project_context.md")
TAVAN = 700

KAYIT = """- **SON-12 (2026-10-21 ~00:20 — MODEL SEÇİMİ BİLGİSİ KANONİKLEŞTİRİLDİ: `MODEL_SECIMI_KILAVUZU.md` + D-423):** PO: "Codex ve Claude Code için yaptığın tüm çalışmayı guide olarak kaydet ve belgelendir, eski belgelere linkle bağla, gelecekte yeniden ayar yapmak istediğimde bu belgelerden destek alınsın; bilgiden kanonikleşsin; ne nasıl yapılıyor, tuzaklarını yaz". **TESLİM:** `Huginn Data Insights/MODEL_SECIMI_KILAVUZU.md` — 9 bölüm: (1) ürün→dosya eşleştirmesi (Codex CLI/Desktop = `~/.codex/config.toml`; Claude Code = `~/.claude/settings.json`; **Claude Desktop = `%LOCALAPPDATA%\Claude-3p\configLibrary\<appliedId>.json` → `inferenceModels`**), (2) dosya adresleri + `inferenceModels` şeması (`name`/`labelOverride`/`anthropicFamilyTier`; **liste doluysa keşif atlanır** → tek satır gören kişi tek model görür), (3) araç envanteri (codex_model_sec/codex_degistir/codex_gui_takma_ad · claude_model_sec · **claude_kutu_doldur** `--durum/--geri/--yeniden-olc` · claude_alias_gorunur `--duzelt` · claude_ham_govde · claude_kutu_aday_test · claude_tasarim_aday · claude_kutuya_evren), (4) önek sözlüğü (cc/ cx/ cl/=**402 bakiye** kc/ bzl/=**60 istek-gün** oc/ · `_next` · combo), (5) etiket okuma kılavuzu, (6) **12 ölçülmüş tuzak**, (7) yeni model ekleme 5 adım tarifi, (8) şu anki 18 modellik kutu tablosu, (9) SON-8…11 karar bağlantıları. **BAĞLANTILAR (çift yönlü):** `AGENTS.md` → yeni "Kanonik Kılavuzlar" düğümü + **D-423** kararı (model/kanal/gateway işinde ilk okunacak belge; yeni tuzak sohbette değil BELGEYE satır olur) · `hubs/TOOLS_SCRIPTS_HUB` · `hubs/TECHNICAL_DOCS_HUB`. **AMAÇ ETİKETİ (PO: "ne için kullanacağım görünsün — kod/tasarım/derin düşünme"):** hız kaldırıldı; `tek_test()` tek soruyla modelin ürettiği KOD/HTML/thinking işaretlerini okuyup `KOD / TASARIM / DERİN DÜŞÜNME / ÇOK AMAÇLI / GENEL` yazıyor → **uydurma etiket yok, ölçüm var**. Kota tasarımı: amaç önbelleği `scripts/claude_kutu_amac.json` (17 ölçülmüş değer yazıldı); önbellekteki modelde 400 token'lık amaç sorusu **sorulmaz**, 64 token'lık kapı kontrolü yapılır → ikinci koşu kota harcamaz (ölçüldü: 18/18 kutu korundu). **İki kendi hatam bu turda yakalandı:** (a) önbellek YAZIM satırı refactor'da düşmüştü → her koşul kota yakardı, geri eklendi; (b) diff işaretini `<<<<<<<<<<<<<<` diye yazıp aracı patlattım → format düzeltildi. **Not:** Claude Desktop hâlâ kapan-aç bekliyor; PO ekranında 18 model görünmeli.
"""

metin = HEDEF.read_text(encoding="utf-8")
if "SON-12 (2026-10-21" in metin:
    print("SON-12 zaten var")
    raise SystemExit(0)
satirlar = metin.splitlines()
for i, s in enumerate(satirlar):
    if s.startswith("- **SON-11 (2026-10-21"):
        satirlar.insert(i + 1, KAYIT.rstrip("\n"))
        break
else:
    satirlar.insert(0, KAYIT.rstrip("\n"))
son = "\n".join(satirlar) + "\n"
sayi = son.count("\n")
if sayi > TAVAN:
    raise SystemExit(f"YAZILMADI: {sayi} > {TAVAN}")
HEDEF.write_text(son, encoding="utf-8")
print(f"YAZILDI · satir: {sayi}/{TAVAN}")
