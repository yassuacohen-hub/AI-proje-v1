# -*- coding: utf-8 -*-
# Script to append the rest of page.tsx - Part 4b

file_path = r"c:\Huginn Data Projesi\Huginn Data Insights\frontend\src\app\firma\[vkn]\page.tsx"

with open(file_path, "a", encoding="utf-8") as f:
    # Sektör ve NACE section
    f.write('              <section>\n')
    f.write('                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">\n')
    f.write('                  <Tag className="h-5 w-5 text-primary" />\n')
    f.write('                  Sektör ve NACE\n')
    f.write('                </h2>\n')
    f.write('                <div className="p-4 bg-muted/30 rounded-xl">\n')
    f.write('                  <p className="font-medium">{firma.sektor}</p>\n')
    f.write('                  <p className="text-sm text-muted-foreground mt-1">NACE {firma.nace_kod}: {firma.nace_aciklama}</p>\n')
    f.write('                </div>\n')
    f.write('              </section>\n\n')

    # Risk Analizi section
    f.write('              <section>\n')
    f.write('                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">\n')
    f.write('                  <Shield className="h-5 w-5 text-primary" />\n')
    f.write('                  Risk Analizi\n')
    f.write('                </h2>\n')
    f.write('                <div className="grid gap-4 md:grid-cols-2">\n')
    f.write('                  <div className="p-4 rounded-xl bg-red-50 border-red-200">\n')
    f.write('                    <div className="text-xs text-muted-foreground mb-1">Risk Skoru</div>\n')
    f.write('                    <div className="text-4xl font-bold">{firma.risk_skoru}/100</div>\n')
    f.write('                    <div className="mt-2 px-3 py-1 rounded-full text-sm font-medium inline-block bg-red-100 text-red-700">\n')
    f.write('                      {firma.risk_seviye} Risk\n')
    f.write('                    </div>\n')
    f.write('                  </div>\n')
    f.write('                  <div className="p-4 bg-muted/30 rounded-xl">\n')
    f.write('                    <div className="text-xs text-muted-foreground mb-1">Kimlik Tamlığı</div>\n')
    f.write('                    <div className="text-2xl font-bold">{firma.kimlik_tamligi}%</div>\n')
    f.write('                    <div className="text-xs text-muted-foreground mt-1">Veri Kalitesi: {firma.veri_kalitesi}%</div>\n')
    f.write('                  </div>\n')
    f.write('                </div>\n')
    f.write('              </section>\n\n')

print("Part 4b written")