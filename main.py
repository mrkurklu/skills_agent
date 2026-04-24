import os
from dotenv import load_dotenv

load_dotenv()

from core.workflow import Workflow
from core.agent import SkillAgent

# Yeteneklerimizi içeri alalım
from skills.system import ReadFileSkill, RunCommandSkill
from skills.sub_flow import RunWorkflowSkill
from skills.web import ApiRequestSkill

def main():
    print("🚀 SkillFlow: Gerçek Dünya API Testi (Alternatif API)\n")

    # 1. Sisteme Tüm Yetenekleri Yükle
    skills_dict = {
        "read_file": ReadFileSkill(),
        "run_command": RunCommandSkill(),
        "api_request": ApiRequestSkill()
    }
    # Alt akış yeteneğini ekle
    skills_dict["run_workflow"] = RunWorkflowSkill(available_skills=skills_dict)
    
    available_skills_list = list(skills_dict.values())

    # 2. Ajanı Başlat
    agent = SkillAgent(skills=available_skills_list, model_name="gemini/gemini-2.5-flash")

    # 3. Gerçek Dünya Görevi! (Dünyanın en güvenilir test API'sini kullanıyoruz)
    görev = """
1. https://jsonplaceholder.typicode.com/users/1 adresine GET isteği atarak örnek kullanıcı (Leanne Graham) verisini JSON olarak çek.
2. Dönen veriyi kullanarak terminalde echo komutu ile 'kullanici_rapor.txt' adlı bir dosyaya yazdır. 
(Not: Gelen veri JSON olacağı için, echo komutunda doğrudan {{adim_1.result}} kullanabilirsin).
"""
    print(f"👤 KULLANICI GÖREVİ:{görev}")

    # 4. Ajan Plan Yapsın
    plan = agent.plan_workflow(user_prompt=görev)
    
    if not plan:
        print("❌ Plan oluşturulamadı.")
        return

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
            print(f"Hata: Bilinmeyen yetenek {step['skill_name']}")

    # İş akışını kaydet
    flow.save_to_file("flows/kullanici_raporlama_akisi.json")

    # Çalıştır!
    final_state = flow.run()

    if final_state["status"] == "success":
        print("\n✅ GÖREV BAŞARIYLA TAMAMLANDI!")
        print("Klasörünüzde 'kullanici_rapor.txt' dosyasını kontrol edin!")

if __name__ == "__main__":
    main()