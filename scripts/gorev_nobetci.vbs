' FIX-NOB-02: gorev_nobetci.bat dosyasini gizli pencerede calistirir
Set sh = CreateObject("WScript.Shell")
sh.Run "cmd /c ""C:\Huginn Data Projesi\Huginn Data Insights\scripts\gorev_nobetci.bat""", 0, False
