import json
import re
import os
from typing import Any, Dict, List
from core.base import BaseSkill

class Workflow:
    def __init__(self):
        self.steps =[]
        self.state = {}

    def add_step(self, step_id: str, skill: BaseSkill, inputs: Dict[str, Any]):
        self.steps.append({
            "id": step_id,
            "skill": skill,
            "inputs": inputs
        })

    def save_to_file(self, filepath: str):
        """İş akışını (Node'ları) JSON olarak kaydeder."""
        export_steps =[]
        for step in self.steps:
            export_steps.append({
                "step_id": step["id"],
                "skill_name": step["skill"].name,
                "inputs": step["inputs"]
            })
        
        # Eğer klasör yoksa oluştur
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_steps, f, indent=2, ensure_ascii=False)
        print(f"💾 Akış Başarıyla Kaydedildi: {filepath}")

    @classmethod
    def load_from_file(cls, filepath: str, available_skills: Dict[str, BaseSkill]):
        """JSON dosyasından iş akışını geri yükler."""
        with open(filepath, "r", encoding="utf-8") as f:
            import_steps = json.load(f)
        
        workflow = cls()
        for step in import_steps:
            skill_name = step["skill_name"]
            if skill_name not in available_skills:
                raise ValueError(f"Sistemde bulunmayan yetenek: {skill_name}")
            
            workflow.add_step(
                step_id=step["step_id"],
                skill=available_skills[skill_name],
                inputs=step["inputs"]
            )
        return workflow

    def _resolve_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        resolved = {}
        for key, value in inputs.items():
            if isinstance(value, str):
                # GÜNCELLEME: Hem tek '{' hem çift '{{' parantezini yakalar
                matches = re.findall(r"\{{1,2}(.*?)\}{1,2}", value)
                if matches:
                    resolved_val = value
                    for match in matches:
                        parts = match.split('.')
                        current_data = self.state
                        
                        try:
                            for part in parts:
                                current_data = current_data[part]
                            
                            str_val = str(current_data).strip()
                            # Hem çift hem tek parantez versiyonunu değiştir
                            resolved_val = resolved_val.replace("{{" + match + "}}", str_val)
                            resolved_val = resolved_val.replace("{" + match + "}", str_val)
                        except (KeyError, TypeError):
                            resolved_val = resolved_val.replace("{{" + match + "}}", f"[HATA: {match} bulunamadı]")
                            resolved_val = resolved_val.replace("{" + match + "}", f"[HATA: {match} bulunamadı]")
                    
                    resolved[key] = resolved_val
                    continue
            resolved[key] = value
        return resolved

    def run(self) -> Dict[str, Any]:
        print("\n" + "="*50)
        print("🔄 İŞ AKIŞI ÇALIŞTIRILIYOR...")
        print("="*50)
        
        for step in self.steps:
            step_id = step["id"]
            skill = step["skill"]
            raw_inputs = step["inputs"]
            
            print(f"\n▶️ Düğüm (Node): [{step_id}] | Yetenek: {skill.name}")
            
            resolved_inputs = self._resolve_inputs(raw_inputs)
            print(f"   Girdiler: {resolved_inputs}")
            
            result = skill.run(**resolved_inputs)
            
            self.state[step_id] = result
            
            if result["status"] == "error":
                print(f"❌ HATA: Akış durduruldu! Detay: {result.get('error')}")
                return {"status": "error", "failed_step": step_id, "state": self.state}
            
            print(f"   ✅ Durum: Başarılı!")

        print("\n" + "="*50)
        print("🎉 İŞ AKIŞI TAMAMLANDI!")
        print("="*50 + "\n")
        
        return {"status": "success", "state": self.state}