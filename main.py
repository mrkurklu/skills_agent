import os
import sys
from dotenv import load_dotenv

# .env dosyasını sisteme yükle
load_dotenv()

from core.workflow import Workflow
from core.agent import SkillAgent

# Yeteneklerimizi içeri alalım
from skills.system import ReadFileSkill, RunCommandSkill
from skills.sub_flow import RunWorkflowSkill
from skills.web import ApiRequestSkill
from skills.pirate_translator import PirateTranslatorSkill

def main():
    print("========================================")
    print(" 🚀 SKILLFLOW OTONOM AJAN BAŞLATILDI")
    print("========================================")
    print("Çıkmak için 'q' veya 'quit' yazabilirsiniz.\n")

    # --- DİNAMİK MODEL AYARI ---
    active_model = os.getenv("ACTIVE_MODEL", "gpt-4o-mini")
    print(f"🤖 Aktif Model: {active_model}\n")

    # 1. Sisteme Tüm Yetenekleri Yükle
    skills_dict = {
        "read_file": ReadFileSkill(),
        "run_command": RunCommandSkill(),
        "api_request": ApiRequestSkill(),
        "pirate_translator": PirateTranslatorSkill()
    }
    
    # Alt akış (Sub-workflow) yeteneği diğer yetenekleri bilmek zorundadır
    skills_dict["run_workflow"] = RunWorkflowSkill(available_skills=skills_dict)
    
    available_skills_list = list(skills_dict.values())

    # 2. Ajanı Başlat
    agent = SkillAgent(skills=available_skills_list, model_name=active_model)

    # 3. KESİNTİSİZ GÖREV DÖNGÜSÜ (Sürekli açık kalacak)
    while True:
        görev = input("\n👤 Sen (Görev Ver): ")
        
        # Çıkış kontrolü
        if görev.lower() in ['q', 'quit', 'exit']:
            print("👋 Görüşmek üzere! Sistem kapatılıyor...")
            sys.exit(0)
            
        # Boş basıp geçerse yoksay
        if not görev.strip():
            continue

        print("\n🤖 Ajan planlıyor...")
        
        # 4. Ajan Plan Yapsın
        plan = agent.plan_workflow(user_prompt=görev)
        
        if not plan:
            print("❌ Plan oluşturulamadı (Model hatası veya kota sorunu olabilir).")
            continue

        print("\n📋 AJANIN OLUŞTURDUĞU İŞ AKIŞI PLANI:")
        for step in plan:
            print(f"- Adım: {step['step_id']} -> Yetenek: {step['skill_name']}")

        # 5. İş Akışı Motorunu Başlat ve Çalıştır
        flow = Workflow()
        
        for step in plan:
            skill_instance = skills_dict.get(step["skill_name"])
            if skill_instance:
                flow.add_step(step_id=step["step_id"], skill=skill_instance, inputs=step["inputs"])
            else:
                print(f"⚠️ Hata: Ajan bilinmeyen bir yetenek seçti -> {step['skill_name']}")

        # Çalıştır!
        final_state = flow.run()

        if final_state["status"] == "success":
            print("\n✅ GÖREV BAŞARIYLA TAMAMLANDI! Yeni görev verebilirsiniz.")

if __name__ == "__main__":
    main()