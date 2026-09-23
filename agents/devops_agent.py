# DevOps Agent - LLM ile entegre yetenek sistemi

import anthropic  # Claude SDK örneği
from skills.base import registry
import skills.streamlit.debug  # Skill'lerin register'a yüklenmesi için import şarttır
import skills.devops.nginx
import skills.devops.docker
import skills.devops.monitor
import skills.common.file_ops
import skills.common.llm_helper
import skills.streamlit.ux_ui

class ProductionAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-3-5-sonnet-20241022"

    def run(self, user_prompt: str):
        # 1. Kayıtlı tüm yetenek şemalarını Claude'un anlayacağı 'tools' formatında al
        available_tools = registry.get_all_schemas()

        print("🤖 Ajan yetenekleri yükleniyor...")
        
        # 2. LLM'e isteği ve yetenek havuzunu gönder
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=1024,
            tools=available_tools, # <-- Yetenekler buraya enjekte ediliyor!
            messages=[{"role": "user", "content": user_prompt}]
        )

        # 3. Eğer Claude bir skill (tool) kullanmak isterse:
        if response.stop_reason == "tool_use":
            tool_use = response.content[-1] # Son adımdaki tool çağrısını al
            tool_name = tool_use.name
            tool_inputs = tool_use.input

            print(f"🎯 Claude bir skill tetikledi: {tool_name} | Parametreler: {tool_inputs}")

            # 4. İlgili fonksiyonu dinamik olarak çalıştır
            result = registry.execute_skill(tool_name, **tool_inputs)
            
            print(f"✅ Skill Sonucu: {result}")
            return result
        
        return response.content[0].text

# --- ÇALIŞTIRMA ÖRNEĞİ ---
if __name__ == "__main__":
    agent = ProductionAgent()
    
    # Ajan, elindeki "fix_nginx_websocket" yeteneğini şemadan algılayıp otomatik seçecektir.
    agent.run("Streamlit uygulamam production sunucusunda sürekli kopuyor, nginx ayarlarını kontrol etmeliyim. domain: mystreamlitapp.com")