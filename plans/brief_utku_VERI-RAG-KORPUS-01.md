# VERI-RAG-KORPUS-01 — Brief (utku)

**Başlık:** [VERI] Firma kayıtlarını RAG korpusuna çevir ve indeksle (3 saat)
**Öncelik:** P1 · **Kit:** `VERI-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/vector/service.py`
**Bağımlılık:** `ALTYAPI-RAG-EMBEDDER-01`
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

## Neden

Mimir'in cevap verebilmesi için firma kayıtlarının **aranabilir metin** hâline gelmesi gerekiyor. Şu an veritabanında satırlar var, vektör indeksinde karşılığı yok. Bu yüzden `<BAGLAM>` bloğu üretilemiyor ve Mimir hiçbir soruya cevap veremiyor.

Bu iş veri **yazmaz** — sadece var olan firma satırlarını okuyup metin + vektöre çevirir. Yani veri kirlenmesi riski yoktur; tersine, eksik alanları raporlar.

**Kritik kısıt (D-247):** Korpusa kişisel veri alanı **girmeyecek**. Ad-soyad, T.C. kimlik numarası, telefon, e-posta, ev adresi korpus metnine yazılmaz. Bu alanları embed etmek, maskeleme kapısını baypas etmek demektir — maskelenmiş görünür ama vektörde durur.

## Doğrulanacak varsayım

| # | Varsayım | Nasıl ölçülür | Yanlışsa |
|---|---|---|---|
| 1 | Firma başına anlamlı metin üretilebilir kadar alan dolu | 50 rastgele firmanın üretilen metin uzunluğunu ölç; **ortanca** değeri yazdır | Metin çok kısaysa (<80 karakter) korpus işe yaramaz → chat'e sorun aç, İhsan'a dön |
| 2 | Kişisel veri alanı korpusa sızmıyor | Üretilen 50 metinde telefon/e-posta/TCKN **desen taraması** → 0 eşleşme | Sızıntı varsa DUR, önce alan listesini daralt |
| 3 | Chunk'lama gerekli | Metinlerin kaç tanesi 200 karakteri geçiyor? | Hiçbiri geçmiyorsa `chunk_metin` çağrısı YAGNI — tek parça embed et |

**Payda yaz (D-260):** "8.987 kayıt" sayısı kayıt sayısıdır, firma sayısı değildir. Kaç **tekil firma** indekslendiğini ayrı yaz.

## Adımlar

1. **Ölç önce:** 50 rastgele firma için metin üret, üç varsayımı da ölç. Sonuçları yazdır. Varsayım 2 düşerse DUR.
2. `vector/service.py` içinde firma → metin dönüştürücüsünü kur. İzinli alanlar **beyaz liste** olacak (siyah liste değil — yeni kolon eklenince sızar):
   `firma_adı · nace_kodu + açılımı · nace_kaynağı · bölge/OSB · ürün/faaliyet tarifi · çalışan sayısı bandı · kaynak adı · son_güncelleme`
3. Her metin parçasına **kaynak künyesi** ekle: `firma_id · kaynak_adı · güncelleme_tarihi`. Künyesiz chunk indekslenmez — Mimir kaynak satırı yazamaz, prompt kuralı 3 çöker.
4. Varsayım 3 "evet" çıktıysa `odin_ai/rag.chunk_metin` kullan. "hayır" çıktıysa chunk'lama **yapma**.
5. Toplu indeksleme: batch'li, hata toleranslı. Başarısız kayıtları sayıp **listele** — sessizce düşürme.
6. Mandal: `tests/test_rag_korpus.py` — (a) kişisel veri deseni taraması assert'i, (b) künyesiz chunk reddi assert'i. Kırarak doğrula (D-256/4).

## Kabul kriteri

| # | Şart | Kanıt |
|---|---|---|
| 1 | Metin uzunluğu ortancası ≥ 80 karakter | Sayı teslim özetinde |
| 2 | Kişisel veri sızıntısı 0 | Tarama çıktısı |
| 3 | İndekslenen **tekil firma** + **kayıt** sayısı ayrı yazıldı | İki sayı teslim özetinde |
| 4 | Başarısız kayıtlar listelendi | Adet + ilk 5 sebep |
| 5 | Her chunk'ta kaynak künyesi var | Mandal yeşil |
| 6 | `pytest tests/ -q` yeşil | Son satır |

## Kurallar (VERI-KİT · D-196)

- D-247 kişisel veri tek kapıdan · D-250 puan = kimlik dosyası tamlığı · D-252 NACE üç katman (kayıtlı / tahmin ayrımı metinde korunur) · D-238 ölçüm canlı veritabanında.
- Geçici betik yazma (R1).
- Veriyi **değiştirmiyorsun**. UPDATE/DELETE yazmıyorsun. Sadece okuyup indeksliyorsun.

## Ajan chat zorunlu (D-210 · D-217)

```bash
python scripts/ajan_chat.py sorun --ajan utku --task-id VERI-RAG-KORPUS-01 --sorun "<engel>"
python scripts/ajan_chat.py elestiri --ajan utku --konu "RAG korpus" --bulgu "<alan listesine itirazın>"
python scripts/ajan_chat.py oku --son 10
```

Beyaz listedeki bir alanın korpusta işe yaramadığını görürsen **eleştiri** aç — listeyi tek başına değiştirme.

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-RAG-KORPUS-01 --ozet "<tekil firma + kayıt + ortanca uzunluk + sızıntı 0>"
python scripts/gorev_kutusu.py bak --ajan utku      # posta: yeni gorev var mi?
python scripts/ajan_chat.py oku --son 10            # chat: cevap bekleyen mesaj var mi?
```

Yeni görev varsa al ve başla. Bu döngü sonsuzdur (D-312).

## Ilgili Nodlar

- [[AGENTS]]
- [[hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[plans/brief_yasu_ALTYAPI-RAG-EMBEDDER-01]]
