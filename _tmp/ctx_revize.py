"""ihsan_project_context.md revize: eski KALDIĞIM YER bloklarını arşive taşı, panel/hakem durumu + tuzaklar ekle."""
import re
from pathlib import Path

ROOT = Path(r"c:/Huginn Data Projesi/Huginn Data Insights")
CTX = ROOT / "ihsan_project_context.md"
ARS = ROOT / "archive" / "ihsan_context_202610.md"

L = CTX.read_text(encoding="utf-8").split("\n")


def idx(pred, start=0):
    for i in range(start, len(L)):
        if pred(L[i]):
            return i
    raise SystemExit("bulunamadi")


i_kal = idx(lambda s: s.startswith("## KALDIĞIM YER"))
i_tuz = idx(lambda s: s.startswith("## Tuzaklar"))
i_oz = idx(lambda s: s.startswith("## Öz-eleştiri"))
i_son = idx(lambda s: s.startswith("## KALDIGIM YER — 2026-10-17"))

eski_kal = L[i_kal:i_tuz]
eski_son = L[i_son:]

YENI_KAL = """## KALDIĞIM YER (D-219: tek blok, üzerine yazılır)

**KONUM (2026-10-22 05:30 TR) — MÜŞTERİ PANELİ V12 HAKEM TURU KAPANDI, PO KARARI BEKLENEN: V12 İNŞA ONAYI.**

| Konu | Durum | Dosya / kanıt |
|---|---|---|
| Wireframe | V11B_TURUNCU (`#FF5A1F`, Inter, antrasit) | `docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html` |
| Hakem turu | 6 hakem (nur nisa salih utku yasu bilo); yasu GEÇERSİZ, kapsamı nur'a verildi; nisa 1 gün izinli | `data/orchestrator/hakem_v12/*.md` |
| Derleme + PO kararları | Q1–Q8 kesin (Q3 radar canlı ~1200 ms tek tur, Q4 navGir canlı sonrası) | `docs/MUSTERI_PANEL_HAKEM_DERLEME_V12.md` §5.1 |
| Kod | DONUK (D-420); inşa PO onayı sonrası | `frontend-web/components/panel/*` dokunma |
| Sıradaki | utku briefleri revize → sıra seç → dağıt (Kahn kökü: K1/K3 düzeltmesi) | `plans/brief_utku_*` |

**Karar özeti:** çizgi+nokta (dalga yok) · KPI sayaç 600 ms · radar sonsuz döngü yok · süre bütçesi widget ≤600 / sayfa ≤1000 (radar istisna 1200) · Inter+JetBrains Mono self-host · `onclick`→`addEventListener` (üretimde) · K1/K3 ihlali V12 ilk iş.

**Açık engeller:**
- `MAIL-SAGLAYICI-TESTI-01` (bilo) review'da BEKLİYOR: `web_app.py` 2683 ve 2770'te konu satırı `Huginn â€” …` (mojibake, doğrulandı). Kod donuk → düzeltme PO onayı + dondurma kalkınca. Onaylama.
- 4 yasu + 1 ihsan tetik postada (TETIK: ihsan=1 salih=1 yasu=4).
- İki repo/UU çatışmaları (aşağı Tuzaklar).

**Yeni oturum ilk komutlar:** `python scripts/gorev_kutusu.py nobet --ajan ihsan` · `python scripts/gorev_kutusu.py ozet` · `python scripts/ajan_chat.py ozet --durum acik` · oku: bu dosya, DERLEME §5.1, `ihsan_BASLANGIC_PROMPT.md`.

Eski KONUM blokları (2026-10-04…10-17, SON-3…SON-15 model seçimi) → `archive/ihsan_context_202610.md`.
""".split("\n")

TUZAK_SATIRLARI = """| Ajan raporu şablon doldurmuş (yasu hakem, ilk utku/salih/nisa/bilo) | Brife "komut+çıktı yoksa geçersiz" yoktu; ajan okumadan yazar | Her rapor: komut+çıktı veya dosya:satır şart. Yoksa sil, scope'u başkasına ver. Brife satırı baştan koy |
| Ajan yanlış yola yazdı (utku üst dizine hakem dosyası) | Çalışma dizini workspace kökü ≠ `Huginn Data Insights/` | Teslimde `git status` ile yol kontrol et; yanlışı kopyala-sil, brife tam yol yaz |
| Körleme bozuldu (PO mesajı hakemler arası taşıdı) | 6 hakem paralel, PO tek pencereden dağıttı | Sonuçları saklayıp en son aç; uyum ≠ bağımsızlık, güveni artırma |
| Ölçmeden yazdığım iddia yanlış çıktı ("26 menü" gerçek 19–20; "turuncu sarıya benzer" ΔE ile çürüdü) | DEMİR KURAL D-362 çiğnendi | Sayı yazmadan önce `search_files`/ölçüm; yoksa "ölçülmedi" yaz |
| `web_app.py` mail konu satırları `â€”` | UTF-8 dosya cp1252 gibi okunup tekrar yazılmış | Kod donuk (D-420). Dondurma kalkınca 2683/2770 + 2 satır onar; dosyayı tekrar yazan araçta encoding'i `utf-8` sabitle |
| `git pull --rebase --autostash` sonrası UU (AGENT_SYNC, gorun_panosu, bulgu_defteri, chat/messages.jsonl, ajan-chat.jsonl, onay_kuyrugu.json) | Çok ajan aynı dosyaya yazar; 38 stash birikmiş | `git checkout HEAD -- <dosya>`; stash'leri temizlemeden `stash pop` yapma |
| Commit mesajına `D-NNN` yazınca hook red | `karar_no` mandalı | Mesajda D-numarası kullanma |
| `%WT%/` çöp klasörleri repoda | Windows `%WT%` env genişlemeyen komut | Silme (ajan işi, KOK-TEMIZLIK); yeni çalıştırmada `set` ile değişkeni önce tanımla |
| Kilit beni `yasu` sanıyor | git `user.name=Yasua` | Her git/gorev komutu: `set HUGINN_AJAN=ihsan&& ...` |
| `onayla` Notion 400 uyarısı basıyor | Notion sync şeması | Zararsız; görev `done` olduysa devam |""".split("\n")

OZ = """### 2026-10-22 — Panel V12 hakem turu (ihsan, KALICI)
| Hata | Daha iyisi |
|---|---|
| Q2 (900 ms) ile Q5 (widget ≤600) çelişkisini görmeden "A" önerdim | Karar paketinde tüm öneriler çapraz tutarlılık tablosundan geçsin |
| 6 hakemi tek PO mesajıyla dağıttım; körleme bozuldu | Hakem başına ayrı pencere veya sonuçları sonda aç |
| yasu'nun sahte raporunu geç fark ettim | Teslimde ilk iş: komut+çıktı var mı? Yoksa onaylama |
| "26 menü", "turuncu sarıya benzer" ölçüsüzdü | Ölçüm önce, yazı sonra (D-362) |
| Context dosyası 3 haftadır panel işini içermiyordu | Her büyük tur sonu KONUM bloğu güncelle |
""".split("\n")

# yeni dosya
out = L[:i_kal] + YENI_KAL + [""] + L[i_tuz:i_oz]
# tuzak tablosunun son satırı
i_t0 = out.index(next(s for s in out if s.startswith("## Tuzaklar")))
j = i_t0 + 1
while j < len(out) and not out[j].startswith("|"):
    j += 1
while j < len(out) and out[j].startswith("|"):
    j += 1
out = out[:j] + TUZAK_SATIRLARI + out[j:]
# öz-eleştiri başı
out = out + [L[i_oz], ""] + OZ + L[i_oz + 1 : i_son]
out = [s for s in out]
# son blok arşive; Ilgili Nodlar zaten i_son'dan önce
txt = "\n".join(out).rstrip() + "\n"

# header
txt = re.sub(r"(Tarih[^:\n]*:\s*)[^\n]*", r"\g<1>2026-10-22 05:30 TR", txt, count=1)
txt = re.sub(r"(Oturum Başlığı[^:\n]*:\s*)[^\n]*", r"\g<1>MÜŞTERİ PANELİ V12 HAKEM TURU KAPANDI", txt, count=1)

ARS.parent.mkdir(exist_ok=True)
with ARS.open("a", encoding="utf-8") as f:
    f.write("\n# ihsan context arşivi — 2026-10-22 taşıması\n\n")
    f.write("\n".join(eski_kal))
    f.write("\n\n")
    f.write("\n".join(eski_son))
    f.write("\n")
CTX.write_text(txt, encoding="utf-8")
print("satir:", txt.count("\n"), "arsiv:", ARS.exists())
