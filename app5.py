import os
import streamlit as st

st.title("🎵 カスタム音声プレイヤー")

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
        
    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{selected_file_name}.m4a")

    # 1. プレイヤーを囲む外枠を配置
    st.markdown(
        f"""
        <div class="custom-player-box">
            <div class="player-title">📄 再生中: {selected_file_name}.m4a</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. クラウドで稼働実績のある確実なプレイヤーを配置
    st.audio(physical_path, format="audio/mp4")

    # 3. 🔴 画面全体の「見た目（CSS）」を直接上書きする
    # ここにCSSを記述することで、HTMLファイルを作らなくてもデザインを変更できます
    st.markdown(
        """
        <style>
        /* プレイヤーを囲む背景パネルのデザイン */
        .custom-player-box {
            background-color: #f0f2f6; 
            padding: 15px; 
            border-radius: 10px; 
            font-family: sans-serif;
            margin-bottom: -10px; /* 下のプレイヤーと密着させる */
        }
        .player-title {
            font-weight: bold; 
            color: #31333f; 
            font-size: 14px;
        }
        
        /* Streamlit標準のaudioプレイヤー自体の見た目をCSSでカスタム（ブラウザ依存あり） */
        element-container audio {
            background-color: #f0f2f6;
            border-radius: 0 0 10px 10px;
            padding: 0 10px 10px 10px;
            box-shadow: none;
            width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
