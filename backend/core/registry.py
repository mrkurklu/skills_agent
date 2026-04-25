import json
import types
from typing import List, Dict, Any
from core.base import BaseSkill
from core.database import get_all_skills

class SkillRegistry:
    def __init__(self):
        self.catalog =[]

    def build_catalog(self):
        """Veritabanından yetenekleri çeker."""
        skills_in_db = get_all_skills()
        self.catalog =[]
        
        for skill in skills_in_db:
            self.catalog.append({
                "name": skill["name"],
                "description": skill["description"],
                "parameters_schema": json.loads(skill["parameters_schema"]),
                "python_code": skill["python_code"]
            })
        print(f"📚 Veritabanından Toplam {len(self.catalog)} yetenek yüklendi.")

    def search_skills(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_words = query.lower().split()
        scored_skills =[]
        
        for skill in self.catalog:
            score = 0
            desc = skill["description"].lower()
            name = skill["name"].lower()
            
            for word in query_words:
                if len(word) > 2 and (word in desc or word in name):
                    score += 1
                    
            scored_skills.append((score, skill))
            
        scored_skills.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored_skills[:top_k]]

    def load_skill(self, skill_data: dict) -> BaseSkill:
        """Veritabanındaki STRING Python kodunu canlı ve çalışan bir BaseSkill Objesine çevirir!"""
        code = skill_data["python_code"]
        class_name = "".join(word.capitalize() for word in skill_data["name"].split("_")) + "Skill"
        
        # Dinamik (Sanal) bir modül oluşturuyoruz
        module = types.ModuleType("dynamic_skill_module")
        
        # String halindeki kodu bu modülün içine Execute (çalıştır) ediyoruz
        exec(code, module.__dict__)
        
        # Modülün içinden class'ı bulup örneğini oluşturuyoruz
        skill_class = getattr(module, class_name)
        return skill_class()