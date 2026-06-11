import os
import streamlit as st
import streamlit.components.v1 as components

st.title("🎵 カスタムHTMLプレイヤー")

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
        
    # 音声の正しいURL（ドメイン直下の /static/... から指定）
    audio_url = f"/static/{selected_folder}/{selected_file_name}.m4a"

    st.caption(f"選択中: {selected_folder}/{selected_file_name}.m4a")

    # 🔴 潰れて見えなくなるのを防ぐため、iframe（内側の枠）に直接「見える大きさ」を書き込みます
    # これにより、プレイヤーが最初から必ず画面に表示されます
    components.html(
        f"""
        <iframe src="/static/player.html?audio={audio_url}" 
                style="width:100%; height:150px; border:none; overflow:hidden;" 
                scrolling="no">
        </iframe>
        """,
        height=160,  # Streamlit側で確保する外側の高さ
    )
else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
