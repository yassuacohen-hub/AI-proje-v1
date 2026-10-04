# -*- coding: utf-8 -*-
'''9Router anahtar guvenli guncelleme (ALTYAPI-9ROUTER-ANAHTAR-01).

Kural: anahtar HICBIR YERDE yazilmaz - ne stdout, ne log, ne commit.
Yalniz ilk 4 karakter basilir.

Atomik yazma: once .env.bak al, sonra gecici dosyaya yaz,
os.replace ile degistir. Boylece yarim .env olusmaz.

Kullanim:
    python scripts/ninerouter_anahtar_guncelle.py --kuru <yeni_anahtar>
    python scripts/ninerouter_anahtar_guncelle.py <yeni_anahtar>
'''
import argparse
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
ENV = KOK / '.env'
ANAHTAR_ADI = 'NINEROUTER_KEY'
GOSTER = 4


def _yedek(yol):
    """Zaman damgali yedek al."""
    damga = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    yedek = yol.with_name(yol.name + '.bak_' + damga)
    shutil.copy2(yol, yedek)
    return yedek


def _satir_sayisi(metin):
    """NINEROUTER_KEY= ile baslayan satir sayisi."""
    return sum(1 for ln in metin.splitlines()
               if ln.strip().startswith(ANAHTAR_ADI + '='))


def _guncelle(env_yolu, yeni):
    """NINEROUTER_KEY satirini degistirir/ekler; atomik yazar.

    Doner: (yedek_yolu, adet, maske)
    """
    metin = env_yolu.read_text(encoding='utf-8-sig')
    yeni_satir = ANAHTAR_ADI + '=' + yeni
    satirlar = []
    adet = 0
    for ln in metin.splitlines():
        if ln.strip().startswith(ANAHTAR_ADI + '='):
            satirlar.append(yeni_satir)
            adet += 1
        else:
            satirlar.append(ln)
    if adet == 0:
        satirlar.append(yeni_satir)
        adet = 1
    icerik = '\n'.join(satirlar) + '\n'
    yedek = _yedek(env_yolu)
    gecici = env_yolu.with_name(env_yolu.name + '.tmp')
    gecici.write_text(icerik, encoding='utf-8')
    os.replace(gecici, env_yolu)
    return yedek, adet, yeni[:GOSTER]


def _geri_yukle(yedek_yolu, env_yolu):
    """Yedekten geri al (atomik)."""
    gecici = env_yolu.with_name(env_yolu.name + '.geri')
    shutil.copy2(yedek_yolu, gecici)
    os.replace(gecici, env_yolu)


def main():
    ap = argparse.ArgumentParser(
        description='9Router anahtarini .env icinde guvenle guncelle')
    ap.add_argument('anahtar', help='yeni anahtar degeri')
    ap.add_argument('--kuru', action='store_true',
                    help='hicbir dosyaya yazmaz, yalniz plani gosterir')
    ap.add_argument('--env', default=str(ENV), help='hedef .env yolu')
    a = ap.parse_args()

    yol = Path(a.env)
    if not yol.exists():
        print('HATA: .env bulunamadi: ' + str(yol))
        return 2

    yeni = a.anahtar.strip()
    if not yeni:
        print('HATA: anahtar bos')
        return 2

    mevcut = _satir_sayisi(yol.read_text(encoding='utf-8-sig'))
    print('hedef dosya    : ' + str(yol))
    print('mevcut satir   : ' + str(mevcut))
    print('plan           : ' + ANAHTAR_ADI + '=' + yeni[:GOSTER]
          + '... (' + str(GOSTER) + ' karakter gosterildi)')

    if a.kuru:
        print('[KURU] hicbir dosya degismedi')
        return 0

    if mevcut > 1:
        print('HATA: .env icinde ' + str(mevcut) + ' adet ' + ANAHTAR_ADI
              + ' satiri var; tekillestirilmeden degistirilmez.')
        return 3

    yedek, adet, maske = _guncelle(yol, yeni)
    print('guncellenen    : ' + str(adet) + ' satir')
    print('yedek          : ' + yedek.name)

    sonraki = _satir_sayisi(yol.read_text(encoding='utf-8'))
    if sonraki != 1:
        _geri_yukle(yedek, yol)
        print('DOGRULAMA BASARISIZ: satir ' + str(sonraki)
              + ', yedek geri yuklendi')
        return 1
    print('DOGRULAMA      : tek satir, yedek mevcut')
    return 0


if __name__ == '__main__':
    sys.exit(main())