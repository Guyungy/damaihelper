import json
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class TicketHelperGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("抢票助手 V5.0")
        self.window.geometry("1280x900")
        self.window.config(bg="#e3f2fd")
        self.window.resizable(False, False)

        self.style = ttk.Style()
        self.style.configure(
            "TButton",
            font=("Arial", 12),
            padding=8,
            relief="flat",
            background="#3498db",
            foreground="white",
        )
        self.style.map("TButton", background=[("active", "#2980b9")])
        self.style.configure("TCheckbutton", font=("Arial", 11), foreground="#333")
        self.style.configure("TLabel", font=("Arial", 11), foreground="#333")
        self.style.configure("TLabelframe.Label", font=("Arial", 12, "bold"))

        self.create_menus()
        self.create_widgets()

    def create_menus(self):
        menu_bar = tk.Menu(self.window)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="保存配置", command=self.save_config)
        file_menu.add_command(label="加载配置", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.window.quit)
        menu_bar.add_cascade(label="文件", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menu_bar.add_cascade(label="帮助", menu=help_menu)

        self.window.config(menu=menu_bar)

    def create_widgets(self):
        main_frame = tk.Frame(self.window, bg="#e3f2fd")
        main_frame.place(relwidth=1, relheight=1)

        title = ttk.Label(
            main_frame,
            text="抢票助手配置中心",
            font=("Arial", 26, "bold"),
            foreground="#2c3e50",
            background="#e3f2fd",
        )
        title.pack(pady=20)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        self.create_global_tab()
        self.create_account_tab()
        self.create_strategy_tab()
        self.create_monitor_tab()
        self.create_notification_tab()
        self.create_plugin_tab()
        self.create_dependency_tab()

        control_frame = tk.LabelFrame(
            main_frame,
            text="任务控制",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#333",
            padx=10,
            pady=10,
        )
        control_frame.pack(fill=tk.X, padx=20, pady=5)

        self.auto_buy_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            control_frame,
            text="启用自动抢票",
            variable=self.auto_buy_check_var,
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.start_button = ttk.Button(control_frame, text="开始抢票", command=self.start_ticket_task)
        self.start_button.grid(row=0, column=1, padx=10)
        self.stop_button = ttk.Button(
            control_frame,
            text="停止任务",
            command=self.stop_ticket_task,
            state=tk.DISABLED,
        )
        self.stop_button.grid(row=0, column=2, padx=10)
        self.restart_button = ttk.Button(
            control_frame,
            text="重试任务",
            command=self.retry_ticket_task,
            state=tk.DISABLED,
        )
        self.restart_button.grid(row=0, column=3, padx=10)

        status_frame = tk.Frame(main_frame, bg="#e3f2fd")
        status_frame.pack(fill=tk.X, padx=20, pady=5)

        self.status_label = ttk.Label(
            status_frame,
            text="当前状态: 未开始",
            font=("Arial", 11),
            background="#e3f2fd",
            foreground="#2c3e50",
        )
        self.status_label.grid(row=0, column=0, padx=10)

        self.progress_bar = ttk.Progressbar(status_frame, length=240, mode="determinate", maximum=100)
        self.progress_bar.grid(row=0, column=1, padx=10)

        self.progress_label = ttk.Label(
            status_frame,
            text="进度: 0%",
            font=("Arial", 11),
            background="#e3f2fd",
            foreground="#2c3e50",
        )
        self.progress_label.grid(row=0, column=2, padx=10)

        log_frame = tk.LabelFrame(
            main_frame,
            text="日志输出",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#333",
            padx=10,
            pady=10,
        )
        log_frame.pack(fill=tk.BOTH, padx=20, pady=10)

        self.log_text = tk.Text(
            log_frame,
            height=8,
            width=120,
            font=("Arial", 11),
            wrap=tk.WORD,
            bg="#f8f9fa",
            state=tk.DISABLED,
        )
        self.log_text.grid(row=0, column=0, padx=10, pady=5)

    def create_global_tab(self):
        tab = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(tab, text="全局设置")

        self.global_log_level = self._add_labeled_combo(
            tab,
            0,
            "日志等级",
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            default="DEBUG",
        )
        self.global_timezone = self._add_labeled_entry(tab, 1, "时区", "Asia/Shanghai")
        self.global_ntp_servers = self._add_labeled_entry(tab, 2, "NTP服务器(逗号分隔)", "time.google.com,ntp.aliyun.com")

        dashboard_frame = tk.LabelFrame(tab, text="Dashboard", bg="#ffffff", padx=10, pady=10)
        dashboard_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        dashboard_frame.columnconfigure(1, weight=1)

        self.dashboard_enable = tk.BooleanVar(value=True)
        ttk.Checkbutton(dashboard_frame, text="启用可视化面板", variable=self.dashboard_enable).grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.dashboard_host = self._add_labeled_entry(dashboard_frame, 1, "面板地址", "0.0.0.0")
        self.dashboard_port = self._add_labeled_entry(dashboard_frame, 2, "面板端口", "8765")

    def create_account_tab(self):
        tab = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(tab, text="账户配置")

        self.account_platform = self._add_labeled_combo(
            tab,
            0,
            "平台",
            ["taopiaopiao", "maoyan", "showstart", "piaoxingqiu", "others"],
            default="taopiaopiao",
        )
        self.account_mobile = self._add_labeled_entry(tab, 1, "手机号", "")
        self.account_password = self._add_labeled_entry(tab, 2, "密码", "")
        self.account_otp = self._add_labeled_entry(tab, 3, "OTP Secret(可选)", "")

        target_frame = tk.LabelFrame(tab, text="目标信息", bg="#ffffff", padx=10, pady=10)
        target_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        target_frame.columnconfigure(1, weight=1)

        self.target_event_url = self._add_labeled_entry(target_frame, 0, "演出链接", "")
        self.target_date_priorities = self._add_labeled_entry(target_frame, 1, "日期优先级(逗号)", "1,2")
        self.target_session_priorities = self._add_labeled_entry(target_frame, 2, "场次优先级(逗号)", "1")
        self.target_price_range = self._add_labeled_combo(
            target_frame,
            3,
            "票价策略",
            ["lowest_to_highest", "highest_to_lowest", "custom"],
            default="lowest_to_highest",
        )
        self.target_tickets = self._add_labeled_entry(target_frame, 4, "购票数量", "2")
        self.target_viewers = self._add_labeled_entry(target_frame, 5, "观影人索引(逗号)", "0,1")

        proxy_frame = tk.LabelFrame(tab, text="代理设置", bg="#ffffff", padx=10, pady=10)
        proxy_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        proxy_frame.columnconfigure(1, weight=1)

        self.proxy_type = self._add_labeled_combo(
            proxy_frame,
            0,
            "代理类型",
            ["socks5", "http", "https"],
            default="socks5",
        )
        self.proxy_addr = self._add_labeled_entry(proxy_frame, 1, "代理地址(user:pass@host:port)", "")
        self.proxy_rotate = self._add_labeled_entry(proxy_frame, 2, "轮换间隔(秒)", "300")

    def create_strategy_tab(self):
        tab = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(tab, text="策略设置")

        self.strategy_auto = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text="启用自动出手", variable=self.strategy_auto, background="#ffffff").grid(
            row=0, column=0, sticky="w", padx=10, pady=5
        )
        self.strategy_time = self._add_labeled_entry(tab, 1, "开抢时间(ISO)", "2026-01-25T12:00:00")
        self.strategy_preheat = self._add_labeled_entry(tab, 2, "预热阶段(秒,逗号)", "5.0,2.0,0.5")

        self.strategy_ai = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text="启用AI决策", variable=self.strategy_ai, background="#ffffff").grid(
            row=3, column=0, sticky="w", padx=10, pady=5
        )
        self.strategy_ai_model = self._add_labeled_entry(tab, 4, "AI模型路径", "models/lstm_onnx.onnx")
        self.strategy_max_retries = self._add_labeled_entry(tab, 5, "最大重试次数", "180")
        self.strategy_retry_backoff = self._add_labeled_combo(
            tab,
            6,
            "重试策略",
            ["exponential", "fixed"],
            default="exponential",
        )

    def create_monitor_tab(self):
        tab = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(tab, text="监控设置")

        self.monitor_enable = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text="启用库存监控", variable=self.monitor_enable, background="#ffffff").grid(
            row=0, column=0, sticky="w", padx=10, pady=5
        )
        self.monitor_poll_interval = self._add_labeled_entry(tab, 1, "轮询间隔(秒)", "1.5")

        trigger_frame = tk.LabelFrame(tab, text="触发条件(每行一条)", bg="#ffffff", padx=10, pady=10)
        trigger_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self.monitor_triggers = tk.Text(trigger_frame, height=5, width=60, font=("Arial", 10))
        self.monitor_triggers.insert(tk.END, "price_drop > 10%\ntickets_added > 0\nstatus_change: soldout -> available")
        self.monitor_triggers.pack(fill=tk.X)

    def create_notification_tab(self):
        tab = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(tab, text="通知设置")

        telegram_frame = tk.LabelFrame(tab, text="Telegram", bg="#ffffff", padx=10, pady=10)
        telegram_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        telegram_frame.columnconfigure(1, weight=1)

        self.telegram_token = self._add_labeled_entry(telegram_frame, 0, "Bot Token", "")
        self.telegram_chat = self._add_labeled_entry(telegram_frame, 1, "Chat ID", "")

        email_frame = tk.LabelFrame(tab, text="Email", bg="#ffffff", padx=10, pady=10)
        email_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        email_frame.columnconfigure(1, weight=1)

        self.email_smtp = self._add_labeled_entry(email_frame, 0, "SMTP地址", "smtp.example.com:465")
        self.email_user = self._add_labeled_entry(email_frame, 1, "邮箱账号", "")
        self.email_pass = self._add_labeled_entry(email_frame, 2, "邮箱密码", "")
        self.email_recipients = self._add_labeled_entry(email_frame, 3, "收件人(逗号)", "user@domain.com")

    def create_plugin_tab(self):
        tab = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(tab, text="插件扩展")

        ttk.Label(tab, text="自定义插件(逗号分隔)", background="#ffffff").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.plugins_custom = ttk.Entry(tab, width=60, font=("Arial", 11))
        self.plugins_custom.insert(0, "my_adapter.py,extra_notifier.py")
        self.plugins_custom.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    def create_dependency_tab(self):
        tab = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(tab, text="依赖管理")

        description = (
            "本项目用于模拟与学习。可在此配置“伪安装”依赖清单，\n"
            "点击按钮将以日志方式模拟安装流程，不会真实下载或执行安装。"
        )
        ttk.Label(tab, text=description, background="#ffffff", foreground="#555").grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w"
        )

        deps_frame = tk.LabelFrame(tab, text="依赖清单(每行一条)", bg="#ffffff", padx=10, pady=10)
        deps_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self.dependency_list = tk.Text(deps_frame, height=8, width=70, font=("Arial", 10))
        self.dependency_list.insert(
            tk.END,
            "undetected-chromedriver==2.0\n"
            "aiohttp>=3.8\n"
            "httpx>=0.25\n"
            "scikit-learn\n"
            "onnxruntime\n"
            "prometheus-client\n"
            "grafana-api\n"
            "celery\n"
            "redis\n"
            "pymongo\n",
        )
        self.dependency_list.pack(fill=tk.X)

        self.dep_auto_install = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab,
            text="启动时自动模拟安装",
            variable=self.dep_auto_install,
            background="#ffffff",
        ).grid(row=2, column=0, padx=10, pady=5, sticky="w")

        install_button = ttk.Button(tab, text="模拟安装依赖", command=self.simulate_dependency_install)
        install_button.grid(row=2, column=1, padx=10, pady=5, sticky="e")

    def _add_labeled_entry(self, parent, row, label, default):
        ttk.Label(parent, text=label, background=parent.cget("bg")).grid(
            row=row, column=0, padx=10, pady=6, sticky="w"
        )
        entry = ttk.Entry(parent, width=48, font=("Arial", 11))
        entry.grid(row=row, column=1, padx=10, pady=6, sticky="ew")
        if default:
            entry.insert(0, default)
        return entry

    def _add_labeled_combo(self, parent, row, label, values, default=None):
        ttk.Label(parent, text=label, background=parent.cget("bg")).grid(
            row=row, column=0, padx=10, pady=6, sticky="w"
        )
        combo = ttk.Combobox(parent, values=values, state="readonly", width=45, font=("Arial", 11))
        combo.grid(row=row, column=1, padx=10, pady=6, sticky="ew")
        if default:
            combo.set(default)
        elif values:
            combo.set(values[0])
        return combo

    def _parse_list(self, raw_text):
        return [item.strip() for item in raw_text.split(",") if item.strip()]

    def _parse_int_list(self, raw_text):
        return [int(item.strip()) for item in raw_text.split(",") if item.strip().isdigit()]

    def _get_text_lines(self, text_widget):
        content = text_widget.get("1.0", tk.END).strip()
        return [line.strip() for line in content.splitlines() if line.strip()]

    def start_ticket_task(self):
        if self.dep_auto_install.get():
            self.simulate_dependency_install()
        self.log("任务开始！")
        self.status_label.config(text="当前状态: 抢票进行中")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.restart_button.config(state=tk.NORMAL)

        self.task_thread = threading.Thread(target=self.simulate_ticket_task, daemon=True)
        self.task_thread.start()

    def stop_ticket_task(self):
        self.log("任务已停止！")
        self.status_label.config(text="当前状态: 任务已停止")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)

    def retry_ticket_task(self):
        self.log("正在重试任务...")
        self.start_ticket_task()

    def simulate_ticket_task(self):
        for i in range(1, 101):
            time.sleep(0.08)
            self.progress_bar["value"] = i
            self.progress_label.config(text=f"进度: {i}%")
            self.window.update_idletasks()

        self.log("任务完成！")
        self.status_label.config(text="当前状态: 任务完成")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.NORMAL)

    def simulate_dependency_install(self):
        dependencies = self._get_text_lines(self.dependency_list)
        if not dependencies:
            self.log("依赖清单为空，已跳过。")
            return
        self.log("开始模拟安装依赖...")
        for item in dependencies:
            time.sleep(0.05)
            self.log(f"已模拟安装: {item}")
        self.log("依赖模拟安装完成。")

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.yview(tk.END)

    def save_config(self):
        config_data = {
            "version": "4.5",
            "global": {
                "log_level": self.global_log_level.get(),
                "timezone": self.global_timezone.get(),
                "ntp_servers": self._parse_list(self.global_ntp_servers.get()),
                "dashboard": {
                    "enable": self.dashboard_enable.get(),
                    "host": self.dashboard_host.get(),
                    "port": int(self.dashboard_port.get() or 0),
                },
            },
            "accounts": {
                "acc_primary": {
                    "platform": self.account_platform.get(),
                    "credentials": {
                        "mobile": self.account_mobile.get(),
                        "password": self.account_password.get(),
                        "otp_secret": self.account_otp.get(),
                    },
                    "target": {
                        "event_url": self.target_event_url.get(),
                        "priorities": {
                            "date": self._parse_int_list(self.target_date_priorities.get()),
                            "session": self._parse_int_list(self.target_session_priorities.get()),
                            "price_range": self.target_price_range.get(),
                        },
                        "tickets": int(self.target_tickets.get() or 0),
                        "viewers": self._parse_int_list(self.target_viewers.get()),
                    },
                    "proxy": {
                        "type": self.proxy_type.get(),
                        "addr": self.proxy_addr.get(),
                        "rotate_interval": f"{self.proxy_rotate.get()}s",
                    },
                }
            },
            "strategy": {
                "auto_strike": self.strategy_auto.get(),
                "strike_time": self.strategy_time.get(),
                "preheat_stages": [
                    float(item) for item in self._parse_list(self.strategy_preheat.get())
                ],
                "ai_enabled": self.strategy_ai.get(),
                "ai_model_path": self.strategy_ai_model.get(),
                "max_retries": int(self.strategy_max_retries.get() or 0),
                "retry_backoff": self.strategy_retry_backoff.get(),
            },
            "monitor": {
                "enable": self.monitor_enable.get(),
                "poll_interval": f"{self.monitor_poll_interval.get()}s",
                "triggers": self._get_text_lines(self.monitor_triggers),
            },
            "notification": {
                "channels": [
                    {
                        "telegram": {
                            "bot_token": self.telegram_token.get(),
                            "chat_id": self.telegram_chat.get(),
                        }
                    },
                    {
                        "email": {
                            "smtp": self.email_smtp.get(),
                            "user": self.email_user.get(),
                            "pass": self.email_pass.get(),
                            "recipients": self._parse_list(self.email_recipients.get()),
                        }
                    },
                ]
            },
            "plugins": {"custom": self._parse_list(self.plugins_custom.get())},
            "dependencies": {
                "auto_install": self.dep_auto_install.get(),
                "packages": self._get_text_lines(self.dependency_list),
            },
        }

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json")],
            initialfile="config.json",
        )
        if not file_path:
            return

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(config_data, file, ensure_ascii=False, indent=2)
        self.log("配置已保存！")

    def load_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON文件", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                config_data = json.load(file)
        except (json.JSONDecodeError, OSError) as error:
            messagebox.showerror("错误", f"无法读取配置文件: {error}")
            return

        global_cfg = config_data.get("global", {})
        self.global_log_level.set(global_cfg.get("log_level", "DEBUG"))
        self.global_timezone.delete(0, tk.END)
        self.global_timezone.insert(0, global_cfg.get("timezone", ""))
        self.global_ntp_servers.delete(0, tk.END)
        self.global_ntp_servers.insert(0, ",".join(global_cfg.get("ntp_servers", [])))
        dashboard_cfg = global_cfg.get("dashboard", {})
        self.dashboard_enable.set(dashboard_cfg.get("enable", True))
        self.dashboard_host.delete(0, tk.END)
        self.dashboard_host.insert(0, dashboard_cfg.get("host", ""))
        self.dashboard_port.delete(0, tk.END)
        self.dashboard_port.insert(0, str(dashboard_cfg.get("port", "")))

        accounts = config_data.get("accounts", {})
        primary = accounts.get("acc_primary", {})
        self.account_platform.set(primary.get("platform", "taopiaopiao"))
        creds = primary.get("credentials", {})
        self.account_mobile.delete(0, tk.END)
        self.account_mobile.insert(0, creds.get("mobile", ""))
        self.account_password.delete(0, tk.END)
        self.account_password.insert(0, creds.get("password", ""))
        self.account_otp.delete(0, tk.END)
        self.account_otp.insert(0, creds.get("otp_secret", ""))

        target = primary.get("target", {})
        self.target_event_url.delete(0, tk.END)
        self.target_event_url.insert(0, target.get("event_url", ""))
        priorities = target.get("priorities", {})
        self.target_date_priorities.delete(0, tk.END)
        self.target_date_priorities.insert(0, ",".join(map(str, priorities.get("date", []))))
        self.target_session_priorities.delete(0, tk.END)
        self.target_session_priorities.insert(0, ",".join(map(str, priorities.get("session", []))))
        self.target_price_range.set(priorities.get("price_range", "lowest_to_highest"))
        self.target_tickets.delete(0, tk.END)
        self.target_tickets.insert(0, str(target.get("tickets", "")))
        self.target_viewers.delete(0, tk.END)
        self.target_viewers.insert(0, ",".join(map(str, target.get("viewers", []))))

        proxy = primary.get("proxy", {})
        self.proxy_type.set(proxy.get("type", "socks5"))
        self.proxy_addr.delete(0, tk.END)
        self.proxy_addr.insert(0, proxy.get("addr", ""))
        self.proxy_rotate.delete(0, tk.END)
        self.proxy_rotate.insert(0, str(proxy.get("rotate_interval", "")).replace("s", ""))

        strategy = config_data.get("strategy", {})
        self.strategy_auto.set(strategy.get("auto_strike", True))
        self.strategy_time.delete(0, tk.END)
        self.strategy_time.insert(0, strategy.get("strike_time", ""))
        self.strategy_preheat.delete(0, tk.END)
        self.strategy_preheat.insert(0, ",".join(map(str, strategy.get("preheat_stages", []))))
        self.strategy_ai.set(strategy.get("ai_enabled", True))
        self.strategy_ai_model.delete(0, tk.END)
        self.strategy_ai_model.insert(0, strategy.get("ai_model_path", ""))
        self.strategy_max_retries.delete(0, tk.END)
        self.strategy_max_retries.insert(0, str(strategy.get("max_retries", "")))
        self.strategy_retry_backoff.set(strategy.get("retry_backoff", "exponential"))

        monitor = config_data.get("monitor", {})
        self.monitor_enable.set(monitor.get("enable", True))
        self.monitor_poll_interval.delete(0, tk.END)
        self.monitor_poll_interval.insert(0, str(monitor.get("poll_interval", "")).replace("s", ""))
        self.monitor_triggers.delete("1.0", tk.END)
        self.monitor_triggers.insert(tk.END, "\n".join(monitor.get("triggers", [])))

        notification = config_data.get("notification", {})
        channels = notification.get("channels", [])
        telegram = next((c.get("telegram") for c in channels if "telegram" in c), {})
        email = next((c.get("email") for c in channels if "email" in c), {})
        self.telegram_token.delete(0, tk.END)
        self.telegram_token.insert(0, telegram.get("bot_token", ""))
        self.telegram_chat.delete(0, tk.END)
        self.telegram_chat.insert(0, telegram.get("chat_id", ""))
        self.email_smtp.delete(0, tk.END)
        self.email_smtp.insert(0, email.get("smtp", ""))
        self.email_user.delete(0, tk.END)
        self.email_user.insert(0, email.get("user", ""))
        self.email_pass.delete(0, tk.END)
        self.email_pass.insert(0, email.get("pass", ""))
        self.email_recipients.delete(0, tk.END)
        self.email_recipients.insert(0, ",".join(email.get("recipients", [])))

        plugins = config_data.get("plugins", {})
        self.plugins_custom.delete(0, tk.END)
        self.plugins_custom.insert(0, ",".join(plugins.get("custom", [])))

        dependencies = config_data.get("dependencies", {})
        self.dep_auto_install.set(dependencies.get("auto_install", True))
        self.dependency_list.delete("1.0", tk.END)
        self.dependency_list.insert(tk.END, "\n".join(dependencies.get("packages", [])))
        self.log("配置已加载！")

    def show_about(self):
        messagebox.showinfo(
            "关于",
            "抢票助手 V5.0\n\n交互界面支持 README 中的配置项预设。\n\n说明: 仅研究用途。",
        )


if __name__ == "__main__":
    app = TicketHelperGUI()
    app.window.mainloop()
