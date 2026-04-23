import os
import subprocess

def read_file(path):
    """Belirtilen yoldaki dosyanın içeriğini okur."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Hata: {str(e)}"

def write_file(path, content):
    """Yeni dosya oluşturur veya var olanın üzerine yazar."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Dosya başarıyla kaydedildi: {path}"
    except Exception as e:
        return f"Hata: {str(e)}"

def run_command(command):
   
    """Terminalde komut çalıştırır. Sunucu gibi işlemleri non-blocking başlatır."""
    try:
        # Eğer komut 'uvicorn' veya 'python' gibi sürekli çalışan bir şeyse
        # Onu arka planda başlatıp kontrolü geri almalıyız.
        # Basitlik için şimdilik standart çıktıya odaklanalım:
        
        process = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        # Kısa bir süre bekle, eğer hemen hata verirse yakala
        try:
            stdout, stderr = process.communicate(timeout=2)
            return f"Çıktı: {stdout}\nHata: {stderr}"
        except subprocess.TimeoutExpired:
            # Eğer 2 saniye içinde kapanmadıysa, muhtemelen bir sunucudur ve çalışıyordur.
            return f"İşlem arka planda başarıyla başlatıldı (PID: {process.pid})"
            
    except Exception as e:
        return f"Hata: {str(e)}"




def replace_in_file(path, search_text, replace_text):
    """Dosya içindeki belirli bir metni bulur ve yenisiyle değiştirir."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if search_text not in content:
            return f"Hata: Değiştirilmek istenen metin dosyada bulunamadı."
        
        new_content = content.replace(search_text, replace_text)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"Dosya başarıyla güncellendi: {path}"
    except Exception as e:
        return f"Hata: {str(e)}"

def list_files(directory="."):
    """Mevcut klasördeki tüm dosya ve klasörleri listeler (Hiyerarşik)."""
    try:
        output = []
        for root, dirs, files in os.walk(directory):
            # venv, .git gibi kalabalık klasörleri gizleyelim
            if 'venv' in root or '.git' in root or '__pycache__' in root:
                continue
            
            level = root.replace(directory, '').count(os.sep)
            indent = ' ' * 4 * level
            output.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                output.append(f"{sub_indent}{f}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Hata: {str(e)}"


# Bu kısım LLM'e araçları tanıtmamız için gereken şemadır
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Bir dosyanın içeriğini okumak için kullanılır.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Yeni dosya oluşturmak veya kodu güncellemek için kullanılır.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Terminalde komut çalıştırmak (örn: pip install, python run) için kullanılır.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "replace_in_file",
        "description": "Bir dosya içindeki belirli bir metin bloğunu bulur ve yenisiyle değiştirir. Tüm dosyayı yeniden yazmak yerine sadece belirli kısımları güncellemek için kullanılır.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Güncellenecek dosyanın yolu."
                },
                "search_text": {
                    "type": "string",
                    "description": "Dosya içinde aranacak olan mevcut metin bloğu."
                },
                "replace_text": {
                    "type": "string",
                    "description": "Mevcut metnin yerine geçecek olan yeni metin."
                }
            },
            "required": ["path", "search_text", "replace_text"]
        }
    } 
    },
    {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "Proje dizin yapısını görmek için kullanılır. Agent bu sayede hangi dosyalar üzerinde çalışabileceğini anlar.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "default": "."}
            }
        }
    }
}
]