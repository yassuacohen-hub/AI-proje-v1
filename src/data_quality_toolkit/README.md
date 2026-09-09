# Data Quality Toolkit

Kurumsal veri setleri için **sınıflandırma (PII/DLP)**, **sentetik veri tasarımı** ve **kalite doğrulama** altyapısı.

## Mimari

`
data_quality_toolkit/
├── classifier/        # PII tarayıcı, şema profilleme
│   ├── pii_scanner.py
│   └── schema_profiler.py
├── designer/          # Sentetik veri uretici
│   ├── schema_builder.py
│   └── synthetic_generator.py
├── validator/         # Kalite kuralları ve motor
│   ├── rules.py
│   └── quality_engine.py
├── main.py            # Uctan uca demo
├── main.js            # Node.js karşılığı
└── sample_data.py     # Ornek veri seti
`

## Kullanım

`ash
python -m data_quality_toolkit.main
`

## Bağımlılık

Yalnızca standart kutuphane + standart regex/random modulleri. Ucuncu parti bağımlılık yok.

## İlgili Belgeler

- V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md (kalite boyutları)
- V10/07_referanslar/01_veri_kaynagi_envanteri.md
