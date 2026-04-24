import os
import re
import importlib
from litellm import completion
from typing import Type
from core.base import BaseSkill

class SkillBuilder:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def build_skill_code(self, prompt: str, class_name: str, skill_name: str) -> str:
        print(f"🧠 [SkillBuilder] '{class_name}' için kod yazılıyor... (Model: {self.model_name})")
        
        system_prompt = f"""Sen üst düzey bir Python ve Yapay Zeka geliştiricisisin. 
Görevin: Sistemimiz için yeni bir Yetenek (Skill) sınıfı yazmak.

ŞABLON VE KURALLAR:
1. 'pydantic' kütüphanesinden BaseModel ve Field kullanarak bir Girdi (Input) şeması oluştur.
2. 'core.base.BaseSkill' sınıfından türeyen bir sınıf yaz. Sınıfın adı tam olarak '{class_name}' olmalı.
3. Sınıfın içinde 'name = "{skill_name}"' ve mantıklı bir 'description' değişkeni tanımla.
4. args_schema olarak yazdığın Pydantic modelini ata.
5. Sınıfın içine asıl işlemi yapan 'execute(self, ...)' metodunu yaz.
6. Kodunda güvenlik açıklarına (rm -rf vb.) yer verme. Gerekirse sadece requests, json, math, os gibi standart kütüphaneleri kullan.
7. Çıktın SADECE VE SADECE çalışabilir Python kodundan oluşmalıdır. Markdown açıklama blokları (```python) kullanma, doğrudan kodu ver.
"""
        messages =[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Aşağıdaki işi yapacak yeteneği Python kodu olarak yaz: {prompt}"}
        ]
        
        try:
            # API'ye İstek At (Timeout'u düşük tutalım ki Google çökükse çok beklemesin)
            response = completion(
                model=self.model_name, 
                messages=messages, 
                temperature=0.1,
                timeout=30 # En fazla 30 saniye bekler
            )
            raw_code = response.choices[0].message.content.strip()
            clean_code = re.sub(r"^```python|```$", "", raw_code, flags=re.MULTILINE).strip()
            return clean_code
            
        except Exception as e:
            # API hatalarını zarifçe ekrana bas!
            print(f"\n❌[LLM API HATASI]: Model ({self.model_name}) şu an yanıt veremiyor veya yoğun.")
            print(f"Detay: {str(e)[:200]}...") # Sadece hatanın ilk 200 karakteri
            return None

    def create_and_load_skill(self, prompt: str, module_filename: str, class_name: str, skill_name: str) -> BaseSkill:
        code = self.build_skill_code(prompt, class_name, skill_name)
        
        if not code:
            return None # Kod üretilemediyse None dön
            
        filepath = os.path.join("skills", f"{module_filename}.py")
        
        # Klasör yoksa oluştur (güvenlik için)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
            
        print(f"💾 Yeni yetenek diske kaydedildi: {filepath}")
        module_path = f"skills.{module_filename}"
        
        try:
            module = importlib.import_module(module_path)
            importlib.reload(module)
            skill_class: Type[BaseSkill] = getattr(module, class_name)
            skill_instance = skill_class()
            
            print(f"✅ Yeni yetenek başarıyla sisteme yüklendi: {skill_instance.name}")
            return skill_instance
            
        except Exception as e:
            print(f"❌ Yetenek yüklenirken (import) hata oluştu: {str(e)}")
            return None