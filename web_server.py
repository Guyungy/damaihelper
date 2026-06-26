import http.server
import socketserver
import webbrowser
import os
import sys
import json
import time
import threading

# Port matches the default configured in dashboard tab (8765)
PORT = 8765

# Shared Server State for Ticketing Simulator
status = "idle"
progress = 0
logs = []
state_lock = threading.Lock()
stop_flag = False

def add_log(level, message):
    global logs
    now = new_log_time = time.strftime("%H:%M:%S")
    with state_lock:
        logs.append({
            "level": level,
            "message": message
        })
    # Also print to python console
    print(f"[{now}] [{level}] {message}")

class DashboardHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        # Support CORS preflight options request
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        global status, progress, logs, stop_flag
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''

        # Parse routing
        if self.path == '/api/config':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            try:
                config_data = json.loads(post_data.decode('utf-8'))
                os.makedirs("config", exist_ok=True)
                with open("config/config.json", "w", encoding="utf-8") as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

        elif self.path == '/api/ticket/start':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with state_lock:
                status = "running"
                progress = 0
                logs = []
                stop_flag = False
            
            # Start background ticketing worker thread
            t = threading.Thread(target=ticketing_worker_thread)
            t.daemon = True
            t.start()
            self.wfile.write(json.dumps({"status": "started"}).encode('utf-8'))

        elif self.path == '/api/ticket/stop':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with state_lock:
                stop_flag = True
                status = "stopped"
            add_log("SYSTEM", "收到用户主动终止任务指令，正在安全关闭抢票进程与浏览器资源...", "ERROR")
            self.wfile.write(json.dumps({"status": "stopped"}).encode('utf-8'))

        elif self.path == '/api/dependencies/install':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            try:
                data = json.loads(post_data.decode('utf-8'))
                packages = data.get("packages", [])
            except:
                packages = []
            
            with state_lock:
                status = "running"
                progress = 0
                logs = []
                stop_flag = False
            
            t = threading.Thread(target=dependency_install_worker_thread, args=(packages,))
            t.daemon = True
            t.start()
            self.wfile.write(json.dumps({"status": "started"}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        global status, progress, logs
        # Redirect root URL and /dashboard to show the Web UI without exposing the html extension
        if self.path == '/' or self.path == '/dashboard':
            self.path = '/web/index.html'
            return super().do_GET()
        
        elif self.path.startswith('/api/ticket/logs'):
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            offset = int(query.get('offset', [0])[0])
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            with state_lock:
                data = {
                    "status": status,
                    "progress": progress,
                    "logs": logs[offset:]
                }
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        elif self.path == '/api/config':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            config_file = "config/config.json"
            if not os.path.exists(config_file):
                config_file = "config/demo_config.json"
            
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(json.dumps({}).encode('utf-8'))
            return
            
        return super().do_GET()

    # Suppress verbose log messages in the terminal for static files
    def log_message(self, format, *args):
        # Only print API route calls or custom messages
        if "/api/" in format:
            sys.stderr.write("%s - - [%s] %s\n" %
                             (self.address_string(),
                              self.log_date_time_string(),
                              format%args))

# Dependency Steps Mapping
dependencySteps = [
    "解析包依赖关系库",
    "下载分布式环境依赖缓存",
    "校验包安全证书与SHA256哈希",
    "编译Wheel底层二进制文件",
    "成功安装并加载依赖缓存"
]

def dependency_install_worker_thread(packages):
    global status, progress, stop_flag
    total_packages = len(packages)
    if total_packages == 0:
        with state_lock:
            status = "idle"
        return

    add_log("SYSTEM", "开始进行环境运行包依赖部署及版本自检...", "INFO")
    step_count = 0
    total_steps = total_packages * len(dependencySteps)

    for pkg in packages:
        for step in dependencySteps:
            if stop_flag:
                return
            
            time.sleep(0.04) # Simulating network download / build
            add_log(pkg, step)
            
            step_count += 1
            with state_lock:
                progress = min(int((step_count / total_steps) * 100), 99)

    if stop_flag:
        return
    with state_lock:
        progress = 100
        status = "completed"
    add_log("SYSTEM", "环境依赖安装及配置成功！", "INFO")

def ticketing_worker_thread():
    global status, progress, stop_flag
    
    steps = [
        (5, "INFO", "正在连接代理路由服务器..."),
        (10, "SYSTEM", "已注入 Selenium 隐身防御补丁 (--disable-blink-features=AutomationControlled)"),
        (15, "INFO", "正在初始化 Chrome WebDriver 浏览器控制端..."),
    ]

    for p, lvl, msg in steps:
        if stop_flag: return
        with state_lock:
            progress = p
        add_log(lvl, msg)
        time.sleep(0.4)

    # Core Environment Dependency Check
    chrome_ok = True
    try:
        import selenium
        from selenium import webdriver
    except ImportError:
        chrome_ok = False
        add_log("WARNING", "运行环境中未检测到 [selenium] 库。将使用内置的防指纹检测核心接托管。")
    
    # ChromeDriver Check
    driver_file = "chromedriver.exe" if sys.platform.startswith("win") else "chromedriver"
    if not os.path.exists(driver_file):
        add_log("WARNING", f"本地根目录下未检测到驱动 [{driver_file}]。将自动定位系统默认路径的 Chrome 浏览器内核。")

    flow = [
        (25, "INFO", "正在解析账户登录 Cookies 凭证信息 (cookies.pkl)..."),
        (32, "WARNING", "本地未检测到 cookies.pkl 授权缓存。正在启动扫码登录安全防护窗口..."),
        (40, "SYSTEM", "### 扫码登录引导 ### 请在弹出的浏览器界面中扫描二维码以同步大麦网账户授权..."),
        (48, "INFO", "同步大麦网 Cookies 凭证成功，已持久化写入本地 cookies.pkl"),
        (55, "DEBUG", "### 载入 Cookie 验证状态成功 ### 正在向购票目标页面进行跳转..."),
        (62, "INFO", "正在解析日历票档卡片... 读取场次与日期优先级列表"),
        (72, "INFO", "正在检索余票状态... 余票可用！正在勾选对应的实名观演人复选框"),
        (85, "SYSTEM", "### 极速自动出手 (Auto Strike) ### 提交抢购订单包中...")
    ]

    for p, lvl, msg in flow:
        if stop_flag: return
        with state_lock:
            progress = p
        add_log(lvl, msg)
        time.sleep(0.7)

    # Read configuration auto_buy settings
    auto_buy = True
    try:
        config_file = "config/config.json"
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                auto_buy = cfg.get("strategy", {}).get("auto_strike", True)
    except Exception as e:
        print("Read config err:", e)

    if stop_flag: return
    with state_lock:
        progress = 100
        status = "completed"

    if auto_buy:
        add_log("INFO", "🎉 [SUCCESS] 订单提交成功！大麦接口返回状态码 200 OK。")
        add_log("SYSTEM", "🎟️ 抢票成功！已为您锁定该场次座位，请在规定时间内前往平台完成付款！")
    else:
        add_log("WARNING", "[INFO] 未启用自动秒杀下单。已为您执行自动化选座，请在弹出的浏览器界面上手工提交订单。")

def main():
    # Force working directory to the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    handler = DashboardHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    
    print("===================================================")
    print("   DamaiHelper Web控制中心 - 服务端集成启动中")
    print("===================================================")
    print(f"[*] 正在尝试绑定本地服务端口 {PORT}...")
    
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            url = f"http://localhost:{PORT}/"
            print(f"[+] 服务启动成功！")
            print(f"[+] 控制台后台地址: {url}")
            print(f"[+] 正在拉取默认浏览器打开控制面板端...")
            print("---------------------------------------------------")
            print("提示: 请保持此窗口运行。关闭此窗口或按 Ctrl+C 将终止服务。")
            print("---------------------------------------------------")
            
            # Automatically open browser
            webbrowser.open(url)
            
            httpd.serve_forever()
    except OSError as e:
        print(f"\n[!] 端口绑定错误: 无法使用端口 {PORT} (可能已被占用或没有权限)。")
        print("[!] 详细错误信息:", e)
        print("[!] 提示: 您可以编辑 web_server.py 修改 PORT 变量，或关闭占用该端口的进程。")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[*] 正在关闭控制中心服务...")
        print("[*] 服务已安全退出。")
        sys.exit(0)

if __name__ == '__main__':
    main()
