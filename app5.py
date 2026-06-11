import os
import streamlit as st
import streamlit.components.v1 as components

st.title("🎵 カスタムHTMLプレイヤー (完全解決版)")

STATIC_DIR = "static"

# 有効なフォルダを検索（ここは先ほどと同じです）
available_folders = []
if os.path.exists(STATIC_DIR):
    for folder in os.listdir(STATIC_DIR):
        folder_path = os.path.join(STATIC_DIR, folder)
        if os.path.isdir(folder_path):
            if "_" in folder:
                file_name = folder.split("_")[-1]
            else:
                file_name = folder
            m4a_path = os.path.join(folder_path, f"{file_name}.m4a")
            if os.path.exists(m4a_path):
                available_folders.append(folder)

if available_folders:
    available_folders.sort()
    selected_folder = st.selectbox("再生する音声を選択してください", options=available_folders)
    
    if "_" in selected_folder:
        selected_file_name = selected_folder.split("_")[-1]
    else:
        selected_file_name = selected_folder
        
    # 音声ファイルへの「HTMLから見た相対パス」を計算します
    # player.html から見ると、同じ static フォルダ内なので以下のパスで届きます
    audio_relative_url = f"./{selected_folder}/{selected_file_name}.m4a"

    # 🔴 HTMLと音声を同じ「/static/」ドメイン下で動かすことで、セキュリティを突破します
    # URLの末尾に「?audio=音声のパス」をつけてHTMLに伝えます
    iframe_url = f"/static/player.html?audio={audio_relative_url}"

    # st.components.v1.iframe を使って、静的配信されているHTMLを直接呼び出します
    components.iframe(iframe_url, height=200)

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
