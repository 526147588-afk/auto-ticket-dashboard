"""Streamlit 入口：把 dashboard_v5.html 原样嵌入，自动加载最新 dashboard_data.json

部署到 Streamlit Cloud：
  1. 把整个 dashboard 目录（dashboard_v5.html, dashboard_data.json, app.py, requirements.txt）
     push 到 GitHub repo
  2. Streamlit Cloud 选这个 repo + app.py 入口
  3. URL 类似 https://xxx.streamlit.app

本地测试：
  streamlit run app.py
"""
import json
import os
import streamlit as st

# ============== 1. 页面配置 ==============
st.set_page_config(
    page_title="自动出票数据看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============== 2. 加载数据 ==============
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_data.json")

if not os.path.exists(DATA_FILE):
    st.error(f"❌ 找不到数据文件：{DATA_FILE}")
    st.info("请先运行 `python gen_dashboard_data.py --month all` 生成数据")
    st.stop()

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data_text = f.read()

# ============== 3. 加载 HTML 模板 ==============
HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_v5.html")
if not os.path.exists(HTML_FILE):
    st.error(f"❌ 找不到 HTML 模板：{HTML_FILE}")
    st.stop()

with open(HTML_FILE, "r", encoding="utf-8") as f:
    html = f.read()

# ============== 4. 注入数据到 HTML（核心） ==============
safe_data = (
    data_text
    .replace("</script>", "<\\/script>")
    .replace("<!--", "<\\!--")
)

injection = f"<script>window.__DASHBOARD_DATA__ = {safe_data};</script>"
if "</head>" in html:
    html = html.replace("</head>", injection + "</head>", 1)
else:
    html = html.replace("<body>", "<body>" + injection, 1)

# ============== 5. 渲染 ==============
# streamlit 1.58 的 st.iframe 自动检测 src 类型：
# 不以 http/https/data 开头、不以 / 开头、不是文件路径 → 当 HTML 字符串，用 srcdoc 嵌入
st.iframe(html, height=5000)

# ============== 6. 底部状态条 ==============
try:
    data = json.loads(data_text)
    months = data.get("available_months", [])
    total = data.get("summary", {}).get("total_orders", 0)
    current = data.get("current_month", "")
    st.caption(
        f"📅 数据月份：{current} · 可选：{months} · "
        f"📊 总单数：{total:,} · "
        f"🕐 看板刷新：{data.get('generated_at', 'N/A')}"
    )
except Exception:
    pass
