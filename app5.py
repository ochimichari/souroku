import os
import streamlit as st
import streamlit.components.v1 as components

# 画面設定とダークモード風タイトル
st.set_page_config(layout="centered")
st.markdown('<div style="text-align: center; margin-bottom: 20px;"><h2 style="color: #00b4d8; font-family: sans-serif; letter-spacing: 1px;">奏録 / SOUROKU</h2></div>', unsafe_allow_html=True)

STATIC_DIR = "static"
available_folders = sorted([f for f in os.listdir(STATIC_DIR) if os.path.isdir(os.path.join(STATIC_DIR, f))]) if os.path.exists(STATIC_DIR) else []

if available_folders:
    st.markdown('<p class="section-title">Select session</p>', unsafe_allow_html=True)
    selected_folder = st.selectbox("再生する音声を選択してください", options=available_folders, label_visibility="collapsed")
    
    # 🔴【復活】フォルダ名からファイル名を取り出すルール（20260607_airs -> airs）
    file_name = selected_folder.split("_")[-1] if "_" in selected_folder else selected_folder
    
    # 🔴【維持】ファイル切り替え時に再生時間をゼロにリセット
    if "last_folder" not in st.session_state or st.session_state.last_folder != selected_folder:
        st.session_state.last_folder = selected_folder
        st.session_state.seek_seconds = 0

    audio_url = f"/static/{selected_folder}/{file_name}.m4a"
    txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.txt")

    # ログファイルの解析とHTML行の生成
    log_html = ""
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("[") and "]" in line:
                    idx_close = line.find("]")
                    time_str = line[1:idx_close].strip()
                    text_content = line[idx_close+1:].strip()
                    
                    # 🔴【復活】時:分:秒、あるいは分:秒を正確に計算するロジック
                    try:
                        p = time_str.split(":")
                        if len(p) == 2: secs = int(p[0]) * 60 + int(p[1])
                        elif len(p) == 3: secs = int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])
                        else: secs = 0
                    except ValueError: secs = 0
                    
                    # 🔴【維持】行全体をクリック可能にし、水色でハイライト
                    log_html += f'<div class="log-row" onclick="triggerSeek({secs})"><span class="time">[{time_str}]</span><span class="text">{text_content}</span></div>\n'

    # 画像にそっくりな黒基調・水色アクセントのデザインHTML
    ui_html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><style>
        body {{ background-color: #0e1117; color: #e2e8f0; font-family: sans-serif; margin: 0; padding: 0; }}
        .panel {{ background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-bottom: 20px; }}
        audio {{ width: 100%; filter: invert(0.9) hue-rotate(180deg); }}
        .color-bar {{ display: flex; height: 15px; border-radius: 4px; overflow: hidden; margin: 15px 0; border: 1px solid #00b4d8; }}
        .log-container {{ background-color: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 10px; max-height: 380px; overflow-y: auto; }}
        .log-row {{ display: flex; align-items: flex-start; padding: 8px 12px; margin-bottom: 4px; border-radius: 4px; cursor: pointer; transition: 0.1s; user-select: none; }}
        .log-row:hover {{ background-color: #21262d; }}
        .log-row:hover .text {{ color: #ffffff; }}
        .time {{ color: #00b4d8; font-family: monospace; font-size: 14px; margin-right: 15px; white-space: nowrap; }}
        .text {{ font-size: 14px; color: #c9d1d9; line-height: 1.4; }}
    </style></head><body>
        <div class="panel"><audio id="audio" controls src="{audio_url}"></audio></div>
        <div class="color-bar">
            <div style="flex: 2; background: #00b4d8;"></div><div style="flex: 1; background: #ff4b4b;"></div>
            <div style="flex: 3; background: #00b4d8;"></div><div style="flex: 1; background: #ff4b4b;"></div>
            <div style="flex: 1; background: #00b4d8;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <span style="font-weight: bold; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px;">Session Logs</span>
            <div><button style="background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px;">設定</button>
            <button style="background: #00b4d8; color: #0e1117; border: none; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px;">編集</button></div>
        </div>
        <div class="log-container">{log_html}</div>
        <script>
            const audio = document.getElementById('audio');
            function triggerSeek(secs) {{
                if(audio) {{ audio.currentTime = secs; audio.play().catch(e => console.log(e)); }}
            }}
        </script>
    </body></html>
    """
    
    components.html(ui_html, height=580)
    
    # セレクトボックス自体のダークカスタムCSS
    st.markdown('<style>.section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-bottom: 8px; } div[data-baseweb="select"] > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }</style>', unsafe_allow_html=True)
else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
