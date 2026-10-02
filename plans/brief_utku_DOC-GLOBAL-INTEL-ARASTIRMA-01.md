# DOC-GLOBAL-INTEL-ARASTIRMA-01 — Brief (utku)

**Başlık:** [DOC] Faz 6 küresel istihbarat ağı kapsamını araştır → docs/FAZ6_GLOBAL_INTEL_KAPSAM.md (4s)
**Öncelik:** P3 · **Kit:** `ADMIN` (AGENTS.md D-196)
**Kilitli dosya:** `docs/FAZ6_GLOBAL_INTEL_KAPSAM.md`
**Bağımlılık:** `DOC-VENDOR-DD-ARASTIRMA-01`
**Hub:** `hubs/PLAN_STRATEGY_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Bu bir KOD görevi DEĞİL.** Şema, göç, tablo, Python — hepsi **kapsam dışı**. Çıktı tek markdown belgesi.
> **Bu aynı zamanda bir "YAPMAYIN" belgesi olabilir.** Faz 6'nın bugün yapılamaz olduğu sonucuna
> varırsan, bu **başarısızlık değil, doğru cevaptır** — yeter ki gerekçesi ölçümle yazılı olsun.

---

## Neden

Faz 6 yol haritasının **son** basamağı. SSOT'ta durumu ölçüldü:

| Kanıt | `dosya:satır` | Ne yazıyor |
|---|---|---|
| Faz 6'nın SSOT'taki tüm içeriği | `yedekler/Huginn Data Insights (HUGIns).txt:871-873` | `Faz 6` + `Global Corporate Intelligence Network` — **başka hiçbir şey yok** |
| Nihai Misyon (Faz 6'nın hedefi) | aynı dosya `875-885` | *"İnternet üzerindeki her şirket için; 'Kimdir?' 'Güvenilir midir?' 'Risk taşır mı?' sorularını saniyeler içinde cevaplayan, yapay zeka destekli küresel kurumsal istihbarat platformu oluşturmak."* |
| Bugünkü gerçek kapsam | `data/osb/` + `companies` tablosu | **yalnız Türkiye**, yalnız OSB firmaları |

**İki kelime arasındaki uçurum bu görevin konusu:** SSOT "küresel" diyor, elimizdeki veri
"Türkiye'deki OSB firmaları". Faz 6 = bu uçurumun köprüsü. Köprünün nasıl kurulacağı SSOT'ta yazılı değil.

Kod brifi yazsam tamamını uydurmuş olurdum — **D-260 ihlali**. Bu yüzden görev **araştırmadır**:
uçurumu ölç, köprü seçeneklerini listele, maliyetini tahmin et, **karar önerisi** getir.

**Neden `DOC-VENDOR-DD-ARASTIRMA-01`'e bağımlı:** Faz 5 belgesi "elimizde ne var" tablosunu çıkaracak.
Faz 6 o tablonun üzerine "bunu başka ülkeye nasıl taşırız" diye bakar. Önce envanter, sonra genişleme.

---

## Doğrulanacak varsayım

> Zorunlu bölüm (D-66). Aşağıdaki her madde **brif yazarken sabitlendi**. Tutmuyorsa **dur, chat'e yaz, uydurma.**

- `yedekler/Huginn Data Insights (HUGIns).txt` var ve ~1687 satır varsayıldı. Yoksa **dur**.
- Satır `871-873` Faz 6 başlığı, `875-885` nihai misyon, `11-17` 7 soru, `25-32` 8 kitle varsayıldı.
  **Satırları kendin aç ve gör** — verdiğim numaralara güvenme, teyit et (D-245).
- `docs/FAZ6_GLOBAL_INTEL_KAPSAM.md` diskte **YOK** varsayıldı. Varsa **dur**.
- `docs/FAZ5_VENDOR_DUE_DILIGENCE_KAPSAM.md` bu görev başladığında **VAR** varsayıldı (bağımlılık).
  Yoksa: chat'e yaz ve **yine de devam et** (D-65: iş durmaz), belgede "Faz 5 envanteri yoktu" notu düş.
- Bugünkü veri kapsamı **yalnız Türkiye** varsayıldı. Faz A'da bunu **ölçerek** teyit edeceksin.

---

## Faz A — Uçurumu ÖLÇ: bugün kaç ülke, kaç firma?

**Kök neden:** "Küresel" hedefi ile bugünkü kapsam arasındaki mesafeyi sayı olarak bilmeden
hiçbir genişleme planı dürüst olamaz.

**Yapılacak:**
1. OSB veri setini ölç — **mevcut kalıcı kapıyı kullan, yeni betik yazma (R1):**
   ```bash
   python scripts/osb_veri_denetim.py
   ```
   Çıktıdaki `toplam`, `tekil`, `kimliksiz`, `mukerrer` sayılarını **olduğu gibi** belgeye yaz.
2. Şemada ülke/ulus bilgisi tutan bir kolon var mı? **Ara, tahmin etme:**
   ```bash
   findstr /S /I /C:"country" /C:"ulke" /C:"nation" src\company_master\schema\migrations\*.sql
   ```
   Bulduğun satırları `dosya:satır` ile belgeye yaz. **Bulamazsan "ülke kolonu YOK" yaz** — bu çok
   önemli bir bulgudur, Faz 6'nın ilk engelidir.
3. Belgeye şu tabloyu doldur:

| Ölçüm | Değer | Nasıl ölçüldü |
|---|---|---|
| Veri setindeki toplam kayıt | ? | `osb_veri_denetim.py` çıktısı |
| Tekil firma | ? | aynı |
| Kapsanan ülke sayısı | ? | şema taraması |
| Şemada ülke kolonu | var / **yok** | `findstr` çıktısı |

**Kapı:** Bu tablodaki hiçbir hücre tahmin olamaz. Ölçemediğin hücreye `ölçülemedi: <sebep>` yaz (D-249).

---

## Faz B — "Küresel" ne demek: 3 ölçek tanımı

**Kök neden:** "Küresel" kelimesi tek başına plan değildir. Üç farklı şey olabilir ve maliyetleri
10 kat farklıdır. Ürün Sahibi'nin hangisini istediğini seçebilmesi için üçünü de tanımlaman gerekir.

**Yapılacak:** `## Üç Ölçek Tanımı` başlığı altında her biri için ayrı blok:

```
### Ölçek 1 — Türkiye derinleşmesi ("küresel değil ama sağlam")
- **Ne demek:** <sade Türkçe, 2 cümle>
- **Gereken yeni veri kaynağı:** <liste>
- **Gereken şema değişikliği:** <liste VEYA "yok">
- **Engel:** <somut engel>
- **7 sorudan kaçını cevaplar:** N/7

### Ölçek 2 — Komşu ülkeler (AB + bölge)
...aynı 5 alt madde...

### Ölçek 3 — Gerçek küresel (SSOT'un yazdığı hedef)
...aynı 5 alt madde...
```

**Kural:** "Gereken yeni veri kaynağı" satırına **gerçek, adı olan bir kaynak** yaz
(örn. "AB İşletme Sicili / BRIS"). Adını bilmiyorsan **"kaynak adı araştırılmadı"** yaz —
uydurma bir API adı yazmak D-260 ihlalidir.

---

## Faz C — Üç teknik engel, ölçümle

**Kök neden:** Genişleme planları teknik engellerde ölür, vizyonda değil. Engelleri önceden yaz.

**Yapılacak:** `## Teknik Engeller` başlığı, **en az 3** engel, her biri şu kalıpta:

```
### E1 — <engelin adı>
- **Nerede görünür:** `dosya:satır` (kodda/şemada gösterilebilir yer)
- **Neden engel:** <2 cümle>
- **Aşmanın yolu:** <somut öneri VEYA "yolu bilinmiyor">
```

Aramaya şuradan başla (bunlar **aday** engeller, teyit etmen gerekir):
- **Kimlik numarası:** Şema `vkn` (Türkiye vergi no) ile firma tekilleştiriyor. Başka ülkede VKN yok.
  Ölç: `findstr /S /I /C:"vkn" src\company_master\schema\migrations\*.sql`
- **Sektör kodu:** NACE Avrupa standardı; ABD `NAICS` kullanır. Ölç: `findstr /S /I /C:"nace" src\company_master\schema\migrations\*.sql`
- **Dil:** Firma adı normalleştirmesi Türkçe karakter varsayıyor olabilir.
  Ölç: `findstr /S /I /C:"maketrans" /C:"encoding" src\company_master\entity_resolution\*.py`

Her engel için **ölçüm komutunu çalıştır ve çıktıyı belgeye yaz.** Çalıştırmadığın komutun sonucunu yazmak yasaktır (D-266).

---

## Faz D — Karar önerisi: 3 yol + senin önerin

**Yapılacak:** `## Yol Önerileri` başlığı, 3 seçenek, biri `← ÖNERİM` işaretli:

| Yol | Ne yapar | Artısı | Eksisi | Ne zaman başlanmalı |
|---|---|---|---|---|
| A | Faz 6'yı **ertele**, Faz 1-4 bitene kadar dokunma | odak dağılmaz | hedef kağıtta kalır | — |
| B | Yalnız **şemayı hazırla** (ülke kolonu + kimlik türü alanı), veri sonra | ucuz, geri dönülmez karar vermez | boş kolon = D-249 riski | ? |
| C | Tam genişleme: harici küresel veri sağlayıcı | hedefe ulaşır | maliyet + hukuk | ? |

**Önerini işaretle ve 2 cümleyle gerekçelendir.**
**Not:** "A — ertele" seçeneğini önermek tamamen geçerlidir. Ürün Sahibi'ne *"bugün yapılamaz, sebebi şu"*
demek, yapılamaz bir planı güzel göstermekten değerlidir.

---

## Faz E — Öz-eleştiri

`## Öz-eleştiri` başlığı, **en az 1 madde.** Örnek kalıp:
*"Üç ölçeği teknik gözle tanımladım; hukuki engelleri (KVKK/GDPR sınır ötesi veri) ölçmedim, bu belgenin en zayıf yeri."*

---

## Kabul kriteri

- [ ] `docs/FAZ6_GLOBAL_INTEL_KAPSAM.md` oluşturuldu.
- [ ] **Faz A:** ölçüm tablosu 4 satır dolu; her hücre ya gerçek sayı ya `ölçülemedi: <sebep>`.
- [ ] **Faz A kapısı:** `osb_veri_denetim.py` **fiilen çalıştırıldı**, çıktısı belgeye kopyalandı.
- [ ] **Faz A kapısı:** şemada ülke kolonu arandı; sonuç ("var `dosya:satır`" / "yok") yazılı.
- [ ] **Faz B:** 3 ölçek, her birinde 5 alt madde dolu, "7 sorudan kaçını cevaplar" sayısı yazılı.
- [ ] **Faz C:** ≥ 3 engel, her birinde `dosya:satır` **veya** "kodda gösterilemedi" notu.
- [ ] **Faz C kapısı:** belgede yazılan her `findstr` çıktısı gerçekten çalıştırıldı (D-266).
- [ ] **Faz D:** 3 yol + 1 `← ÖNERİM` + gerekçe.
- [ ] **Faz E:** öz-eleştiri ≥ 1 madde.
- [ ] ≥ 2 Obsidyen wikilink `[[...]]` (D-218).
- [ ] `hubs/PLAN_STRATEGY_HUB.md` "Kapanan işler"e `DOC-GLOBAL-INTEL-ARASTIRMA-01` satırı (B-14).

---

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Kod yazmak YASAK.** Göç, tablo, modül, test üretilmez. Kod gerektiğini düşündüğün yeri
  belgede **"ayrı görev gerekir"** diye not et.
- **Geçici betik yazmak yasak (R1).** Ölçüm için `scripts/osb_veri_denetim.py` ve `findstr` yeter.
  Yeni ölçüm aracı gerekiyorsa chat'e yaz, kendin açma.
- **Çalıştırmadığın komutun sonucunu yazma (D-266).** Her sayı bir komut çıktısıdır.
- "Veri yok" ile "0" karıştırılmaz (D-249).
- **Teslimden önce** `hubs/PLAN_STRATEGY_HUB.md` "Kapanan işler" bölümüne satır yaz (B-14 kapısı).

---

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Aşağıdaki durumlarda **chat'e yazmak zorunludur**:

- SSOT satır numaraları tutmuyorsa → `ac` ile sorun aç, **uydurma, durma**.
- `docs/FAZ5_...md` yoksa → sorun aç, **yine de devam et** (D-65).
- Bir faz tıkandıysa → sorun aç, **sonraki faza geç**.
- @mention aldıysan → P0 5-10 dk, P1 10-15 dk, P2 15-30 dk içinde cevap **zorunlu**.

```bash
python scripts/ajan_chat.py ac utku DOC-GLOBAL-INTEL-ARASTIRMA-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id DOC-GLOBAL-INTEL-ARASTIRMA-01
python scripts/chat_gonder.py --to ihsan --type soru --task-id DOC-GLOBAL-INTEL-ARASTIRMA-01 --mesaj "<metin>"
```

---

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id DOC-GLOBAL-INTEL-ARASTIRMA-01 --ozet "<özet>"
```

Teslim özetinde **şu üç şey** olmak zorunda: ölçülen toplam firma sayısı · şemada ülke kolonu var mı ·
önerdiğin yol (A/B/C) ve tek cümle gerekçesi.

**Teslimden sonra DURMAK YASAK (D-312).** Posta + chat kontrolü zorunlu:

```bash
python scripts/gorev_kutusu.py bak --ajan utku      # posta: yeni gorev var mi?
python scripts/ajan_chat.py oku --son 10            # chat: cevap bekleyen mesaj var mi?
```

- Mesaj varsa → **cevapla**.
- Yeni görev varsa → `al` ile al, baştan başla.
- İkisi de boşsa → `basla --ajan utku` ile zinciri yeniden yokla.
- Döngü sonsuzdur: iş bitti demek "bekle" demek değildir.

---

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[hubs/PLAN_STRATEGY_HUB]]
- [[plans/brief_yasu_DOC-VENDOR-DD-ARASTIRMA-01]]
- [[plans/brief_yasu_VERI-ENTITY-GRAPH-01]]
