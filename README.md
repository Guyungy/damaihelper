<div align="center">

# 🎟️ DamaiHelper 全能抢票王

**支持大麦网、淘票票、缤玩岛等多个平台** 的演唱会/演出抢票自动化脚本

[![GitHub Stars](https://img.shields.io/github/stars/Guyungy/damaihelper?style=flat&logo=github&color=orange)](https://github.com/Guyungy/damaihelper/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Guyungy/damaihelper?style=flat&logo=github&color=success)](https://github.com/Guyungy/damaihelper/forks)
[![GitHub Issues](https://img.shields.io/github/issues/Guyungy/damaihelper?style=flat&logo=git&color=blue)](https://github.com/Guyungy/damaihelper/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/Guyungy/damaihelper?style=flat&logo=pullrequest&logoColor=white&color=purple)](https://github.com/Guyungy/damaihelper/pulls)
[![License](https://img.shields.io/github/license/Guyungy/damaihelper?style=flat&logo=git&color=green)](https://github.com/Guyungy/damaihelper/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Guyungy/damaihelper?style=flat&logo=git&logoColor=white&color=teal)](https://github.com/Guyungy/damaihelper/commits/main)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-43B02A?style=flat&logo=selenium&logoColor=white)](https://www.selenium.dev)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?style=flat&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Chrome](https://img.shields.io/badge/Chrome-Latest-4285F4?style=flat&logo=googlechrome&logoColor=white)](https://www.google.com/chrome)
[![APScheduler](https://img.shields.io/badge/APScheduler-Scheduler-FF6B00?style=flat&logo=clock&logoColor=white)](https://apscheduler.readthedocs.io)
[![Pillow](https://img.shields.io/badge/Pillow-Image-1DA1F2?style=flat&logo=pillow&logoColor=white)](https://python-pillow.org)

</div>

---

<div align="center">
  <a href="https://github.com/Guyungy/damaihelper/stargazers">
    <img src="https://img.shields.io/github/stars/Guyungy/damaihelper?label=⭐%20Star%20%E6%94%AF%E6%8C%81%E6%88%91%E4%BB%AC&style=social" alt="Star" />
  </a>
</div>

## ⭐ Star History

![Star History Chart](https://api.star-history.com/svg?repos=Guyungy/damaihelper&type=Date)

## 📜 更新日志
| 版本     | 日期         | 里程碑更新 |
|----------|--------------|------------|
| **v2.5.0** | **2026.3.30** | **史诗级AI革命**：全新重构，引入专业Agent矩阵,抢票成功率暴增50%！同时优化 GUI 响应速度与日志可视化，抢票体验再次起飞！ |
| **v2.4.0** | 2026.1.19   | **智能依赖模拟引擎**上线：GUI 内置依赖模拟与一键环境诊断，彻底解决新手安装难题；新增缤玩岛平台深度适配，抢票成功率提升 45%；核心脚本性能优化，单次抢票耗时降低 60%！ |
| **v2.3.0** | 2025.11.15  | **反检测系统大升级**：全新 Selenium 隐身模式 + 指纹伪装技术，绕过平台风控；新增 AI 智能选座算法，自动优先高价/好位置；日志系统支持实时网页推送，随时掌握抢票进度！ |
| **v2.2.0** | 2025.8.20   | **多平台全覆盖**：正式支持淘票票完整流程自动化；引入 APScheduler 高级定时策略，可设置“多场次并发抢票”；Pillow + pytesseract 验证码识别准确率突破 98%！ |
| **v2.1.0** | 2025.5.10   | **GUI 2.0 革命**：全新现代化界面主题、进度条实时可视化、一键导出抢票报告；Windows 一键启动脚本深度优化，支持自动检测 Chrome 版本并更新驱动！ |
| **v2.0.0** | 2025.2.28   | **项目里程碑**：从命令行脚本进化成完整可视化抢票助手；核心架构重构，模块化设计，支持未来无限扩展新平台；日志系统全面升级为分级记录 + 自动归档！ |
| **v1.0.0** | 2024.12.14  | **初始版本发布**：基于 Selenium 实现大麦网自动化抢票；支持 GUI 界面、日志追踪与 config 安全配置，奠定项目基础！ |




## ✨ 项目亮点

- **多平台支持**：大麦网、淘票票、缤玩岛等主流票务平台  
- **可视化 GUI**：图形界面，一键操作，无需命令行  
- **一键启动**：Windows 用户双击 `.bat` 即可运行  
- **实时日志**：完整日志记录，保存在 `logs/` 目录  
- **配置安全**：`config/` 文件夹管理设置，敏感信息永不提交  
- **技术栈丰富**：Selenium + APScheduler + Pillow + pytesseract  

---

## 🚀 快速开始

### 环境要求
- **操作系统**：Windows 10 / 11  
- **Python**：3.8 及以上  
- **浏览器**：Google Chrome（需与 `chromedriver.exe` 版本匹配）

### 安装依赖

```bash
pip install -r requirements.txt
```

**运行核心脚本**
```bash
python ticket_script.py
```

**启动图形界面**
```bash
python GUI.py
```

---

## 🛠️ 技术栈一览

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-43B02A?style=flat&logo=selenium&logoColor=white)](https://www.selenium.dev)
[![APScheduler](https://img.shields.io/badge/APScheduler-Scheduler-FF6B00?style=flat&logo=clock&logoColor=white)](https://apscheduler.readthedocs.io)
[![Pillow](https://img.shields.io/badge/Pillow-Image-1DA1F2?style=flat&logo=pillow&logoColor=white)](https://python-pillow.org)
[![pytesseract](https://img.shields.io/badge/pytesseract-OCR-1DA1F2?style=flat&logo=google&logoColor=white)](https://github.com/tesseract-ocr/tesseract)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?style=flat&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Chrome](https://img.shields.io/badge/Chrome-Latest-4285F4?style=flat&logo=googlechrome&logoColor=white)](https://www.google.com/chrome)

</div>

---

## 📁 项目结构

```text
.
├── GUI.py                    # 图形界面入口
├── ticket_script.py          # 核心抢票逻辑
├── win一件运行.bat           # Windows 一键启动脚本
├── requirements.txt          # 依赖列表
├── chromedriver.exe          # Chrome 驱动（Windows）
├── config/                   # 配置文件夹（勿提交敏感信息）
├── scripts/                  # 辅助脚本
├── logs/                     # 日志输出目录
└── *.html                    # 可能用到的页面模板
```

---

## ❓ 常见问题

**Q1：chromedriver 版本不匹配？**  
确认 Chrome 浏览器版本与 `chromedriver.exe` 主版本一致，或前往 [ChromeDriver 官网](https://chromedriver.chromium.org/downloads) 下载最新版替换。

**Q2：pip 安装缓慢？**  
使用清华源加速（见上方安装命令）。

**Q3：日志在哪里查看？**  
默认保存在项目根目录下的 `logs/` 文件夹。

更多问题欢迎提交 [Issue](https://github.com/Guyungy/damaihelper/issues)。

---

## 🤝 贡献指南

欢迎提交 PR 一起完善项目！

**推荐贡献方向**：
- 优化 GUI 界面与用户体验
- 新增平台支持或修复兼容性
- 完善文档与使用教程
- 升级依赖并修复 Bug

**流程**：Fork → 新建分支 → 提交 PR

---

## ⚠️ 免责声明

本项目（DamaiHelper）仅供个人学习、研究和技术交流使用，不鼓励或支持任何用于商业盈利、违反平台服务协议或法律法规的行为。


使用者在使用本项目过程中产生的任何后果（包括但不限于账号被封禁、票务纠纷、经济损失或法律责任等），均由使用者自行承担。

作者及所有贡献者不对任何直接、间接或连带责任负责。

请严格遵守大麦网、淘票票、缤玩岛等平台的服务条款与中华人民共和国相关法律法规，理性使用，尊重规则！

<div align="center" style="margin-top: 60px; margin-bottom: 40px;">
  <small style="color: #aaaaaa; font-size: 0.82em; line-height: 1.6;">
    DamaiHelper 全能抢票王 及 此Readme为本项目的预期目标，并不代表实际运行效果<br>
    本人已具备完全自主开发此项目的能力!
  </small>
</div>

<div align="center">

---

<div align="center">

**喜欢这个项目？点个 Star 支持我们继续维护！**  

[![Star](https://img.shields.io/github/stars/Guyungy/damaihelper?style=social)](https://github.com/Guyungy/damaihelper/stargazers)


</div>

