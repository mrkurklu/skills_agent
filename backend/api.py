import os
import requests
import types
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

from core.database import init_db, get_all_skills, add_skill
from core.registry import SkillRegistry
from core.agent import SkillAgent
from core.workflow import Workflow
from core.base import BaseSkill

app = FastAPI(title="SkillFlow API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DB KURULUMU VE TOHUMLAMA (SEED) ---
init_db()

if not get_all_skills():
    print("🌱 Veritabanı boş, Temel Yetenekler yükleniyor...")
    
    # 1. READ FILE
    rf_code = """
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
        if not os.path.exists(file_path): raise FileNotFoundError("Dosya bulunamadi.")
        with open(file_path, "r", encoding="utf-8") as f: return f.read()
"""
    rf_schema = {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}
    add_skill("read_file", "Dosya okuma yeteneği.", rf_schema, rf_code)

    # 2. RUN COMMAND
    rc_code = """
import subprocess
from pydantic import BaseModel, Field
from core.base import BaseSkill
class RunCommandInput(BaseModel):
    command: str = Field(...)
class RunCommandSkill(BaseSkill):
    name = "run_command"
    description = "Terminalde komut çalıştırır (echo, ls, dir vb.)"
    args_schema = RunCommandInput
    def execute(self, command: str):
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return result.stdout if result.stdout else (result.stderr if result.stderr else "Komut calisti (Cikti yok)")
"""
    rc_schema = {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}
    add_skill("run_command", "Sistem terminalinde bash/cmd komutu çalıştırır.", rc_schema, rc_code)

    # 3. API REQUEST
    api_code = """
import requests
from pydantic import BaseModel, Field
from core.base import BaseSkill
class ApiRequestInput(BaseModel):
    url: str = Field(...)
    method: str = Field(default="GET")
class ApiRequestSkill(BaseSkill):
    name = "api_request"
    description = "Verilen URL'ye HTTP isteği atıp veriyi JSON veya metin olarak çeker."
    args_schema = ApiRequestInput
    def execute(self, url: str, method: str = "GET"):
        res = requests.request(method=method, url=url, timeout=15)
        res.raise_for_status()
        try: return res.json()
        except: return res.text
"""
    api_schema = {"type": "object", "properties": {"url": {"type": "string"}, "method": {"type": "string"}}, "required": ["url"]}
    add_skill("api_request", "Web'den (API/URL) güncel veri çeker.", api_schema, api_code)


registry = SkillRegistry()
registry.build_catalog()

# --- MODELLER ---
class AgentRequest(BaseModel):
    prompt: str

class WorkflowStep(BaseModel):
    step_id: str
    skill_name: str
    inputs: Dict[str, Any]

class WorkflowRunRequest(BaseModel):
    steps: List[WorkflowStep]

class GithubImportRequest(BaseModel):
    url: str

# --- ENDPOINT'LER ---
@app.get("/api/skills")
def get_skills():
    registry.build_catalog() 
    return registry.catalog

@app.post("/api/skills/import")
def import_skill_from_github(request: GithubImportRequest):
    """Github URL'sinden Python kodunu indirir, analiz eder ve veritabanına ekler."""
    url = request.url
    # Normal github linki verildiyse raw (ham kod) linkine çevir
    if "github.com" in url and "/blob/" in url:
        url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

    try:
        # Kodu internetten çek
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        python_code = res.text

        # Kodu sanal bir modülde çalıştırarak analiz et
        module = types.ModuleType("temp_github_module")
        exec(python_code, module.__dict__)

        # İçindeki BaseSkill sınıfını bul
        skill_instance = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseSkill) and attr is not BaseSkill:
                skill_instance = attr()
                break

        if not skill_instance:
            raise HTTPException(status_code=400, detail="Kod içinde 'BaseSkill' sınıfından türeyen bir yetenek bulunamadı.")

        # Yeteneğin bilgilerini Pydantic'ten otomatik çek
        name = skill_instance.name
        description = skill_instance.description
        schema = skill_instance.args_schema.model_json_schema() # Pydantic mucizesi!

        # Veritabanına Kaydet
        add_skill(name, description, schema, python_code)
        
        # Sistemi Güncelle
        registry.build_catalog()

        return {"status": "success", "message": f"'{name}' yeteneği başarıyla yüklendi!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İndirme veya analiz hatası: {str(e)}")

@app.post("/api/agent/plan")
def create_plan(request: AgentRequest):
    active_model = os.getenv("ACTIVE_MODEL", "gpt-4o-mini")
    relevant_skills = registry.search_skills(query=request.prompt, top_k=5)
    
    loaded_skills =[registry.load_skill(s) for s in relevant_skills]
    agent = SkillAgent(skills=loaded_skills, model_name=active_model)
    plan = agent.plan_workflow(user_prompt=request.prompt)
    
    if not plan: raise HTTPException(status_code=500, detail="Plan oluşturulamadı.")
    return {"status": "success", "model_used": active_model, "workflow_plan": plan}

@app.post("/api/workflow/run")
def run_workflow(request: WorkflowRunRequest):
    flow = Workflow()
    for step in request.steps:
        skill_data = next((s for s in registry.catalog if s["name"] == step.skill_name), None)
        if not skill_data:
            raise HTTPException(status_code=400, detail=f"Yetenek DB'de yok: {step.skill_name}")
        skill_instance = registry.load_skill(skill_data)
        flow.add_step(step_id=step.step_id, skill=skill_instance, inputs=step.inputs)
    return flow.run()