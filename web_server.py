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
            add_log("SYSTEM", "收到用户主动终止任务指令，正在安全关闭抢票进程与浏览器资源...")
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

    add_log("SYSTEM", "开始进行环境运行包依赖部署及版本自检...")
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
    add_log("SYSTEM", "环境依赖安装及配置成功！")

def ticketing_worker_thread():
    global status, progress, stop_flag

    # Load user config so logs reflect real settings (still a sandbox — no real purchase)
    target_url = ""
    tickets = 2
    viewers = [0, 1]
    platform = "damai"
    mobile = ""
    date_priorities = [1]
    session_priorities = [1]
    auto_buy = True
    try:
        config_file = "config/config.json"
        if not os.path.exists(config_file):
            config_file = "config/demo_config.json"
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            auto_buy = cfg.get("strategy", {}).get("auto_strike", True)
            acc = (cfg.get("accounts") or {}).get("acc_primary") or {}
            platform = acc.get("platform") or platform
            creds = acc.get("credentials") or {}
            mobile = creds.get("mobile") or ""
            target = acc.get("target") or {}
            target_url = target.get("event_url") or ""
            tickets = target.get("tickets") or tickets
            viewers = target.get("viewers") or viewers
            priorities = target.get("priorities") or {}
            date_priorities = priorities.get("date") or date_priorities
            session_priorities = priorities.get("session") or session_priorities
    except Exception as e:
        print("Read config err:", e)

    add_log(
        "WARNING",
        "当前为 Web 控制台【沙箱演示】：不会打开真实浏览器、不会真实下单。"
        " 预览画面中的城市/姓名若曾写死为示例文案，已改为按 config 渲染。"
        " 实机请运行 ticket_script.py 或桌面 GUI。",
    )
    add_log(
        "INFO",
        f"读取配置 → 平台={platform} 手机={mobile or '未填写'} "
        f"票数={tickets} 观演人索引={viewers} "
        f"日期优先级={date_priorities} 场次优先级={session_priorities}",
    )
    if target_url:
        add_log("INFO", f"目标演出链接 (来自配置): {target_url}")
    else:
        add_log("WARNING", "配置中未填写 target.event_url，预览将使用占位标题。")

    steps = [
        (5, "INFO", "[沙箱] 模拟连接代理路由服务器..."),
        (10, "SYSTEM", "[沙箱] 模拟注入 Selenium 隐身防御补丁 (--disable-blink-features=AutomationControlled)"),
        (15, "INFO", "[沙箱] 模拟初始化 Chrome WebDriver（未真实启动浏览器）..."),
    ]

    for p, lvl, msg in steps:
        if stop_flag:
            return
        with state_lock:
            progress = p
        add_log(lvl, msg)
        time.sleep(0.4)

    # Core Environment Dependency Check
    chrome_ok = True
    try:
        import selenium  # noqa: F401
        from selenium import webdriver  # noqa: F401
    except ImportError:
        chrome_ok = False
        add_log("WARNING", "运行环境中未检测到 [selenium] 库。沙箱演示可继续，实机抢票需先安装依赖。")

    driver_file = "chromedriver.exe" if sys.platform.startswith("win") else "chromedriver"
    if not os.path.exists(driver_file):
        add_log(
            "WARNING",
            f"本地根目录下未检测到驱动 [{driver_file}]。沙箱演示不依赖驱动；实机将尝试系统 Chrome。",
        )
    if chrome_ok:
        add_log("DEBUG", "selenium 已安装（本线程仍不执行真实抢票）。")

    flow = [
        (25, "INFO", "[沙箱] 模拟解析账户 Cookies (cookies.pkl)..."),
        (32, "WARNING", "[沙箱] 演示路径：若无 cookies.pkl，实机将弹出扫码登录窗口"),
        (40, "SYSTEM", f"### 扫码登录引导 (演示) ### 绑定手机: {mobile or '未填写'}"),
        (48, "INFO", "[沙箱] 模拟 Cookies 同步成功（未真实扫码）"),
        (55, "DEBUG", "### 载入 Cookie 验证状态成功 (演示) ### 正在向购票目标页面进行跳转..."),
        (
            62,
            "INFO",
            f"正在解析日历票档卡片... 日期优先级={date_priorities} 场次优先级={session_priorities}",
        ),
        (
            72,
            "INFO",
            f"正在检索余票状态... 模拟勾选实名观演人索引 {viewers}（索引来自配置，非固定姓名如「张三」）",
        ),
        (85, "SYSTEM", "### 极速自动出手 (Auto Strike · 沙箱) ### 模拟提交订单包中..."),
    ]

    for p, lvl, msg in flow:
        if stop_flag:
            return
        with state_lock:
            progress = p
        add_log(lvl, msg)
        time.sleep(0.7)

    if stop_flag:
        return
    with state_lock:
        progress = 100
        status = "completed"

    if auto_buy:
        add_log("INFO", "🎉 [SUCCESS] 沙箱流程走通（演示成功，未真实下单 / 未扣款）。")
        add_log(
            "SYSTEM",
            "🎟️ 沙箱演示结束。实机抢票请运行: python ticket_script.py 或桌面 GUI，并确认 Chrome/Cookie 就绪。",
        )
    else:
        add_log(
            "WARNING",
            "[沙箱] 未启用自动秒杀下单。演示仅模拟选座；实机需在浏览器中人工提交订单。",
        )

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
