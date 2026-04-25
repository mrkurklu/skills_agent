import os
import sys
from dotenv import load_dotenv

load_dotenv()

from core.workflow import Workflow
from core.agent import SkillAgent

# Şimdilik elimizdeki yetenekleri manuel katalogluyoruz (Binlerce skill yapısına geçmeden önceki son adım)
from skills.system import ReadFileSkill, RunCommandSkill
from skills.web import ApiRequestSkill
from skills.pirate_translator import PirateTranslatorSkill

def main():
    print("======================================================")
    print(" 🛠️ SKILLFLOW: KULLANICI DÜZENLEMELİ AJAN MİMARİSİ")
    print("======================================================")
    
    active_model = os.getenv("ACTIVE_MODEL", "gpt-4o-mini")
    
    # 1. Kütüphanemizdeki Yetenekler (Katalog)
    skills_dict = {
        "read_file": ReadFileSkill(),
        "run_command": RunCommandSkill(),
        "api_request": ApiRequestSkill(),
        "pirate_translator": PirateTranslatorSkill()
    }
    
    # 2. Mimar Ajanı Başlat
    agent = SkillAgent(skills=list(skills_dict.values()), model_name=active_model)

    print("\nNe tür bir otomasyon ajanı oluşturmak istersin?")
    print("(Örn: Webden veri çek, terminalde dosyaya yaz vb.)")
    
    görev = input("\n👤 Sen (Ajan Promptu): ")
    if not görev.strip():
        print("Görev boş olamaz, çıkılıyor.")
        sys.exit(0)

    print(f"\n🤖 Mimar Ajan '{active_model}' ile planlıyor...")
    plan = agent.plan_workflow(user_prompt=görev)
    
    if not plan:
        print("❌ Plan oluşturulamadı.")
        sys.exit(1)

    # 3. OLUŞTURULAN PLANI JSON OLARAK KAYDET (Kullanıcı düzenleyebilsin diye)
    taslak_dosya = "flows/taslak_ajan.json"
    
    # Geçici bir workflow objesi oluşturup save_to_file metodumuzu kullanıyoruz
    temp_flow = Workflow()
    for step in plan:
        skill_instance = skills_dict.get(step["skill_name"])
        if skill_instance:
            temp_flow.add_step(step_id=step["step_id"], skill=skill_instance, inputs=step["inputs"])
    
    temp_flow.save_to_file(taslak_dosya)
    
    # 4. KULLANICIYA DÜZENLEME ŞANSI VER! (n8n Mantığının Kalbi)
    print("\n" + "*"*60)
    print("🎯 AJAN TASLAĞI HAZIRLANDI!")
    print(f"👉 Sistem şu dosyayı oluşturdu: '{taslak_dosya}'")
    print("İstersen VS Code veya not defteri ile bu JSON dosyasını açıp parametreleri değiştirebilirsin.")
    print("Düzenlemen bittiğinde veya doğrudan çalıştırmak istersen Enter'a bas.")
    print("*"*60)
    
    input("\n[Çalıştırmak için ENTER'a bas]...")

    # 5. DÜZENLENMİŞ JSON'U GERİ YÜKLE VE ÇALIŞTIR!
    print("\n🚀 AKIŞ ÇALIŞTIRILIYOR...")
    
    try:
        # JSON'dan kullanıcının belki de editlediği son haliyle yüklüyoruz
        final_flow = Workflow.load_from_file(filepath=taslak_dosya, available_skills=skills_dict)
        sonuc = final_flow.run()
        
        if sonuc["status"] == "success":
            print("\n✅ AJAN GÖREVİNİ BAŞARIYLA TAMAMLANDI!")
    except Exception as e:
         print(f"\n❌ JSON çalıştırılırken hata oluştu (JSON formatını bozmuş olabilirsiniz): {e}")

if __name__ == "__main__":
    main()