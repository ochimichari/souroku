import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="centered")
st.title("🎵 奏録 / SOUROKU")

STATIC_DIR = "static"
available_folders = sorted([f for f in os.listdir(STATIC_DIR) if os.path.isdir(os.path.join(STATIC_DIR, f))]) if os.path.exists(STATIC_DIR) else []

if available_folders:
    selected_folder = st.selectbox("Select session", options=available_folders)
    file_name = selected_folder.split("_")[-1] if "_" in selected_folder else selected_folder
    
    # 🔴【変更点1】ファイル切り替え時に再生時間を「0秒」に強制リセット
    if "last_folder" not in st.session_state or st.session_state.last_folder != selected_folder:
        st.session_state.last_folder = selected_folder
        st.session_state.seek_seconds = 0

    audio_url = f"/static/{selected_folder}/{file_name}.m4a"
    txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.txt")

    # ログファイルの解析とHTML行の組み立て
    log_html = ""
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("[") and "]" in line:
                    time_str, text = line.split("]", 1)
                    time_str = time_str.replace("[", "").strip()
                    parts = time_str.split(":")
                    secs = int(parts[0]) * 60 + int(parts[1]) if len(parts) == 2 else 0
                    
                    # 🔴【変更点2】時間＋コメントの「行全体」を1つの外枠（onclick）で包む
                    log_html += f"""
                    <div class="log-row" onclick="triggerSeek({secs})">
                        <span class="time">[{time_str}]</span><span class="text">{text.strip()}</span>
                    </div>"""

    # プレイヤーとログを1つのHTMLに同居させ、セキュリティ制限を完全回避
    ui_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ background-color: #0e1117; color: #e2e8f0; font-family: sans-serif; margin: 0; }}
            .panel {{ background: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-bottom: 20px; }}
            audio {{ width: 100%; filter: invert(0.9) hue-rotate(180deg); }}
            .container {{ background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 10px; max-height: 350px; overflow-y: auto; }}
            /* 行全体の見た目とホバー設定 */
            .log-row {{ display: flex; padding: 8px; border-radius: 4px; cursor: pointer; transition: 0.1s; }}
            .log-row:hover {{ background-color: #21262d; }}
            .time {{ color: #00b4d8; font-family: monospace; margin-right: 15px; white-space: nowrap; }}
            .text {{ color: #c9d1d9; }}
        </style>
    </head>
    <body>
        <div class="panel"><audio id="audio" controls src="{audio_url}"></audio></div>
        <div class="container">{log_html}</div>
        <script>
            const audio = document.getElementById('audio');
            // 🔴 クリックされたら瞬時に時間を書き換えて自動再生
            function triggerSeek(secs) {{
                if(audio) {{ audio.currentTime = secs; audio.play().catch(e => console.log(e)); }}
            }}
        </script>
    </body>
    </html>
    """
    components.html(ui_html, height=530)
else:
    st.warning("音声フォルダが見つかりません。")
