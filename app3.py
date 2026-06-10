import os
import glob
import json
import streamlit as st
import streamlit.components.v1 as components

# 最上層のパスを確実に取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
list_txt_path = os.path.join(BASE_DIR, "list.txt")

session_list = []

if os.path.exists(list_txt_path):
    # 'utf-8-sig' にすることで、BOM付きUTF-8ファイルでも正常に読み込めます
    with open(list_txt_path, "r", encoding="utf-8-sig") as f:
        for line in f:
            # 1. 改行コード（\r\n や \n）を完全に除去
            # 2. 前後の不要な空白を除去
            clean_line = line.replace('\r', '').replace('\n', '').strip()
            
            # 空行でなければリストに追加
            if clean_line:
                session_list = clean_line
else:
    # 画面にファイルが見つからないエラーを表示（デバッグ用）
    st.error(f"❌ list.txt が最上層に見つかりません。探索パス: {list_txt_path}")

# デバッグ用：正しく読み込めたか画面に中身を出力してみる
if session_list:
    st.success(f"✅ list.txt の読み込みに成功しました！データ数: {len(session_list)}")
    # st.write(session_list) # 中身を確認したい場合はコメントアウトを外してください
else:
    st.warning("⚠️ list.txt は存在しますが、中身が空、または正しく行を認識できていません。")

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
