import os
import streamlit as st
import streamlit.components.v1 as components

# 画面全体の表示設定
st.set_page_config(
    page_title="奏録 / SOUROKU Web",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Streamlit標準の余白を強制的に消すCSS
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            padding-left: 0px !important;
            padding-right: 0px !important;
            max-width: 100% !important;
        }
        iframe {
            display: block;
            border: none;
            width: 100vw;
            height: 100vh;
        }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------
# データの読み込み処理
# --------------------------------------------------------------------
# ① list.txt の読み込み
list_data = ""
possible_paths = ["list.txt", "static/list.txt", ".streamlit/static/list.txt"]
for path in possible_paths:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                list_data = f.read()
            break
        except Exception:
            pass

if not list_data:
    list_data = "読み込みエラー\nlist.txtが配置されていません"

# 特殊文字のエスケープ処理
list_data_escaped = list_data.replace("`", "\\`").replace("$", "\\$")

# ② 分割したHTMLファイルの読み込み
html_template = ""
if os.path.exists("index.html"):
    with open("index.html", "r", encoding="utf-8") as f:
        html_template = f.read()
else:
    html_template = "<h3>エラー: index.html が見つかりません。</h3>"

# HTMLのプレースホルダー「__LIST_DATA__」を実際のテキストに置き換える
full_html = html_template.replace("__LIST_DATA__", list_data_escaped)

# Streamlitの画面にコンポーネントとして埋め込み
components.html(full_html, height=1000, scrolling=False)
