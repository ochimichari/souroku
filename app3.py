import os
import glob
import json
import streamlit as st
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(page_title="奏録 / SOUROKU Web", layout="centered", initial_sidebar_state="collapsed")

# 🛠️ デバッグモードのON/OFFスイッチを画面最上部に設置
debug_mode = st.checkbox("🔍 ファイル読み込み状況をチェックする（デバッグ）", value=False)

# 基準となる最上層のフォルダパスを取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

all_data = {}
session_list = []

# --- 1. list.txtの読み込み ---
list_txt_path = os.path.join(BASE_DIR, "list.txt")
if os.path.exists(list_txt_path):
    with open(list_txt_path, "r", encoding="utf-8-sig") as f:
        for line in f:
            clean_line = line.replace('\r', '').replace('\n', '').strip()
            if clean_line:
                session_list.append(clean_line)
    if debug_mode:
        st.success(f"📂 **list.txt 読み込み成功:** {len(session_list)} 個のフォルダを検出しました。")
else:
    st.error(f"❌ **list.txt が見つかりません。** 探索パス: {list_txt_path}")

# --- 2. 各セッションファイルの読み込み ---
for folder in session_list:
    file_name = folder.split('_')[-1] if '_' in folder else folder
    all_data[folder] = {"color": "", "text": ""}
    
    if debug_mode:
        st.markdown(f"--- \n### 📂 フォルダ: `{folder}`")
    
    # カラーファイルの読み込み
    c_path = os.path.join(BASE_DIR, "static", folder, f"{file_name}_color.txt")
    if os.path.exists(c_path):
        with open(c_path, "r", encoding="utf-8") as f:
            all_data[folder]["color"] = f.read().strip()
        if debug_mode:
            st.caption(f"🟢 カラー取得成功 ({len(all_data[folder]['color'])}文字): `{os.path.basename(c_path)}`")
    else:
        if debug_mode:
            st.error(f"🔴 カラー無し: `{c_path}` が見つかりません")
            
    # ログファイルの読み込み
    t_path = os.path.join(BASE_DIR, "static", folder, f"{file_name}.txt")
    if os.path.exists(t_path):
        with open(t_path, "r", encoding="utf-8") as f:
            all_data[folder]["text"] = f.read()
        if debug_mode:
            st.caption(f"🟢 テキスト取得成功 ({len(all_data[folder]['text'])}文字): `{os.path.basename(t_path)}`")
    else:
        if debug_mode:
            st.error(f"🔴 テキスト無し: `{t_path}` が見つかりません")

# --- app3.py の一番最後（components.html の直前） ---

# JavaScriptで安全に読めるようにJSON文字列化
json_data = json.dumps(all_data, ensure_ascii=False)
json_list = json.dumps(session_list, ensure_ascii=False)

# index.html の読み込み
html_template = ""
index_html_path = os.path.join(BASE_DIR, "index.html")
if os.path.exists(index_html_path):
    with open(index_html_path, "r", encoding="utf-8") as f:
        html_template = f.read()

# 💡 修正: 置換(replace)に頼らず、HTMLのすぐ前に直接JavaScriptの変数定義を合体させる（最も確実）
injection_script = f"""
<script>
    window.__SERVER_DATA__ = {json_data};
    window.__JSON_LIST__ = {json_list};
</script>
"""
full_html = injection_script + html_template

# HTMLコンポーネントの描画
components.html(full_html, height=1000, scrolling=False)

