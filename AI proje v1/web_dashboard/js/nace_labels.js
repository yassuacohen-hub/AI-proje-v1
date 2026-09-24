// NACE kodlari - sektor aciklamalari (ilk 2 haneye gore)
const NACE_SECTORS = {
  '01':'Tarim ve Bahcecilik','02':'Ormancilik','03':'Balikcilik','05':'Madencilik','06':'Petrol ve Dogal Gaz',
  '07':'Metal Madencilik','08':'Diger Madencilik','09':'Madencilik Destek','10':'Gida Uretimi',
  '11':'Içecek Uretimi','12':'Tutun Urunleri','13':'Tekstil','14':'Giyim','15':'Deri',
  '16':'Agac ve Mobilya','17':'Kagit','18':'Baski ve Yayincilik','19':'Kok ve Kok','20':'Kimya',
  '21':'Ilac ve Eczacilik','22':'Plastik ve Lastik','23':'Cam ve Seramik','24':'Demir Celik',
  '25':'Metal Isleme','26':'Elektronik','27':'Elektrik','28':'Makine','29':'Otomotiv',
  '30':'Ulasim Arac','31':'Mobilya','32':'Diger Uretim','33':'Onarim','35':'Enerji',
  '36':'Su','37':'Atik Toplama','38':'Atik Geri Donusum','39':'Geri Donusum','41':'Insaat',
  '42':'Altyapi Insaat','43':'Ozel Insaat','45':'Otomotiv Satis','46':'Toptan Ticaret',
  '47':'Perakende','49':'Lojistik','50':'Deniz Tasima','51':'Hava Tasima','52':'Depolama',
  '53':'Posta','55':'Konaklama','56':'Yemek','58':'Yayincilik','59':'Film','60':'TV',
  '61':'Telekom','62':'Yazilim','63':'Bilisim','64':'Finans','65':'Sigorta','66':'Finans Hizmet',
  '68':'Gayrimenkul','69':'Hukuk','70':'Danismanlik','71':'Muhendislik','72':'Ar-Ge',
  '73':'Reklam','74':'Tasarim','75':'Veteriner','77':'Kiralama','78':'Insan Kaynaklari',
  '79':'Turizm','80':'Guvenlik','81':'Bakim','82':'Ofis Hizmet','84':'Kamu','85':'Egitim',
  '86':'Saglik','87':'Sosyal Bakim','88':'Sosyal Hizmet','90':'Sanat','91':'Kültür',
  '92':'Sans','93':'Spor','94':'Dernegi','95':'Servis','96':'Hizmet','97':'Ozel Hane',
  '98':'Tarim','99':'Diger',
};

function getNaceLabel(code) {
  if (!code) return '-';
  const prefix = code.substring(0, 2);
  const sector = NACE_SECTORS[prefix];
  return sector ? sector + ' (' + code + ')' : code;
}

function getNaceSector(code) {
  if (!code) return 'Diger';
  const prefix = code.substring(0, 2);
  return NACE_SECTORS[prefix] || 'Diger';
}
