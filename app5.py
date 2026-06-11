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

    # 🔴【デザインの工夫】全体を囲む独自のパネル（枠）を配置します
    st.markdown(
        f"""
        <div class="my-audio-container">
            <div class="my-audio-header">
                <span class="music-icon">🎵</span>
                <span class="music-title">再生中: {selected_file_name}.m4a</span>
            </div>
            <div class="player-wrapper">
        """,
        unsafe_allow_html=True
    )

    # 🔴 タイムライン選択が100%確実に動く公式プレイヤー（この位置に埋め込まれます）
    st.audio(physical_path, format="audio/mp4")

    # 閉じタグ
    st.markdown('</div></div>', unsafe_allow_html=True)

    # 🔴 CSSで標準プレイヤーを包み込み、オリジナルの見た目に変形させます
    st.markdown(
        """
        <style>
        /* 全体を包む独自パネル（グレーの背景、大きな角丸、シャドウ） */
        .my-audio-container {
            background: linear-gradient(135deg, #f0f2f6 0%, #e4e7eb 100%);
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            font-family: sans-serif;
            margin-top: 10px;
        }
        
        /* タイトル部分の装飾 */
        .my-audio-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
        }
        .music-icon { font-size: 18px; }
        .music-title {
            font-weight: bold;
            color: #1e293b;
            font-size: 15px;
        }
        
        /* 🔴 標準プレイヤー自体の形や色を、背景になじませるカスタム */
        .player-wrapper audio {
            width: 100%;
            height: 40px;
            border-radius: 8px;
            background-color: #ffffff; /* バーの背景を白にして浮き立たせる */
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
