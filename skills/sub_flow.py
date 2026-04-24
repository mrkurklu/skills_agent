import os
from pydantic import BaseModel, Field
from core.base import BaseSkill

class RunWorkflowInput(BaseModel):
    filepath: str = Field(..., description="Çalıştırılacak alt iş akışının (JSON) dosya yolu. Örn: flows/ornek.json")

class RunWorkflowSkill(BaseSkill):
    name = "run_workflow"
    description = "Önceden kaydedilmiş başka bir iş akışını (sub-workflow) çalıştırır ve sonucunu döndürür."
    args_schema = RunWorkflowInput

    def __init__(self, available_skills: dict):
        """Alt akışı çalıştırabilmek için sistemdeki tüm yeteneklere erişimi olmalı."""
        self.available_skills = available_skills
        super().__init__()

    def execute(self, filepath: str) -> dict:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"İş akışı dosyası bulunamadı: {filepath}")
        
        # Circular import'u engellemek için fonksiyon içinde import ediyoruz
        from core.workflow import Workflow 
        
        # Alt akışı yükle ve çalıştır
        print(f"\n   [Alt Akış (Sub-Workflow) Başlatılıyor: {filepath}]")
        sub_flow = Workflow.load_from_file(filepath, self.available_skills)
        result = sub_flow.run()
        
        if result["status"] == "error":
            raise Exception(f"Alt akış başarısız oldu: Düğüm '{result.get('failed_step')}'")
            
        # Alt akışın tüm state'ini (hafızasını) geri döndür ki ana akış bunu kullanabilsin
        return result["state"]