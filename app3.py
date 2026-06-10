import os
import glob
import json
import streamlit as st
import streamlit.components.v1 as components

# ページ設定（一番最初に記述）
st.set_page_config(page_title="奏録 / SOUROKU Web", layout="centered", initial_sidebar_state="collapsed")

# 基準となる最上層のフォルダパスを取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. サーバー内のデータを全てスキャンして辞書にまとめる
all_data = {}
session_list = []

# list.txtの読み込み（バグを修正）
list_txt_path = os.path.join(BASE_DIR, "list.txt")
if os.path.exists(list_txt_path):
    with open(list_txt_path, "r", encoding="utf-8-sig") as f:
        for line in f:
            clean_line = line.replace('\r', '').replace('\n', '').strip()
            if clean_line:
                session_list.append(clean_line) # <- 正しく配列に追加
else:
    st.error(f"❌ list.txt が見つかりません。探索パス: {list_txt_path}")

# 各セッションのテキストデータを先読み
for folder in session_list:
    file_name = folder.split('_')[-1] if '_' in folder else folder
    all_data[folder] = {"color": "", "text": ""}
    
    # カラーファイルの読み込み
    c_path = os.path.join(BASE_DIR, "static", folder, f"{file_name}_color.txt")
    if os.path.exists(c_path):
        with open(c_path, "r", encoding="utf-8") as f:
            all_data[folder]["color"] = f.read().strip()
            
    # ログファイルの読み込み
    t_path = os.path.join(BASE_DIR, "static", folder, f"{file_name}.txt")
    if os.path.exists(t_path):
        with open(t_path, "r", encoding="utf-8") as f:
            all_data[folder]["text"] = f.read()

# JavaScriptで安全に読めるようにJSON文字列化
json_data = json.dumps(all_data, ensure_ascii=False)
json_list = json.dumps(session_list, ensure_ascii=False)

# 2. HTMLテンプレートの読み込みと埋め込み
html_template = ""
index_html_path = os.path.join(BASE_DIR, "index.html")
if os.path.exists(index_html_path):
    with open(index_html_path, "r", encoding="utf-8") as f:
        html_template = f.read()

full_html = html_template.replace("__JSON_DATA__", json_data).replace("__JSON_LIST__", json_list)
components.html(full_html, height=1000, scrolling=False)
