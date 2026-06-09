import os
import glob
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="奏録 / SOUROKU Web", layout="centered", initial_sidebar_state="collapsed")

# 1. サーバー内のデータを全てスキャンして辞書にまとめる
all_data = {}
session_list = []

# list.txtの読み込み
if os.path.exists("list.txt"):
    with open("list.txt", "r", encoding="utf-8") as f:
        session_list = [line.trim() for line in f if line.trim()]

# 各セッションのテキストデータを先読み
for folder in session_list:
    file_name = folder.split('_')[-1] if '_' in folder else folder
    all_data[folder] = {"color": "", "text": ""}
    
    # カラーファイルの読み込み
    c_path = f"static/{folder}/{file_name}_color.txt"
    if os.path.exists(c_path):
        with open(c_path, "r", encoding="utf-8") as f:
            all_data[folder]["color"] = f.read()
            
    # ログファイルの読み込み
    t_path = f"static/{folder}/{file_name}.txt"
    if os.path.exists(t_path):
        with open(t_path, "r", encoding="utf-8") as f:
            all_data[folder]["text"] = f.read()

# JavaScriptで安全に読めるようにJSON文字列化
json_data = json.dumps(all_data, ensure_ascii=False)
json_list = json.dumps(session_list, ensure_ascii=False)

# 2. HTMLテンプレートの読み込みと埋め込み
html_template = ""
if os.path.exists("index.html"):
    with open("index.html", "r", encoding="utf-8") as f:
        html_template = f.read()

full_html = html_template.replace("__JSON_DATA__", json_data).replace("__JSON_LIST__", json_list)
components.html(full_html, height=1000, scrolling=False)
