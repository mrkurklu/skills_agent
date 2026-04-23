import json
import time
from litellm import completion
from litellm.exceptions import ServiceUnavailableError
# Tools dosyasından tüm fonksiyonları import ettiğimizden emin olalım
from tools import TOOLS_DEFINITION, read_file, write_file, run_command, replace_in_file, list_files

class SkillsAgent:
    def __init__(self, model="gemini/gemini-1.5-flash"):
        self.model = model
        self.history = [
            {"role": "system", "content": "Sen yetenekli bir yazılım mühendisisin. Terminali ve dosya sistemini kullanarak verilen görevleri tamamla. Her adımda ne yaptığını açıkla."}
        ]
        self.load_history() # Geçmişi başlangıçta yükle

    def save_history(self):
        with open("chat_history.json", "w") as f:
            json.dump(self.history, f, indent=4)

    def load_history(self):
        try:
            with open("chat_history.json", "r") as f:
                self.history = json.load(f)
        except FileNotFoundError:
            pass # Dosya yoksa, varsayılan geçmişi kullan

    def execute(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        
        while True:
            try:
                response = completion(
                    model=self.model,
                    messages=self.history,
                    tools=TOOLS_DEFINITION,
                    tool_choice="auto"
                )
            except ServiceUnavailableError:
                print("\n[!] Sunucu yoğun, 3 saniye sonra tekrar deneniyor...")
                time.sleep(3)
                continue
            
            response_message = response.choices[0].message
            self.history.append(response_message)

            # Eğer LLM bir araç kullanmak istemiyorsa döngüden çık
            if not response_message.tool_calls:
                self.save_history() # Geçmişi kaydet
                return response_message.content

            # Araç kullanma talebi varsa döngü başlar
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                print(f"-> [ARAÇ ÇALIŞTIRILIYOR]: {function_name}")
                
                # Araçları eşleştirelim
                if function_name == "read_file":
                    result = read_file(**args)
                elif function_name == "write_file":
                    result = write_file(**args)
                elif function_name == "run_command":
                    result = run_command(**args)
                elif function_name == "replace_in_file":
                    result = replace_in_file(**args)
                elif function_name == "list_files":
                    result = list_files(**args)
                else:
                    result = "Bilinmeyen araç."

                # Sonucu geçmişe ekle
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": result
                })
