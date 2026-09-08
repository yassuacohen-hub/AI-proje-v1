/**
 * Kurumsal Büyük Veri Sınıflandırma, Sentetik Tasarım ve Kalite Test Platformu
 * Node.js & JavaScript Çalıştırıcı
 */

// ==========================================
// 1. MODÜL: HASSAS VERİ (PII) VE DLP TARAYICI
// ==========================================

const SensitivityLevel = {
  RESTRICTED: "RESTRICTED (Çok Gizli)",
  CONFIDENTIAL: "CONFIDENTIAL (Gizli)",
  INTERNAL: "INTERNAL (Kurum İçi)",
  PUBLIC: "PUBLIC (Genel)",
};

class PIIScanner {
  static validateTCKN(tckn) {
    const str = String(tckn).trim();
    if (!/^\d{11}$/.test(str) || str[0] === "0") return false;

    const digits = str.split("").map(Number);
    const oddSum = digits[0] + digits[2] + digits[4] + digits[6] + digits[8];
    const evenSum = digits[1] + digits[3] + digits[5] + digits[7];

    const tenth = ((oddSum * 7) - evenSum) % 10;
    if (tenth < 0 ? (tenth + 10) !== digits[9] : tenth !== digits[9]) return false;

    const eleventh = digits.slice(0, 10).reduce((a, b) => a + b, 0) % 10;
    return eleventh === digits[10];
  }

  static validateLuhnCreditCard(card) {
    const clean = String(card).replace(/[\s-]/g, "");
    if (!/^\d{13,19}$/.test(clean)) return false;

    let sum = 0;
    let shouldDouble = false;
    for (let i = clean.length - 1; i >= 0; i--) {
      let digit = parseInt(clean.charAt(i), 10);
      if (shouldDouble) {
        digit *= 2;
        if (digit > 9) digit -= 9;
      }
      sum += digit;
      shouldDouble = !shouldDouble;
    }
    return sum % 10 === 0;
  }

  static classifyValue(val) {
    if (val === null || val === undefined || String(val).trim() === "") return null;
    const s = String(val).trim();

    if (this.validateLuhnCreditCard(s)) return "CREDIT_CARD";
    if (this.validateTCKN(s)) return "TCKN";
    if (/^TR\d{2}\d{5}[0-9A-Z]{17}$/i.test(s.replace(/\s/g, ""))) return "IBAN";
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s)) return "EMAIL";
    if (/^(\+?90|0)?[5]\d{9}$/.test(s.replace(/[\s()-]/g, ""))) return "PHONE";

    return null;
  }

  static scanColumn(colName, values) {
    const counts = {};
    for (const v of values) {
      const type = this.classifyValue(v);
      if (type) counts[type] = (counts[type] || 0) + 1;
    }

    const lower = colName.toLowerCase();
    if (lower.includes("tc") || lower.includes("kimlik")) counts["TCKN"] = (counts["TCKN"] || 0) + 2;
    if (lower.includes("kart") || lower.includes("card")) counts["CREDIT_CARD"] = (counts["CREDIT_CARD"] || 0) + 2;
    if (lower.includes("mail")) counts["EMAIL"] = (counts["EMAIL"] || 0) + 2;
    if (lower.includes("tel") || lower.includes("phone")) counts["PHONE"] = (counts["PHONE"] || 0) + 2;

    const entries = Object.entries(counts);
    if (entries.length === 0) {
      return {
        detectedType: "GENERIC_DATA",
        level: SensitivityLevel.PUBLIC,
        confidence: 0.95,
        recommendation: "Genel kurumsal veri.",
      };
    }

    entries.sort((a, b) => b[1] - a[1]);
    const topType = entries[0][0];

    let level = SensitivityLevel.PUBLIC;
    let rec = "Açık veri.";
    if (topType === "CREDIT_CARD") {
      level = SensitivityLevel.RESTRICTED;
      rec = "ACİL: Kredi kartı verisi maskelenmeli ve tokenization uygulanmalı.";
    } else if (topType === "TCKN" || topType === "IBAN") {
      level = SensitivityLevel.CONFIDENTIAL;
      rec = "KVKK Uyarısı: Hassas kimlik/finans verisi. Sentetik ikame zorunlu.";
    } else if (topType === "EMAIL" || topType === "PHONE") {
      level = SensitivityLevel.INTERNAL;
      rec = "İletişim verisi: Kurum içi erişimle sınırlandırılmalı.";
    }

    return {
      detectedType: topType,
      level: level,
      confidence: Math.min(0.99, (entries[0][1] / values.length) + 0.3),
      recommendation: rec,
    };
  }
}

// ==========================================
// 2. MODÜL: NVIDIA NeMo İLHAMLI SENTETİK VERİ ÜRETİCİ
// ==========================================

class SyntheticDataGenerator {
  static FIRST_NAMES = ["Ahmet", "Mehmet", "Mustafa", "Ali", "Fatma", "Ayşe", "Zeynep", "Elif", "Burak", "Can", "Selin"];
  static LAST_NAMES = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Öztürk", "Aydın", "Arslan", "Doğan"];
  static CITIES = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"];

  static generateValidMockTCKN() {
    const first = Math.floor(Math.random() * 9) + 1;
    const digits = [first];
    for (let i = 0; i < 8; i++) digits.push(Math.floor(Math.random() * 10));

    const oddSum = digits[0] + digits[2] + digits[4] + digits[6] + digits[8];
    const evenSum = digits[1] + digits[3] + digits[5] + digits[7];
    const tenth = ((oddSum * 7) - evenSum) % 10;
    digits.push(tenth < 0 ? tenth + 10 : tenth);

    const eleventh = digits.reduce((a, b) => a + b, 0) % 10;
    digits.push(eleventh);

    return digits.join("");
  }

  static generateValidMockCreditCard() {
    const prefixes = ["4", "51", "52", "53", "54", "55"];
    const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
    let payload = prefix;
    while (payload.length < 15) {
      payload += Math.floor(Math.random() * 10);
    }

    // Luhn check digit
    let sum = 0;
    let shouldDouble = true;
    for (let i = payload.length - 1; i >= 0; i--) {
      let digit = parseInt(payload.charAt(i), 10);
      if (shouldDouble) {
        digit *= 2;
        if (digit > 9) digit -= 9;
      }
      sum += digit;
      shouldDouble = !shouldDouble;
    }
    const checkDigit = (10 - (sum % 10)) % 10;
    const card = payload + checkDigit;
    return `${card.slice(0,4)} ${card.slice(4,8)} ${card.slice(8,12)} ${card.slice(12)}`;
  }

  static generateDataset(rowCount = 100) {
    const dataset = {
      customer_id: [],
      full_name: [],
      tckn_mock: [],
      credit_card_mock: [],
      email: [],
      phone: [],
      city: [],
      account_balance_tl: [],
      status: [],
    };

    for (let i = 1; i <= rowCount; i++) {
      const first = this.FIRST_NAMES[Math.floor(Math.random() * this.FIRST_NAMES.length)];
      const last = this.LAST_NAMES[Math.floor(Math.random() * this.LAST_NAMES.length)];

      dataset.customer_id.push(`CUST-${10000 + i}`);
      dataset.full_name.push(`${first} ${last}`);
      dataset.tckn_mock.push(this.generateValidMockTCKN());
      dataset.credit_card_mock.push(this.generateValidMockCreditCard());
      dataset.email.push(`${first.toLowerCase()}.${last.toLowerCase()}${i}@kurumsal.com`);
      dataset.phone.push(`+90 532 ${Math.floor(Math.random() * 899 + 100)} ${Math.floor(Math.random() * 89 + 10)} ${Math.floor(Math.random() * 89 + 10)}`);
      dataset.city.push(this.CITIES[Math.floor(Math.random() * this.CITIES.length)]);
      
      // %3 Anomali enjeksiyonu (Test senaryoları için)
      if (Math.random() < 0.03) {
        dataset.account_balance_tl.push(-250.0); // Negatif bakiye anomalisi
      } else {
        dataset.account_balance_tl.push(parseFloat((Math.random() * 75000 + 1500).toFixed(2)));
      }

      dataset.status.push(Math.random() < 0.90 ? "ACTIVE" : "PENDING");
    }

    return dataset;
  }
}

// ==========================================
// 3. MODÜL: VERİ KALİTE VE DOĞRULAMA MOTORU
// ==========================================

class DataQualityEngine {
  constructor() {
    this.rules = [];
  }

  addRule(rule) {
    this.rules.push(rule);
  }

  validate(dataset) {
    const results = [];
    let passedCount = 0;
    let failedCount = 0;
    let totalCells = 0;
    let failedCells = 0;

    for (const rule of this.rules) {
      const values = dataset[rule.column] || [];
      const total = values.length;
      totalCells += total;

      const failedIndices = [];
      values.forEach((v, idx) => {
        if (!rule.validator(v)) failedIndices.push({ idx, val: v });
      });

      const failed = failedIndices.length;
      const passed = total - failed;
      failedCells += failed;

      const isPassed = failed === 0;
      if (isPassed) passedCount++;
      else failedCount++;

      results.push({
        name: rule.name,
        column: rule.column,
        description: rule.description,
        passed: isPassed,
        total,
        passedRecords: passed,
        failedRecords: failed,
        failureRate: ((failed / Math.max(total, 1)) * 100).toFixed(1),
        samples: failedIndices.slice(0, 3).map(f => `Satır ${f.idx}: ${f.val}`),
      });
    }

    const cellPassRate = 1.0 - (failedCells / Math.max(totalCells, 1));
    const rulePassRate = passedCount / Math.max(this.rules.length, 1);
    const score = Math.max(0, Math.min(100, (cellPassRate * 60 + rulePassRate * 40).toFixed(2)));

    return {
      score: parseFloat(score),
      totalRules: this.rules.length,
      passedRules: passedCount,
      failedRules: failedCount,
      results,
    };
  }
}

// ==========================================
// ANA ÇALIŞTIRMA VE GÖRSEL DEMO
// ==========================================

function main() {
  console.log("\n" + "★".repeat(85));
  console.log(" KURUMSAL BÜYÜK VERİ SINIFLANDIRMA, SENTETİK TASARIM VE KALİTE TEST PLATFORMU ");
  console.log("★".repeat(85));

  // 1. Sentetik Veri Tasarımı ve Üretimi
  console.log("\n" + "=".repeat(80));
  console.log(" 🚀 1. AŞAMA: NVIDIA NeMo DATA DESIGNER İLE SENTETİK VERİ ÜRETİMİ");
  console.log("=".repeat(80));

  const dataset = SyntheticDataGenerator.generateDataset(150);
  console.log(`✅ 150 Satır Kurumsal Bankacılık Sentetik Verisi Üretildi (KVKK Uyumlu)`);
  console.log("\nİlk 3 Örnek Kayıt:");
  for (let i = 0; i < 3; i++) {
    console.log(`  • [${dataset.customer_id[i]}] ${dataset.full_name[i]} | TCKN: ${dataset.tckn_mock[i]} | Kart: ${dataset.credit_card_mock[i]} | Bakiye: ${dataset.account_balance_tl[i]} TL`);
  }

  // 2. Veri Sınıflandırma ve DLP Taraması
  console.log("\n" + "=".repeat(80));
  console.log(" 🚀 2. AŞAMA: KURUMSAL VERİ SINIFLANDIRMA VE DLP TARAMASI");
  console.log("=".repeat(80));

  console.log(`${"SÜTUN ADI".padEnd(20)} | ${"TESPİT EDİLEN PII".padEnd(18)} | ${"GÜVENLİK SEVİYESİ".padEnd(28)} | GÜVEN`);
  console.log("-".repeat(85));

  for (const [colName, colValues] of Object.entries(dataset)) {
    const res = PIIScanner.scanColumn(colName, colValues);
    console.log(
      `${colName.padEnd(20)} | ${res.detectedType.padEnd(18)} | ${res.level.padEnd(28)} | %${Math.round(res.confidence * 100)}`
    );
  }

  // 3. Veri Kalitesi ve Doğrulama Testleri
  console.log("\n" + "=".repeat(80));
  console.log(" 🚀 3. AŞAMA: GREAT EXPECTATIONS MODELİNDE VERİ KALİTE TESTLERİ");
  console.log("=".repeat(80));

  const engine = new DataQualityEngine();

  engine.addRule({
    name: "NOT_NULL_ID",
    column: "customer_id",
    description: "Müşteri ID alanı asla boş olamaz.",
    validator: v => v !== null && v !== undefined && String(v).trim() !== "",
  });

  engine.addRule({
    name: "TCKN_ALGORITHM",
    column: "tckn_mock",
    description: "TCKN değerleri resmi matematiksel doğrulama algoritmasına uymalıdır.",
    validator: v => PIIScanner.validateTCKN(v),
  });

  engine.addRule({
    name: "LUHN_CREDIT_CARD",
    column: "credit_card_mock",
    description: "Kart numaraları Luhn (Mod 10) algoritmasına uygun olmalıdır.",
    validator: v => PIIScanner.validateLuhnCreditCard(v),
  });

  engine.addRule({
    name: "POSITIVE_BALANCE",
    column: "account_balance_tl",
    description: "Hesap bakiyesi negatif olamaz (>= 0 TL).",
    validator: v => typeof v === "number" && v >= 0,
  });

  engine.addRule({
    name: "VALID_EMAIL",
    column: "email",
    description: "E-posta adresleri geçerli RFC formatında olmalıdır.",
    validator: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v)),
  });

  const report = engine.validate(dataset);

  console.log(`${"KURAL ADI".padEnd(22)} | ${"SÜTUN".padEnd(20)} | ${"DURUM".padEnd(10)} | ${"BAŞARILI".padEnd(10)} | HATALI`);
  console.log("-".repeat(85));

  for (const r of report.results) {
    const statusStr = r.passed ? "✅ GEÇTİ" : "❌ KALDI";
    console.log(`${r.name.padEnd(22)} | ${r.column.padEnd(20)} | ${statusStr.padEnd(10)} | ${String(r.passedRecords).padEnd(10)} | ${r.failedRecords}`);
  }

  console.log("\n" + "=".repeat(85));
  console.log(` 🏆 TOPLAM VERİ KALİTE SKORU (DATA QUALITY SCORE): ${report.score} / 100`);
  console.log("=".repeat(85));

  console.log("\n" + "★".repeat(85));
  console.log(" TÜM AŞAMALAR BAŞARIYLA TAMAMLANDI! ");
  console.log("★".repeat(85) + "\n");
}

main();
