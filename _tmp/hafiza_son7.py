# -*- coding: utf-8 -*-
"""SON-7: GUI model kutusunun tek satir gosterme sebebi = HESAP PLANI (free).
Idempotent; 400 satir tavani (D-219) kontrol edilir."""
from pathlib import Path

HEDEF = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\ihsan_project_context.md")
ÇAPA = "- **Tuzak (yeni, kalıcı): Windows'ta `.vbs`"

KAYIT = """- **SON-7 (2026-10-20 ~22:00 — "SAĞ ALTTA MODEL SEÇİLEMİYOR"UN KESİN CEVABI: HESAP PLANI, AYAR DEĞİL):** PO ısrarla "seçim alanı yok" dedi; 3 tur "tıkla" yönlendirmem BOŞAYÁ çıktı (öz-eleştiri aşağıda). **Ölçülen zincir:** (a) `auth.json → id_token → https://api.openai.com/auth.chatgpt_plan_type = free` → GUI'nin model listesi OpenAI hesabından geliyor, ÜCRETSİZ planda arayüz **tek satır** gösteriyor ("5.6 Luna Sınırlı"), liste açılmıyor. Bu, config/alias/mcp ile AÇILMAZ — OpenAI tarafı. (b) AYRI bir kusur: etiket `Özel` görünüyordu çünkü `config.toml model="cx/gpt-5.6-luna"` GUI kataloğundaki 11 slug arasında YOK; GUI tanımadığı adı "Özel" diye etiketliyor. **Çözüm (kuruldu+doğrulandı):** portföy `cx/…` HAM id'leri yerine GUI'nin tanıdığı **takma adları** yazıyor (`gpt-5.6-luna`, `gpt-5.6-terra`, `gpt-5.5`, `glm-5.3`, `qwen3.8-flash-next`) → etiket doğru görünür VE 9Router takma adından canlı çalışır (`codex -p guclu` → cevap OK). (c) GUI'ye bağımlı olmayan yol teslim edildi: `scripts/codex_degistir.bat <profil>` = model değiştirir + `taskkill ChatGPT.exe` + yeniden başlatır (exe yolu ölçüldü: `C:\\Program Files\\WindowsApps\\OpenAI.Codex_26.1013.4894.0_x64__2p2nqsd0c76g0\\app\\ChatGPT.exe`); masaüstü `gereksiz\\` klasörüne kopyalandı. **KURAL (kalıcı): GUI'den model seçme özelliği bu makinede YOK; model yalnız `codex_model_sec.py <profil>` veya `codex_degistir.bat` ile değişir. Sahaya "sağ alttan seç" deme — önce `chatgpt_plan_type` ölç.** Ayrıca `models_cache.json`ı elle beslemek işe yaramaz (kod kanıtı, D-… önceki kayıt) ve `models refresh timed out` hatası zararsız gürültü.
"""

metin = HEDEF.read_text(encoding="utf-8")
if "SON-7 (2026-10-20" in metin:
    print("SON-7 zaten var — dokunulmadı")
elif ÇAPA not in metin:
    raise SystemExit("ÇAPA yok, elle bak")
else:
    yeni = metin.replace(ÇAPA, KAYIT + ÇAPA, 1)
    satir = yeni.count("\n") + 1
    if satir > 420:
        raise SystemExit(f"UYARI: dosya {satir} satira ulaştı (D-219 tavani 400) — eskileri kisalt")
    HEDEF.write_text(yeni, encoding="utf-8")
    print("EKLENDI · satir:", satir)
