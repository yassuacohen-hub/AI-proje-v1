# Komut Kurallari (DCG uyumlu calisma)

**Neden bu dosya:** Destructive Command Guard (DCG) bir komutu engelledi.

Sebep yazma isleminin kendisi degil, yolun dinamik olmasiydi.

## 1. ASLA yapma

- Degiskenle yol kurmak (R degiskeni, PWD) -> dinamik, dogrulanamaz
- Ayni komutta yazma + calistirma + silme zinciri
- Uzun icerigi PowerShell kacisiyla tasimak (tek ve cok kez basarisiz oldu)


## 2. Bunun yerine

**Tercih sirasi:**

1. Python pathlib ile goreli yol + sabit isim (DCG dostu)
2. Repo icindeki kalici arac scriptleri (zaten var)
3. Gerekirse once olustur, AYRI komutta calistir

**Kural:** yol sabit ve goreli olsun; bir komutta birden fazla yazma/silme yapma.

## 3. Bu dosya nasil olusturuldu

Bu kuralin kendisi de yeni desenle yazildi: kisa python -c + pathlib + goreli yol,
bolum bolum eklendi. Uzun tek-komut yazimi PowerShell kacisinda basarisiz oldu.
