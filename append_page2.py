# -*- coding: utf-8 -*-
# Script to append the rest of page.tsx - Part 4a

file_path = r"c:\Huginn Data Projesi\Huginn Data Insights\frontend\src\app\firma\[vkn]\page.tsx"

with open(file_path, "a", encoding="utf-8") as f:
    # Temel Bilgiler section
    f.write('              <section>\n')
    f.write('                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">\n')
    f.write('                  <Building2 className="h-5 w-5 text-primary" />\n')
    f.write('                  Temel Bilgiler\n')
    f.write('                </h2>\n')
    f.write('                <div className="grid gap-4 md:grid-cols-2">\n')
    f.write('                  <div className="p-4 bg-muted/30 rounded-xl">\n')
    f.write('                    <div className="text-xs text-muted-foreground mb-1">Ticaret Ünvanı</div>\n')
    f.write('                    <p className="font-medium">{firma.ticaret_unvan}</p>\n')
    f.write('                  </div>\n')
    f.write('                  <div className="p-4 bg-muted/30 rounded-xl">\n')
    f.write('                    <div className="text-xs text-muted-foreground mb-1">VKN</div>\n')
    f.write('                    <p className="font-mono font-medium">{firma.vkn}</p>\n')
    f.write('                  </div>\n')
    f.write('                  <div className="p-4 bg-muted/30 rounded-xl">\n')
    f.write('                    <div className="text-xs text-muted-foreground mb-1">Kuruluş Tarihi</div>\n')
    f.write('                    <p className="font-medium">{firma.kurulus_tarihi}</p>\n')
    f.write('                  </div>\n')
    f.write('                  <div className="p-4 bg-muted/30 rounded-xl">\n')
    f.write('                    <div className="text-xs text-muted-foreground mb-1">İl / İlçe</div>\n')
    f.write('                    <p className="font-medium">{firma.il} / {firma.ilce}</p>\n')
    f.write('                  </div>\n')
    f.write('                  <div className="p-4 bg-muted/30 rounded-xl">\n')
    f.write('                    <div className="text-xs text-muted-foreground mb-1">Çalışan Sayısı</div>\n')
    f.write('                    <p className="font-medium">{firma.calisan_sayisi || "Belirtilmemiş"} kişi</p>\n')
    f.write('                  </div>\n')
    f.write('                  <div className="p-4 bg-muted/30 rounded-xl">\n')
    f.write('                    <div className="text-xs text-muted-foreground mb-1">NACE Kodu</div>\n')
    f.write('                    <p className="font-mono font-medium">{firma.nace_kod} - {firma.nace_aciklama}</p>\n')
    f.write('                  </div>\n')
    f.write('                </div>\n')
    f.write('              </section>\n\n')

print("Part 4a written")