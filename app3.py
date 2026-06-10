import os
import json
import streamlit as st

# 1. 画面全体の表示設定
st.set_page_config(
    page_title="奏録 / SOUROKU Web",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 余白を強制的に消すCSS
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

# 2. テキストデータの先読み
all_data = {}
session_list = []

# ① list.txt の読み込み
if os.path.exists("list.txt"):
    with open("list.txt", "r", encoding="utf-8") as f:
        session_list = [line.strip() for line in f if line.strip()]

# ② 各フォルダ内のデータ先読み（今後のステップ用。現在は空のまま進みます）
for folder in session_list:
    all_data[folder] = {"color": "", "text": ""}

# JSに渡すためにJSON文字列化
json_data = json.dumps(all_data, ensure_ascii=False)
json_list = json.dumps(session_list, ensure_ascii=False)

# 3. index.html テンプレートファイルの読み込み
html_template = ""
if os.path.exists("index.html"):
    with open("index.html", "r", encoding="utf-8") as f:
        html_template = f.read()
else:
    html_template = "<h3>エラー: index.html が見つかりません。</h3>"

# プレースホルダーを実際のデータに置換
full_html = html_template.replace(
    "__JSON_DATA__", json_data
).replace(
    "__JSON_LIST__", json_list
)

# 4. 最新推奨の st.html で出力
st.html(full_html)