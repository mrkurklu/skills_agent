# 🧠 Skills Agent: The Model-Agnostic Autonomous Engineer

**Skills Agent**, herhangi bir Büyük Dil Modeli'ni (LLM) tam yetkili bir yazılım mühendisine dönüştüren, hafif ama son derece güçlü bir **Agentic Framework**'tür. 

Claude Code'un sunduğu otonom yetenekleri, tek bir sağlayıcıya (Anthropic) bağımlı kalmadan; **Gemini, OpenAI, Llama (Local)** veya herhangi bir modelle kullanmanıza olanak tanır.

---

## ✨ Öne Çıkan Özellikler

* **🌐 Model Bağımsız (Model Agnostic):** `LiteLLM` entegrasyonu sayesinde saniyeler içinde model değiştirin. Bir gün Gemini, ertesi gün GPT-4o veya tamamen yerel bir Llama 3 kullanın.
* **💾 Kalıcı Bellek (Persistent Memory):** `chat_history.json` üzerinden konuşma geçmişini hatırlar. Terminal kapansa bile ajan kaldığı yerden devam eder, bağlamı asla kaybetmez.
* **🛠️ Cerrahi Düzenleme (Surgical Editing):** Tüm dosyayı yeniden yazmak yerine, `replace_in_file` becerisi ile kodun sadece ilgili satırlarında nokta atışı güncellemeler yapar.
* **🖥️ OS Entegrasyonu:** Dosya okuma/yazma, dizin listeleme ve terminalde komut (sunucu başlatma, paket kurma vb.) çalıştırma yeteneği.
* **🔍 Otomatik Keşif:** `list_files` ile proje dizin yapısını analiz eder ve projenin mevcut durumu hakkında stratejik öneriler sunar.
* **⚙️ Öz-Gelişim Kapasitesi:** Kendi kaynak koduna erişebilir ve geliştirme talimatlarını doğrudan kendi mimarisine uygulayabilir.

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum
Projeyi klonlayın ve sanal ortamı hazırlayın:

```bash
git clone [https://github.com/mrkurklu/skills_agent.git](https://github.com/mrkurklu/skills_agent.git)
cd skills_agent
python -m venv venv

# Windows için:
.\venv\Scripts\activate
# Mac/Linux için:
source venv/bin/activate

pip install -r requirements.txt
2. Yapılandırma
Kök dizinde bir .env dosyası oluşturun ve API anahtarınızı ekleyin:

Plaintext
# Örnek kullanım:
OPENAI_API_KEY=sk-your-key
GEMINI_API_KEY=your-gemini-key
3. Çalıştırma
Bash
python main.py
🏗️ Mimari Yapı
Skills Agent, ReAct (Reasoning and Acting) döngüsü üzerine inşa edilmiştir:

Düşünce (Thought): LLM kullanıcı isteğini ve mevcut durumu analiz eder.

Aksiyon (Action): tools.py içerisinde tanımlanan uygun "beceriyi" (skill) seçer.

Gözlem (Observation): Aracın çıktısını (başarı mesajı veya terminal hatası) sisteme geri besleyerek bir sonraki adımı planlar.

Dosya Sistemi
main.py: CLI arayüzü ve kullanıcı etkileşimi.

agent.py: Çekirdek ajan mantığı ve hafıza yönetimi.

tools.py: Ajanın sistem üzerindeki yetenekleri (I/O & Terminal).

chat_history.json: Konuşma geçmişinin saklandığı otonom bellek.

🗺️ Yol Haritası (Roadmap)
[x] Kalıcı Bellek (History Persistence)

[x] Cerrahi Dosya Düzenleme

[x] Proje Dizin Keşfi

[ ] Model Geri Dönüş (Fallback) Mekanizması

[ ] Docker Üzerinde Güvenli Sandbox Çalıştırma

[ ] Web Tabanlı Kontrol Paneli

🤝 Katkıda Bulunun
Bu proje, yazılım geliştirme süreçlerini otonomlaştırma vizyonunun bir parçasıdır. Her türlü Pull Request, hata bildirimi ve öneriye açığız!

Developed by ❤️ by Ali Emir Kürklü