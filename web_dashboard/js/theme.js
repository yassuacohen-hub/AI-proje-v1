/* theme.js — UX-03: Theme Management System
 *
 * Sorumluluk:
 *   1. Tema durumunu <html data-theme="dark|light"> uzerinde tutmak
 *   2. Kullanici secimini localStorage'da kalici kilmak (anahtar: huginn-theme)
 *   3. Secim yoksa isletim sistemi tercihini (prefers-color-scheme) izlemek
 *   4. Topbar butonunu baglamak ve erisilebilir durum bildirmek
 *
 * Not: FOUC (yanlis tema ile bir kare cizim) engellemek icin bu dosya
 * index.html <head> icinde, CSS'ten SONRA ve body'den ONCE yuklenir.
 * Bu yuzden DOM'a bagimli isler DOMContentLoaded'a ertelenir.
 */
(function (global) {
  "use strict";

  var DEPO_ANAHTARI = "huginn-theme";
  var TEMALAR = ["dark", "light"];
  var VARSAYILAN = "dark";

  function gecerliMi(deger) {
    return TEMALAR.indexOf(deger) !== -1;
  }

  /** localStorage erisimi private mode/quota durumlarinda patlayabilir. */
  function kayitliTema() {
    try {
      var deger = global.localStorage.getItem(DEPO_ANAHTARI);
      return gecerliMi(deger) ? deger : null;
    } catch (e) {
      return null;
    }
  }

  function temayiKaydet(tema) {
    try {
      global.localStorage.setItem(DEPO_ANAHTARI, tema);
      return true;
    } catch (e) {
      return false;
    }
  }

  /** Isletim sistemi tercihi; matchMedia yoksa varsayilana duser. */
  function sistemTemasi() {
    try {
      if (global.matchMedia &&
          global.matchMedia("(prefers-color-scheme: light)").matches) {
        return "light";
      }
    } catch (e) {
      /* sessiz: eski tarayici */
    }
    return VARSAYILAN;
  }

  function aktifTema() {
    var kok = global.document.documentElement;
    var mevcut = kok.getAttribute("data-theme");
    return gecerliMi(mevcut) ? mevcut : VARSAYILAN;
  }

  /** Temayi DOM'a uygular; kalici=false ise yalniz oturum icin gecerlidir. */
  function temaUygula(tema, kalici) {
    if (!gecerliMi(tema)) {
      tema = VARSAYILAN;
    }
    var kok = global.document.documentElement;
    kok.setAttribute("data-theme", tema);

    if (kalici !== false) {
      temayiKaydet(tema);
    }
    butonuGuncelle(tema);
    olayYay(tema);
    return tema;
  }

  function temaDegistir() {
    return temaUygula(aktifTema() === "dark" ? "light" : "dark", true);
  }

  /** Kullanici secimini silip sistem tercihine geri doner. */
  function sistemeDon() {
    try {
      global.localStorage.removeItem(DEPO_ANAHTARI);
    } catch (e) {
      /* sessiz */
    }
    return temaUygula(sistemTemasi(), false);
  }

  function butonuGuncelle(tema) {
    var btn = global.document.getElementById("theme-toggle");
    if (!btn) {
      return;
    }
    var hedef = tema === "dark" ? "aydınlık" : "karanlık";
    btn.setAttribute("aria-pressed", tema === "light" ? "true" : "false");
    btn.setAttribute("aria-label", "Temayı " + hedef + " moda geçir");
    btn.setAttribute("title", "Temayı " + hedef + " moda geçir");

    var etiket = btn.querySelector(".theme-toggle-label");
    if (etiket) {
      etiket.textContent = tema === "dark" ? "Karanlık" : "Aydınlık";
    }
  }

  /** Grafik kutuphaneleri (Chart.js) renkleri yeniden okusun diye olay. */
  function olayYay(tema) {
    try {
      var olay;
      if (typeof global.CustomEvent === "function") {
        olay = new global.CustomEvent("huginn:themechange", {
          detail: { theme: tema }
        });
      } else {
        olay = global.document.createEvent("CustomEvent");
        olay.initCustomEvent("huginn:themechange", false, false, { theme: tema });
      }
      global.document.dispatchEvent(olay);
    } catch (e) {
      /* sessiz */
    }
  }

  /** Kullanici secim yapmadiysa OS tercihi degisince tema da degisir. */
  function sistemIzle() {
    if (!global.matchMedia) {
      return;
    }
    var mq = global.matchMedia("(prefers-color-scheme: light)");
    var isleyici = function () {
      if (!kayitliTema()) {
        temaUygula(sistemTemasi(), false);
      }
    };
    if (mq.addEventListener) {
      mq.addEventListener("change", isleyici);
    } else if (mq.addListener) {
      mq.addListener(isleyici);
    }
  }

  /** Head icinde senkron calisir: ilk boyamadan once dogru tema yazilir. */
  function ilkYukleme() {
    var secim = kayitliTema();
    temaUygula(secim || sistemTemasi(), Boolean(secim));
  }

  function butonuBagla() {
    var btn = global.document.getElementById("theme-toggle");
    if (btn && !btn.dataset.themeBound) {
      btn.dataset.themeBound = "1";
      btn.addEventListener("click", function () {
        temaDegistir();
      });
    }
    butonuGuncelle(aktifTema());
  }

  ilkYukleme();
  sistemIzle();

  if (global.document.readyState === "loading") {
    global.document.addEventListener("DOMContentLoaded", butonuBagla);
  } else {
    butonuBagla();
  }

  global.HuginnTheme = {
    DEPO_ANAHTARI: DEPO_ANAHTARI,
    TEMALAR: TEMALAR,
    VARSAYILAN: VARSAYILAN,
    aktifTema: aktifTema,
    temaUygula: temaUygula,
    temaDegistir: temaDegistir,
    sistemeDon: sistemeDon,
    sistemTemasi: sistemTemasi
  };
})(window);
