import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import threading
import time
import random
import json

class TicketHelperGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("抢票助手 V5.0")
        self.window.geometry("1200x900")
        self.window.config(bg="#e3f2fd")  # 蓝色背景
        self.window.resizable(False, False)  # 禁止调整窗口大小

        # 设置主题样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 14), padding=10, relief="flat", background="#3498db", foreground="white", width=20)
        self.style.map("TButton", background=[('active', '#2980b9')])

        self.style.configure("TCheckbutton", font=("Arial", 12), foreground="#333", background="#e3f2fd")
        self.style.configure("TLabel", font=("Arial", 12), foreground="#333", background="#e3f2fd")
        
        # 创建菜单栏
        self.create_menus()

        # 创建UI组件
        self.create_widgets()

    def create_menus(self):
        menu_bar = tk.Menu(self.window)

        # 文件菜单
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="保存配置", command=self.save_config)
        file_menu.add_command(label="加载配置", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.window.quit)
        menu_bar.add_cascade(label="文件", menu=file_menu)

        # 帮助菜单
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menu_bar.add_cascade(label="帮助", menu=help_menu)

        self.window.config(menu=menu_bar)

    def create_widgets(self):
        # 创建主框架
        main_frame = tk.Frame(self.window, bg="#e3f2fd")
        main_frame.place(relwidth=1, relheight=1)

        # 创建标题
        self.title_label = ttk.Label(main_frame, text="抢票助手", font=("Arial", 30, 'bold'), foreground="#2c3e50", background="#e3f2fd")
        self.title_label.grid(row=0, column=0, columnspan=4, pady=30)

        # -------------------------- 登录区 --------------------------

        login_frame = tk.LabelFrame(main_frame, text="登录信息", font=("Arial", 14), bg="#ffffff", fg="#333", padx=10, pady=10)
        login_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.url_label = ttk.Label(login_frame, text="票务页面 URL", background="#ffffff", font=("Arial", 12))
        self.url_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.url_entry = ttk.Entry(login_frame, font=("Arial", 12), width=40)
        self.url_entry.grid(row=0, column=1, padx=10, pady=5)

        self.time_label = ttk.Label(login_frame, text="抢票时间 (HH:MM:SS)", background="#ffffff", font=("Arial", 12))
        self.time_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.time_entry = ttk.Entry(login_frame, font=("Arial", 12), width=40)
        self.time_entry.grid(row=1, column=1, padx=10, pady=5)

        # -------------------------- 场次管理区 --------------------------

        session_frame = tk.LabelFrame(main_frame, text="场次管理", font=("Arial", 14), bg="#ffffff", fg="#333", padx=10, pady=10)
        session_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        self.session_label = ttk.Label(session_frame, text="选择场次", background="#ffffff", font=("Arial", 12))
        self.session_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.session_listbox = tk.Listbox(session_frame, font=("Arial", 12), selectmode=tk.MULTIPLE, height=6)
        # 模拟一些场次
        for i in range(1, 21):
            self.session_listbox.insert(tk.END, f"场次 {i}")
        self.session_listbox.grid(row=1, column=0, padx=10, pady=5)

        # -------------------------- 代理设置区 --------------------------

        proxy_frame = tk.LabelFrame(main_frame, text="代理设置", font=("Arial", 14), bg="#ffffff", fg="#333", padx=10, pady=10)
        proxy_frame.grid(row=2, column=1, padx=20, pady=10, sticky="nsew")

        self.proxy_check_var = tk.BooleanVar()
        self.proxy_check = ttk.Checkbutton(proxy_frame, text="启用代理 IP", variable=self.proxy_check_var)
        self.proxy_check.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.proxy_ip_label = ttk.Label(proxy_frame, text="代理 IP (可选)", background="#ffffff", font=("Arial", 12))
        self.proxy_ip_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.proxy_ip_entry = ttk.Entry(proxy_frame, font=("Arial", 12), width=40)
        self.proxy_ip_entry.grid(row=1, column=1, padx=10, pady=5)

        self.proxy_port_label = ttk.Label(proxy_frame, text="代理端口", background="#ffffff", font=("Arial", 12))
        self.proxy_port_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.proxy_port_entry = ttk.Entry(proxy_frame, font=("Arial", 12), width=40)
        self.proxy_port_entry.grid(row=2, column=1, padx=10, pady=5)

        # -------------------------- 任务控制区 --------------------------

        task_control_frame = tk.LabelFrame(main_frame, text="任务控制", font=("Arial", 14), bg="#ffffff", fg="#333", padx=10, pady=10)
        task_control_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

        self.auto_buy_check_var = tk.BooleanVar()
        self.auto_buy_check = ttk.Checkbutton(task_control_frame, text="启用自动抢票", variable=self.auto_buy_check_var)
        self.auto_buy_check.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.start_button = ttk.Button(task_control_frame, text="开始抢票", command=self.start_ticket_task)
        self.start_button.grid(row=1, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(task_control_frame, text="停止任务", command=self.stop_ticket_task, state=tk.DISABLED)
        self.stop_button.grid(row=1, column=1, padx=10, pady=10)

        self.restart_button = ttk.Button(task_control_frame, text="重试任务", command=self.retry_ticket_task, state=tk.DISABLED)
        self.restart_button.grid(row=1, column=2, padx=10, pady=10)

        # -------------------------- 状态栏 --------------------------

        status_frame = tk.Frame(main_frame, bg="#e3f2fd")
        status_frame.grid(row=3, column=0, columnspan=4, padx=20, pady=10, sticky="nsew")

        self.status_label = ttk.Label(status_frame, text="当前状态: 未开始", font=("Arial", 12), background="#e3f2fd", foreground="#2c3e50")
        self.status_label.grid(row=0, column=0, padx=10)

        self.progress_bar = ttk.Progressbar(status_frame, length=200, mode="determinate", maximum=100)
        self.progress_bar.grid(row=0, column=1, padx=10)

        self.progress_label = ttk.Label(status_frame, text="进度: 0%", font=("Arial", 12), background="#e3f2fd", foreground="#2c3e50")
        self.progress_label.grid(row=0, column=2, padx=10)

        # -------------------------- 日志区域 --------------------------

        log_frame = tk.LabelFrame(main_frame, text="日志输出", font=("Arial", 14), bg="#ffffff", fg="#333", padx=10, pady=10)
        log_frame.grid(row=4, column=0, columnspan=4, padx=20, pady=10, sticky="nsew")

        self.log_text = tk.Text(log_frame, height=10, width=90, font=("Arial", 12), wrap=tk.WORD, bg="#f8f9fa", state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, padx=10, pady=5)

    def start_ticket_task(self):
        self.log("任务开始！")
        self.status_label.config(text="当前状态: 抢票进行中")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.restart_button.config(state=tk.NORMAL)

        # 任务逻辑模拟
        self.task_thread = threading.Thread(target=self.simulate_ticket_task)
        self.task_thread.start()

    def stop_ticket_task(self):
        self.log("任务已停止！")
        self.status_label.config(text="当前状态: 任务已停止")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)
        # 任务停止逻辑
        if hasattr(self, 'task_thread') and self.task_thread.is_alive():
            self.task_thread.join()

    def retry_ticket_task(self):
        self.log("正在重试任务...")
        self.start_ticket_task()

    def simulate_ticket_task(self):
        # 模拟任务执行，更新进度条
        for i in range(1, 101):
            time.sleep(0.1)  # 模拟延迟
            self.progress_bar["value"] = i
            self.progress_label.config(text=f"进度: {i}%")
            self.window.update()

        self.log("任务完成！")
        self.status_label.config(text="当前状态: 任务完成")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.NORMAL)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.yview(tk.END)

    def save_config(self):
        config_data = {
            "url": self.url_entry.get(),
            "time": self.time_entry.get(),
            "proxy_ip": self.proxy_ip_entry.get(),
            "proxy_port": self.proxy_port_entry.get(),
            "auto_buy": self.auto_buy_check_var.get(),
            "sessions": self.session_listbox.curselection()
        }
        with open("config.json", "w") as f:
            json.dump(config_data, f)
        self.log("配置已保存！")

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                config_data = json.load(f)
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, config_data["url"])
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, config_data["time"])
            self.proxy_ip_entry.delete(0, tk.END)
            self.proxy_ip_entry.insert(0, config_data["proxy_ip"])
            self.proxy_port_entry.delete(0, tk.END)
            self.proxy_port_entry.insert(0, config_data["proxy_port"])
            self.auto_buy_check_var.set(config_data["auto_buy"])
            for idx in config_data["sessions"]:
                self.session_listbox.select_set(idx)
            self.log("配置已加载！")
        except FileNotFoundError:
            messagebox.showerror("错误", "未找到配置文件！")

    def show_about(self):
        messagebox.showinfo("关于", "抢票助手 V5.0\n\n开发者: Your Name\n\n说明: 仅娱乐使用，没有实际效果")


# 创建并启动界面
if __name__ == "__main__":
    app = TicketHelperGUI()
    app.window.mainloop()
