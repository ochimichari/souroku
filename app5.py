import os
import streamlit as st

st.title("🎵 カスタムHTMLプレイヤー (確定解決版)")

STATIC_DIR = "static"

# 有効な音声フォルダを自動リサーチ
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
        
    # サーバ上の実際の音声ファイルパス
    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{selected_file_name}.m4a")

    # 🟢 解決策：外枠のデザイン（HTML/CSS）だけを st.markdown で描画します
    st.markdown(
        f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; box-sizing: border-box; font-family: sans-serif;">
            <div style="font-weight: bold; color: #31333f; font-size: 14px; margin-bottom: 5px;">
                再生中: {selected_file_name}.m4a
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 🟢 そして、一番最初に100%動いたStreamlit標準の安全なオーディオプレイヤーを直下に配置します
    # これなら、最新のStreamlit(Python 3.14)でも絶対にTypeErrorを吐きません
    st.audio(physical_path, format="audio/mp4")

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
