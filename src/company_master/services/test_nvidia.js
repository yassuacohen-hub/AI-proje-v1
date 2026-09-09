/**
 * NVIDIA API Bağlantı Testi
 */

async function testNvidiaAPI() {
  const apiKey = process.env.NVIDIA_API_KEY;
if (!apiKey) {
  console.error("HATA: NVIDIA_API_KEY ortam degiskeni tanimli degil. .env dosyasini kontrol edin.");
  process.exit(1);
}
  const url = "https://integrate.api.nvidia.com/v1/chat/completions";

  console.log("📡 NVIDIA NIM API'sine bağlanılıyor (Model: meta/llama-3.3-70b-instruct)...");

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: "meta/llama-3.3-70b-instruct",
        messages: [
          { role: "user", content: "Merhaba! Kendini 1 cümleyle Türkçe tanıt." }
        ],
        temperature: 0.2,
        max_tokens: 100
      })
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errText}`);
    }

    const data = await response.json();
    console.log("\n✅ NVIDIA API BAĞLANTISI BAŞARILI!");
    console.log("🤖 Modelden Gelen Yanıt:");
    console.log(data.choices[0].message.content);
  } catch (error) {
    console.error("❌ Hata:", error.message);
  }
}

testNvidiaAPI();
