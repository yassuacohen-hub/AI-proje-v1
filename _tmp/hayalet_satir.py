import os
B = "Huginn Data Insights/docs/strateji"
m = {"STRATEJI_08_TICARI_RADAR_MIMARI.md": [102, 103, 144, 177, 254, 264],
     "STRATEJI_05_TEKNIK_ONKOSULLAR.md": [101, 102, 217, 243],
     "STRATEJI_02_API_PAKET_KAPSAMI.md": [43, 55],
     "STRATEJI_03_FIYAT_SOZLESME_SLA.md": [18, 187],
     "STRATEJI_06_PAZAR_YERI.md": [111, 206]}
for f, ns in m.items():
    L = open(os.path.join(B, f), encoding="utf-8").read().splitlines()
    for n in ns:
        print(f"{f[:11]}:{n} | {L[n-1][:280]}")
