import os
import streamlit as st
import streamlit.components.v1 as components

st.title("🎵 カスタムHTMLプレイヤー (ストリーミング版)")

STATIC_DIR = "static"

# リサーチ処理（ここは先ほどと同じです）
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
        
    # 実際の物理パス
    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{selected_file_name}.m4a")
    
    # 🔴【重要】Streamlitの内部機能を使って、ブラウザからアクセス可能な「本物のURL」を逆引きします。
    # これにより、Community Cloud上のセキュリティ制限をすり抜ける正しいURLが手に入ります。
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        # サーバが提供するこのファイル専用の内部配信用URLを取得
        audio_url = st.runtime.exists() and st.runtime.get_instance().media_file_mgr.add(
            physical_path, "audio/mp4", get_script_run_ctx().session_id
        )
    except Exception:
        # ローカル環境などのフォールバック
        audio_url = f"/static/{selected_folder}/{selected_file_name}.m4a"

    st.caption(f"ストリーミング再生中: {selected_folder}/{selected_file_name}.m4a")

    if os.path.exists("player.html"):
        with open("player.html", "r", encoding="utf-8") as f:
            html_code = f.read()

        # 本物のURLをHTML側のプレイヤーに引き渡す
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
        st.error("⚠️ `player.html` が見つかりません。")
else:
    st.warning("`static` フォルダ内に、有効な音声ファイル（フォルダ名と一致するm4a）が見つかりません。")
