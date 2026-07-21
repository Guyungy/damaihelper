# coding: utf-8
"""Generate local README badges + UI mockup SVGs (no external CDN)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "docs" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)


def badge(label: str, value: str, color: str, path: Path) -> None:
    lw = 7 * len(label) + 20
    vw = 7 * len(value) + 20
    w = lw + vw
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
  <mask id="m"><rect width="{w}" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#m)">
    <rect width="{lw}" height="20" fill="#555"/>
    <rect x="{lw}" width="{vw}" height="20" fill="{color}"/>
    <rect width="{w}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{lw/2:.1f}" y="14">{label}</text>
    <text x="{lw + vw/2:.1f}" y="14">{value}</text>
  </g>
</svg>
"""
    path.write_text(svg, encoding="utf-8")
    print("badge", path.name)


def write_dashboard() -> None:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="680" viewBox="0 0 1200 680">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#f5f7fb"/><stop offset="100%" stop-color="#eef2f8"/></linearGradient>
    <filter id="sh" x="-5%" y="-5%" width="110%" height="120%"><feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#0b1220" flood-opacity="0.08"/></filter>
  </defs>
  <rect width="1200" height="680" fill="url(#bg)"/>
  <rect width="220" height="680" fill="#001529"/>
  <rect x="24" y="22" width="28" height="28" rx="8" fill="#1677ff"/>
  <text x="62" y="42" fill="#fff" font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="16" font-weight="700">DamaiHelper</text>
  <g font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="14" fill="#ffffffa6">
    <rect x="12" y="90" width="196" height="40" rx="8" fill="#1677ff"/>
    <text x="36" y="115" fill="#fff">Overview</text>
    <text x="36" y="165">Config</text>
    <text x="36" y="215">Tasks</text>
    <text x="36" y="265">YOLO / CUDA</text>
  </g>
  <rect x="220" width="980" height="64" fill="#fff"/>
  <text x="248" y="40" fill="#1f1f1f" font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="18" font-weight="600">Dashboard</text>
  <rect x="980" y="20" width="88" height="24" rx="12" fill="#f6ffed" stroke="#b7eb8f"/>
  <text x="992" y="37" fill="#389e0d" font-size="12" font-family="Segoe UI, sans-serif">API Online</text>
  <rect x="1080" y="20" width="72" height="24" rx="12" fill="#e6f4ff" stroke="#91caff"/>
  <text x="1094" y="37" fill="#1677ff" font-size="12" font-family="Segoe UI, sans-serif">Idle</text>
  <g filter="url(#sh)" font-family="Segoe UI, Microsoft YaHei, sans-serif">
    <rect x="248" y="96" width="210" height="110" rx="12" fill="#fff"/>
    <text x="268" y="128" fill="#8c8c8c" font-size="13">Backend</text>
    <text x="268" y="168" fill="#3f8600" font-size="28" font-weight="700">Online</text>
    <rect x="478" y="96" width="210" height="110" rx="12" fill="#fff"/>
    <text x="498" y="128" fill="#8c8c8c" font-size="13">Progress</text>
    <text x="498" y="168" fill="#1f1f1f" font-size="28" font-weight="700">100%</text>
    <rect x="708" y="96" width="210" height="110" rx="12" fill="#fff"/>
    <text x="728" y="128" fill="#8c8c8c" font-size="13">CUDA</text>
    <text x="728" y="168" fill="#1677ff" font-size="28" font-weight="700">Ready</text>
    <rect x="938" y="96" width="210" height="110" rx="12" fill="#fff"/>
    <text x="958" y="128" fill="#8c8c8c" font-size="13">YOLO</text>
    <text x="958" y="168" fill="#1f1f1f" font-size="28" font-weight="700">Mock</text>
    <rect x="248" y="230" width="560" height="380" rx="12" fill="#fff"/>
    <text x="272" y="268" fill="#1f1f1f" font-size="16" font-weight="600">Local AI Environment</text>
    <text x="272" y="310" fill="#595959" font-size="14">Python   3.10+</text>
    <text x="272" y="345" fill="#595959" font-size="14">GPU      NVIDIA RTX (auto-detect)</text>
    <text x="272" y="380" fill="#595959" font-size="14">PyTorch  CUDA wheel via install_deps</text>
    <text x="272" y="415" fill="#595959" font-size="14">API      /health  /ai/*  /ticket/*</text>
    <rect x="272" y="450" width="120" height="28" rx="6" fill="#e6f4ff"/>
    <text x="288" y="469" fill="#1677ff" font-size="12">CUDA auto</text>
    <rect x="832" y="230" width="316" height="380" rx="12" fill="#fff"/>
    <text x="856" y="268" fill="#1f1f1f" font-size="16" font-weight="600">Quick Start</text>
    <rect x="856" y="300" width="268" height="44" rx="8" fill="#1677ff"/>
    <text x="920" y="328" fill="#fff" font-size="14">Start Task Runner</text>
    <rect x="856" y="360" width="268" height="44" rx="8" fill="#fff" stroke="#d9d9d9"/>
    <text x="948" y="388" fill="#1f1f1f" font-size="14">Edit Config</text>
    <rect x="856" y="420" width="268" height="44" rx="8" fill="#fff" stroke="#d9d9d9"/>
    <text x="932" y="448" fill="#1f1f1f" font-size="14">YOLO / CUDA</text>
    <text x="856" y="520" fill="#8c8c8c" font-size="12">python tools/install_deps.py</text>
    <text x="856" y="545" fill="#8c8c8c" font-size="12">python web_server.py</text>
  </g>
</svg>
"""
    (ASSETS / "ui-dashboard.svg").write_text(svg, encoding="utf-8")
    print("ui-dashboard.svg")


def write_task() -> None:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="680" viewBox="0 0 1200 680">
  <rect width="1200" height="680" fill="#f5f7fb"/>
  <rect width="220" height="680" fill="#001529"/>
  <rect x="24" y="22" width="28" height="28" rx="8" fill="#1677ff"/>
  <text x="62" y="42" fill="#fff" font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="16" font-weight="700">DamaiHelper</text>
  <g font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="14" fill="#ffffffa6">
    <text x="36" y="115">Overview</text>
    <text x="36" y="165">Config</text>
    <rect x="12" y="190" width="196" height="40" rx="8" fill="#1677ff"/>
    <text x="36" y="215" fill="#fff">Tasks</text>
    <text x="36" y="265">YOLO / CUDA</text>
  </g>
  <rect x="220" width="980" height="64" fill="#fff"/>
  <text x="248" y="40" fill="#1f1f1f" font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="18" font-weight="600">Task Runner</text>
  <rect x="248" y="96" width="680" height="520" rx="12" fill="#fff"/>
  <text x="272" y="132" fill="#1f1f1f" font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="15" font-weight="600">Controls</text>
  <rect x="400" y="114" width="72" height="22" rx="11" fill="#e6f4ff"/>
  <text x="414" y="130" fill="#1677ff" font-size="12" font-family="Segoe UI, sans-serif">running</text>
  <rect x="272" y="160" width="120" height="36" rx="8" fill="#1677ff"/>
  <text x="292" y="183" fill="#fff" font-size="13" font-family="Segoe UI, Microsoft YaHei, sans-serif">Start dry-run</text>
  <rect x="404" y="160" width="80" height="36" rx="8" fill="#fff" stroke="#ff4d4f"/>
  <text x="428" y="183" fill="#ff4d4f" font-size="13" font-family="Segoe UI, Microsoft YaHei, sans-serif">Stop</text>
  <rect x="272" y="220" width="620" height="10" rx="5" fill="#f0f0f0"/>
  <rect x="272" y="220" width="430" height="10" rx="5" fill="#1677ff"/>
  <text x="900" y="230" fill="#595959" font-size="12" font-family="Segoe UI, sans-serif">69%</text>
  <rect x="272" y="250" width="620" height="330" rx="10" fill="#0b1220"/>
  <g font-family="ui-monospace, Consolas, monospace" font-size="12">
    <text x="288" y="278" fill="#7f8da3">[19:41:10]</text><text x="370" y="278" fill="#b37feb">[SYSTEM]</text><text x="440" y="278" fill="#d7e0f2"> task started (dry-run)</text>
    <text x="288" y="304" fill="#7f8da3">[19:41:11]</text><text x="370" y="304" fill="#91caff">[INFO]</text><text x="430" y="304" fill="#d7e0f2"> stealth driver patch</text>
    <text x="288" y="330" fill="#7f8da3">[19:41:14]</text><text x="370" y="330" fill="#91caff">[INFO]</text><text x="430" y="330" fill="#d7e0f2"> parse session cards</text>
    <text x="288" y="356" fill="#7f8da3">[19:41:17]</text><text x="370" y="356" fill="#73d13d">[AI]</text><text x="420" y="356" fill="#d7e0f2"> YOLO slider offset=150px</text>
    <text x="288" y="382" fill="#7f8da3">[19:41:19]</text><text x="370" y="382" fill="#b37feb">[SYSTEM]</text><text x="440" y="382" fill="#d7e0f2"> task completed</text>
  </g>
  <rect x="952" y="96" width="196" height="520" rx="12" fill="#fff"/>
  <text x="972" y="132" fill="#1f1f1f" font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="15" font-weight="600">Dependencies</text>
  <rect x="972" y="160" width="156" height="180" rx="8" fill="#fafafa" stroke="#f0f0f0"/>
  <text x="984" y="190" fill="#8c8c8c" font-size="12" font-family="Consolas, monospace">ultralytics</text>
  <text x="984" y="214" fill="#8c8c8c" font-size="12" font-family="Consolas, monospace">httpx</text>
  <text x="984" y="238" fill="#8c8c8c" font-size="12" font-family="Consolas, monospace">orjson</text>
  <rect x="972" y="360" width="156" height="40" rx="8" fill="#1677ff"/>
  <text x="1000" y="385" fill="#fff" font-size="13" font-family="Segoe UI, Microsoft YaHei, sans-serif">Install task</text>
</svg>
"""
    (ASSETS / "ui-task.svg").write_text(svg, encoding="utf-8")
    print("ui-task.svg")


def main() -> None:
    badge("python", "3.10+", "#3776AB", ASSETS / "badge-python.svg")
    badge("frontend", "Ant Design", "#1677ff", ASSETS / "badge-antd.svg")
    badge("ai", "YOLO + CUDA", "#73d13d", ASSETS / "badge-ai.svg")
    badge("license", "MIT", "#2ea44f", ASSETS / "badge-license.svg")
    badge("platform", "Win / macOS", "#0078D4", ASSETS / "badge-platform.svg")
    badge("api", "REST :8765", "#6f42c1", ASSETS / "badge-api.svg")
    write_dashboard()
    write_task()
    print("done ->", ASSETS)


if __name__ == "__main__":
    main()
