"""6 hakem brifi üretir (MUSTERI-PANEL-HAKEM-V12-<ajan>-01). Tek seferlik; commit'e girmez."""
from pathlib import Path

KOK = Path(r"c:/Huginn Data Projesi/Huginn Data Insights")
ODAK = {
    "nur": ("6.1", "doğruluk ve izlenebilirlik"),
    "nisa": ("6.2", "renk, tipografi, erişilebilirlik ölçümü"),
    "salih": ("6.3", "UX ve geçmiş denetim"),
    "utku": ("6.4", "kod, taşıma, bakım"),
    "yasu": ("6.5", "güvenlik, KVKK, dış bağımlılık"),
    "bilo": ("6.6", "iş modeli ve marka"),
}

SABLON = """# {tid} — Brief ({ajan})

**Başlık:** [MUSTERI-PANEL] V11B_TURUNCU hakem değerlendirmesi — {odak} ekseni (~1 oturum)
**Öncelik:** P1 · **Kit:** `MUSTERI-PANEL` (AGENTS.md D-196)
**Kilitli dosya:** `data/orchestrator/hakem_v12/{ajan}.md` (yalnız bu dosya; başka dosyaya dokunma)
**Hub:** `hubs/MUSTERI_PANELI_HUB.md` — ZORUNLU (B-14). Kapanınca "Kapanan işler" bölümüne yaz.
**Skill:** `web-design, better-ui, doubt-driven-development, verification-before-completion` — ZORUNLU (D-383 · D-407). İşe başlamadan SKILL.md oku.
**Dil (D-407):** PO'ya ve ajana dönük her satır TÜRKÇE.

> **Tek brif kuralı (D-217):** tek görev = tek brif; fazlar aşağıda.

## Neden
PO onayı (22.10 03:50 TR): "hakem yapalım, detayları verirsin, hakemlere en son kararımız bu oturum oldu hepsine baksınlar". Panel tasarımı (wireframe tasarımı `docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html`) yazarı ihsan olan kararlara dayanıyor. Yazar kendini yargılayamaz; 6 bağımsız hakem eksenine göre oy verir. Süreç: `docs/MUSTERI_PANEL_HAKEM_HEYETI_V12.md` §3–§5, `docs/MUSTERI_PANEL_HAKEM_SORULARI_V12B.md` §4–§6. Tasarım UX/arayüz işidir, kod yazılmaz (D-420).

## Doğrulanacak varsayım
- `docs/MUSTERI_PANEL_WIREFRAME_V11B_TURUNCU.html` mevcut (commit `50fc414a`). Yoksa **dur**, sorun aç.
- `docs/MUSTERI_PANEL_HAKEM_SORULARI_V12B.md` §7.1 "PO son kararları" mevcut (commit `47cab929`). Yoksa **dur**, sorun aç, uydurma.
- Kendi özel soruların: V12B §{bolum} (6×10 özel soru, {ajan}). Farklıysa **dur**, sorun aç.
- Depo: `Huginn Data Insights`, branch `chore/monorepo-merge`, çakışma işareti yok. Farklıysa chat'e `git status` yapıştır.

## Faz A — Tur 0 (oy vermeden ÖNCE, körleme)
1. `docs/MUSTERI_PANEL_HAKEM_HEYETI_V12.md` §2 okuma listesini oku; V12B §7.1 (PO son kararları) = **son durum**, yeniden oylanmaz. Kanıtlı itiraz varsa Kova C'ye yaz.
2. V11B_TURUNCU html'i tarayıcıda aç; her menü satırını ve her popup'ı tıkla. Görsel doğrulamayı ihsan yapmadı (V12B §7.1 notu) — bulgun varsa bu senin işin.
3. Diğer hakemlerin çıktısına BAKMA (herd protokolü, V12B §5). Kendi oyunu önce dosyaya yaz.

## Faz B — Oy ve kanıt
1. V12 §4 soru seti + V12B §4 "Çekirdek 12" + V12B §{bolum} senin 10 özel sorun: her soruya A / B / C / PO'YA BIRAK + kanıt (`dosya:satır` veya komut+çıktı) + tek cümle.
2. Kova etiketi: A ölçüm / B müşteri verisi / C PO kararı. Rakamı olmayan = "ölçülmedi".
3. ihsan'ı yanlışlama: en az 1 arama (bulgu varsa yaz, yoksa "aranan: X, bulunan: yok").
4. Çıktı: `data/orchestrator/hakem_v12/{ajan}.md` — tablo + tek sayfa; dolgu yok.

## Kabul kriteri
- [ ] **Skill beyanı (D-401):** teslim kanıtına "okunan skill: X, uygulanan madde: Y" satırı.
- [ ] `data/orchestrator/hakem_v12/{ajan}.md` mevcut; Çekirdek 12 + 10 özel soru cevaplı.
- [ ] Her oy satırı kanıtlı (D-395); kanıtsız satır yok.
- [ ] En az 1 ihsan yanlışlama araması.
- [ ] Kod yazılmadı (D-420).

## Kurallar (ADMIN-KİT · D-196)
- Görev başında SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`.
- Pano yazımı ihsan'a aittir (D-77); sen yalnız `gorev_kutusu.py teslim` kullan.
- Commit yalnız kendi dosyan (pathspec). Chat/teslim = commit + push (D-371).
- Yeni bağımlılık ekleme.

## Ajan chat zorunlu (D-210 · D-217)
- Varsayım tutmuyorsa `ac` ile sorun aç, uydurma.
- Faz tıkandıysa sorun aç, sonraki faza geç.
- @mention'a P1 10–15 dk içinde cevap.

```bash
python scripts/ajan_chat.py ac {ajan} {tid} "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id {tid}
python scripts/chat_gonder.py --to ihsan --type hata --task-id {tid} --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan {ajan} --task-id {tid} --ozet "<özet>"
python scripts/gorev_kutusu.py nobet --ajan {ajan}
```

## Rapor biçimi (D-407)
**1. SIRADAKİ ADIM:** tek cümle.
**2. STRATEJİK ADIM:** tek cümle.
**3. YAPILMASI GEREKENLER:** en fazla 3 madde, kime + ne.

## Öz-eleştiri ve hafıza (D-406)
- [ ] Öz-eleştiri satırı yazıldı + `data/orchestrator/hafiza/dersler_{ajan}.md`'ye tek satır ders işlendi.

## Ilgili Nodlar
- [[Huginn Data Insights/docs/MUSTERI_PANEL_HAKEM_HEYETI_V12]]
- [[Huginn Data Insights/docs/MUSTERI_PANEL_HAKEM_SORULARI_V12B]]
- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
"""

for ajan, (bolum, odak) in ODAK.items():
    tid = f"MUSTERI-PANEL-HAKEM-V12-{ajan}-01"
    p = KOK / "plans" / f"brief_{ajan}_{tid}.md"
    p.write_text(SABLON.format(tid=tid, ajan=ajan, odak=odak, bolum=bolum), encoding="utf-8")
    print("yazildi", p.name)
(KOK / "data/orchestrator/hakem_v12").mkdir(parents=True, exist_ok=True)
