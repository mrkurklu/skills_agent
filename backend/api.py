import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from core.database import init_db, get_all_skills, add_skill
from core.registry import SkillRegistry
from core.agent import SkillAgent

app = FastAPI(title="SkillFlow API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SİSTEM BAŞLARKEN DB'Yİ KUR VE KONTROL ET ---
init_db()

# Eğer DB boşsa, ilk "Tohum" (Seed) yeteneği otomatik ekle!
if not get_all_skills():
    print("🌱 Veritabanı boş, varsayılan 'read_file' yeteneği yükleniyor...")
    sample_code = """
import os
from pydantic import BaseModel, Field
from core.base import BaseSkill

class ReadFileInput(BaseModel):
    file_path: str = Field(...)

class ReadFileSkill(BaseSkill):
    name = "read_file"
    description = "Sistemden bir dosyanın içeriğini okur."
    args_schema = ReadFileInput

    def execute(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError("Dosya bulunamadi.")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
"""
    sample_schema = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Okunacak dosyanın yolu."}
        },
        "required":["file_path"]
    }
    add_skill("read_file", "Sistemden bir dosyanın içeriğini okur.", sample_schema, sample_code)

# Registry'yi başlat
registry = SkillRegistry()
registry.build_catalog()

class AgentRequest(BaseModel):
    prompt: str

@app.get("/api/skills")
def get_skills():
    registry.build_catalog() 
    return registry.catalog

@app.post("/api/agent/plan")
def create_plan(request: AgentRequest):
    active_model = os.getenv("ACTIVE_MODEL", "gpt-4o-mini")
    
    relevant_skills = registry.search_skills(query=request.prompt, top_k=4)
    if not relevant_skills:
         raise HTTPException(status_code=404, detail="Görevi yapacak uygun yetenek veritabanında bulunamadı.")

    loaded_skills =[registry.load_skill(s) for s in relevant_skills]
    
    agent = SkillAgent(skills=loaded_skills, model_name=active_model)
    plan = agent.plan_workflow(user_prompt=request.prompt)
    
    if not plan:
        raise HTTPException(status_code=500, detail="Ajan plan oluşturamadı.")
        
    return {
        "status": "success",
        "model_used": active_model,
        "selected_skills":[s.name for s in loaded_skills],
        "workflow_plan": plan
    }