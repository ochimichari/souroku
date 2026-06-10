import os
import json
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
# サーバー内の全テキストデータをPython側で安全に先読み（fetchを完全回避）
# --------------------------------------------------------------------
all_data = {}
session_list = []

# ① list.txt の先読み
if os.path.exists("list.txt"):
    with open("list.txt", "r", encoding="utf-8") as f:
        session_list = [line.strip() for line in f if line.strip()]

# ② 各セッションフォルダ内のデータを先読みして辞書に格納
for folder in session_list:
    file_name = folder.split('_')[-1] if '_' in folder else folder
    all_data[folder] = {"color": "", "text": ""}
    
    # 配色データ（_color.txt）の読み込み
    c_path = f"static/{folder}/{file_name}_color.txt"
    if os.path.exists(c_path):
        with open(c_path, "r", encoding="utf-8") as f:
            all_data[folder]["color"] = f.read()
            
    # セッションログデータ（.txt）の読み込み
    t_path = f"static/{folder}/{file_name}.txt"
    if os.path.exists(t_path):
        with open(t_path, "r", encoding="utf-8") as f:
            all_data[folder]["text"] = f.read()

# JavaScriptで安全に読めるようJSON文字列化
json_data = json.dumps(all_data, ensure_ascii=False)
json_list = json.dumps(session_list, ensure_ascii=False)

# ③ index.html テンプレートファイルの読み込み
html_template = ""
if os.path.exists("index.html"):
    with open("index.html", "r", encoding="utf-8") as f:
        html_template = f.read()
else:
    html_template = "<h3>エラー: index.html が見つかりません。</h3>"

# プレースホルダーを実際のJSON文字列に置換
full_html = html_template.replace("__JSON_DATA__", json_data).replace("__JSON_LIST__", json_list)

# 画面にコンポーネントとして埋め込み
components.html(full_html, height=1000, scrolling=False)
