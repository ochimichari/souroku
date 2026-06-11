import os
import streamlit as st
import streamlit.components.v1 as components

st.title("🎵 カスタムHTMLプレイヤー (完全統合版)")

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

    # Streamlitのシステムから、クラウドで100%再生できる公式URLを逆引き
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        session_id = ctx.session_id if ctx else None
        
        audio_url = st.runtime.get_instance().media_file_mgr.add(
            physical_path, "audio/mp4", session_id
        )
    except Exception:
        audio_url = f"/static/{selected_folder}/{selected_file_name}.m4a"

    st.caption(f"選択中: {selected_folder}/{selected_file_name}.m4a")

    # 🔴【変更点】元のplayer.htmlに書いていたHTMLとCSSを、ここに直接変数として記述します。
    # これにより「ファイルが見つからないバグ」を完全に消滅させます。
    html_code = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ margin: 0; padding: 0; background: transparent; font-family: sans-serif; }}
            .player-panel {{ background: #f0f2f6; padding: 15px; border-radius: 10px; box-sizing: border-box; }}
            .time-display {{ font-family: monospace; margin-top: 5px; color: #31333f; font-size: 14px; }}
            audio {{ width: 100%; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="player-panel">
            <div style="font-weight: bold; color: #31333f; font-size: 14px;">再生中: {selected_file_name}.m4a</div>
            <audio id="audio" controls src="{audio_url}"></audio>
            <div class="time-display" id="time-display">00:00 / 00:00</div>
        </div>
    </body>
    </html>
    """

    # プレイヤーの画面描画（高さをしっかり確保し、キーを変えることで確実に曲を切り替えます）
    components.html(
        html_code,
        height=160,
        key=f"player_{selected_folder}"
    )

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
