import os
import streamlit as st
import streamlit.components.v1 as components

st.title("🎵 カスタムHTMLプレイヤー (確定版)")

STATIC_DIR = "static"

# 有効なフォルダを自動リサーチ
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
        
    # 🔴 /app は含めず、ドメイン直下の「/static/...」という正しいURLを作ります
    audio_url = f"/static/{selected_folder}/{selected_file_name}.m4a"

    if os.path.exists("player.html"):
        with open("player.html", "r", encoding="utf-8") as f:
            html_code = f.read()

        # HTMLを埋め込み、正しいURLを引き渡す
        components.html(
            html_code + f"""
            <script>
                window.audioUrlFromPython = "{audio_url}";
                if (typeof initPlayer === "function") {{
                    initPlayer();
                }}
            </script>
            """,
            height=200,
        )
else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
