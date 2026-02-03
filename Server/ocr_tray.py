import sys
import os
import threading
import json
import logging
import time
import importlib.metadata
import webbrowser
import psutil
import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as item

# --- 🟢 补丁：修复 werkzeug 版本报错 ---
try:
    _original_version = importlib.metadata.version
    def _patched_version(package_name):
        if package_name.lower() == 'werkzeug':
            return '3.0.0'
        return _original_version(package_name)
    importlib.metadata.version = _patched_version
except Exception:
    pass

# --- 1. 核心：路径智能识别 (修复版) ---
if getattr(sys, 'frozen', False):
    # ✅ 如果是打包后的 exe：
    # sys.executable 是 exe 文件的全路径
    # 我们取它的目录，就是 exe 所在的文件夹
    base_path = os.path.dirname(sys.executable)
else:
    # 📝 如果是脚本运行：
    # 取当前脚本所在目录
    base_path = os.path.dirname(os.path.abspath(__file__))

# 将当前目录加入 path，防止找不到同级模块
sys.path.append(base_path)

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    from wechat_ocr.ocr_manager import OcrManager, OCR_MAX_TASK_ID
except ImportError as e:
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, f"缺少依赖: {e}", "启动错误", 16)
    sys.exit(1)

# --- 2. 配置 ---
# 强制指定 wxocr 文件夹必须在 exe 旁边
WECHAT_LIB_DIR = os.path.join(base_path, "wxocr")
WECHAT_OCR_DIR = os.path.join(WECHAT_LIB_DIR, "WeChatOCR.exe")
PORT = 12345

app = Flask(__name__)
CORS(app)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# --- 3. OCR 核心逻辑 ---
ocr_lock = threading.Lock()
ocr_event = threading.Event()
global_ocr_result = None
ocr_manager = None

def ocr_callback(img_path: str, results: dict):
    global global_ocr_result
    global_ocr_result = results
    ocr_event.set()

def start_ocr_engine():
    global ocr_manager
    
    # 🔍 检查文件是否存在，不存在则弹窗提示 (方便调试)
    if not os.path.exists(WECHAT_OCR_DIR):
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, f"找不到文件:\n{WECHAT_OCR_DIR}\n\n请确保 wxocr 文件夹和 exe 在一起！", "文件缺失", 16)
        return False

    try:
        ocr_manager = OcrManager(WECHAT_LIB_DIR)
        ocr_manager.SetExePath(WECHAT_OCR_DIR)
        ocr_manager.SetUsrLibDir(WECHAT_LIB_DIR)
        ocr_manager.SetOcrResultCallback(ocr_callback)
        ocr_manager.StartWeChatOCR()
        return True
    except Exception as e:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, f"引擎启动失败: {e}", "错误", 16)
        return False

# 启动引擎
start_ocr_engine()

@app.route('/ocr', methods=['POST'])
def run_ocr():
    global global_ocr_result
    data = request.json
    if not data or 'image_path' not in data:
        return jsonify({"error": "Missing image_path"}), 400
    
    img_path = data['image_path'].replace("/", "\\")
    if not os.path.exists(img_path):
        return jsonify({"error": "File not found"}), 404

    width, height = 0, 0
    try:
        with Image.open(img_path) as img:
            width, height = img.size
    except:
        pass

    with ocr_lock:
        ocr_event.clear()
        global_ocr_result = None
        if ocr_manager:
            ocr_manager.DoOCRTask(img_path)
        else:
            # 尝试重启
            start_ocr_engine()
            if ocr_manager:
                ocr_manager.DoOCRTask(img_path)
            else:
                return jsonify({"error": "Engine not running"}), 500
        
        if not ocr_event.wait(timeout=10.0):
            return jsonify({"error": "OCR Timeout"}), 504
            
        items = []
        raw_list = global_ocr_result.get('ocrResult', [])
        for i in raw_list:
            items.append({"text": i['text'], "location": i['location']})

        return jsonify({"code": 200, "width": width, "height": height, "items": items})

# --- 4. 托盘图标逻辑 ---

def create_icon_image():
    width = 64
    height = 64
    color1 = (65, 105, 225) 
    color2 = (255, 255, 255)
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.ellipse((10, 10, 54, 54), fill=color1, outline=color2, width=3)
    dc.rectangle((24, 24, 40, 40), fill=color2)
    return image

def on_quit(icon, item):
    icon.stop()
    try:
        if ocr_manager: ocr_manager.KillWeChatOCR()
    except:
        pass
    os._exit(0)

current_mem_str = "计算中..."

def get_memory_usage():
    try:
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / 1024 / 1024 
        return f"内存: {mem:.1f} MB"
    except:
        return "内存: N/A"

def update_menu_text(icon):
    while True:
        icon.update_menu()
        time.sleep(2)

def setup_tray():
    image = create_icon_image()
    menu = pystray.Menu(
        item('本地微信 OCR', lambda i, it: None, enabled=False),
        pystray.Menu.SEPARATOR,
        item(lambda text: get_memory_usage(), lambda i, it: None, enabled=False),
        pystray.Menu.SEPARATOR,
        item('退出 (Exit)', on_quit)
    )
    icon = pystray.Icon("WeChatOCR", image, "本地微信OCR服务", menu)
    return icon

if __name__ == "__main__":
    flask_thread = threading.Thread(target=lambda: app.run(host='127.0.0.1', port=PORT, debug=False, use_reloader=False))
    flask_thread.daemon = True
    flask_thread.start()

    icon = setup_tray()
    threading.Thread(target=update_menu_text, args=(icon,), daemon=True).start()
    icon.run()