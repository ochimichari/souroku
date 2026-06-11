import os
import streamlit as st

st.set_page_config(layout="centered")
st.markdown('<div style="text-align: center; margin-bottom: 20px;"><h2 style="color: #00b4d8; font-family: sans-serif; letter-spacing: 1px;">奏録 / SOUROKU</h2></div>', unsafe_allow_html=True)

STATIC_DIR = "static"
available_folders = sorted([f for f in os.listdir(STATIC_DIR) if os.path.isdir(os.path.join(STATIC_DIR, f))]) if os.path.exists(STATIC_DIR) else []

if available_folders:
    st.markdown('<p class="section-title">Select session</p>', unsafe_allow_html=True)
    selected_folder = st.selectbox("再生する音声を選択してください", options=available_folders, label_visibility="collapsed")
    
    file_name = selected_folder.split("_")[-1] if "_" in selected_folder else selected_folder
    
    # ファイル切り替え時に再生時間をゼロにリセット
    if "last_folder" not in st.session_state or st.session_state.last_folder != selected_folder:
        st.session_state.last_folder = selected_folder
        st.session_state.seek_seconds = 0
        st.session_state.auto_play = False

    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.m4a")
    txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.txt")
    color_txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}_color.txt")

    # 音声プレイヤー（前段のリフレッシュでセットされた位置から、 autoplay で確実に音が鳴ります）
    st.markdown('<div class="player-panel">', unsafe_allow_html=True)
    st.audio(physical_path, format="audio/mp4", start_time=st.session_state.seek_seconds, autoplay=st.session_state.auto_play)
    st.markdown('<div class="time-display-mock">00:00 / 12:12</div></div>', unsafe_allow_html=True)

    # 🔴【カラーバーの解析と、隠しボタンの同時生成】
    colorbar_inner_html = ""
    if os.path.exists(color_txt_path):
        with open(color_txt_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if line.startswith("[") and "]" in line:
                    idx_close = line.find("]")
                    time_str = line[1:idx_close].strip()
                    status = line[idx_close+1:].strip().upper()
                    
                    try:
                        p = time_str.split(":")
                        if len(p) == 2: secs = int(p[0]) * 60 + int(p[1])
                        elif len(p) == 3: secs = int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])
                        else: secs = 0
                    except ValueError: secs = idx

                    color_code = "#ff4b4b" if "SPEECH" in status else "#00b4d8" if "MUSIC" in status else "#30363d"
                    
                    # 🔴 各マスのonclickで、対応する裏のStreamlitボタン（隠しボタン）を強制クリックさせます
                    colorbar_inner_html += f'<div class="bar-tick" style="background: {color_code};" onclick="document.getElementById(\'bar_btn_{secs}\').click();" onmouseover="updateHoverInfo(\'[{time_str}] {status}\')" onmouseout="clearHoverInfo()"></div>'

    # 🔴 マウスホバー時の情報を表示するテキストエリア（画像のイメージを再現）
    st.markdown('<div id="colorbar-hover-info" style="height: 20px; color: #8b949e; font-family: monospace; font-size: 13px; text-align: center; margin-top: 5px;">バーにマウスを乗せてください</div>', unsafe_allow_html=True)

    if colorbar_inner_html:
        st.markdown(f'<div class="color-bar-container">{colorbar_inner_html}</div>', unsafe_allow_html=True)
        
        # 🔴【ジャンプの連携】カラーバーの各秒数に対応する、Streamlit公式の「隠しボタン」を配置
        # 画面からはCSSで完全に消去（display:none）し、通信用としてのみ機能させます
        st.markdown('<div style="display:none;">', unsafe_allow_html=True)
        if os.path.exists(color_txt_path):
            with open(color_txt_path, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    if line.startswith("[") and "]" in line:
                        idx_close = line.find("]")
                        time_str = line[1:idx_close].strip()
                        try:
                            p = time_str.split(":")
                            if len(p) == 2: secs = int(p[0]) * 60 + int(p[1])
                            elif len(p) == 3: secs = int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])
                            else: secs = 0
                        except: secs = idx
                        
                        # バーが叩かれたら、このボタンが裏でクリックされ、安全にジャンプして自動再生されます
                        if st.button("seek", key=f"bar_btn_{secs}"):
                            st.session_state.seek_seconds = secs
                            st.session_state.auto_play = True
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ログセクション
    st.markdown('<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 25px; margin-bottom: 15px;"><span class="section-title" style="margin:0;">Session Logs</span><div><button class="mock-btn">設定</button><button class="mock-btn" style="background:#00b4d8; color:#0e1117; border:none;">編集</button></div></div>', unsafe_allow_html=True)

    # ログリストの描画
    st.markdown('<div class="log-container">', unsafe_allow_html=True)
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if line.startswith("[") and "]" in line:
                    idx_close = line.find("]")
                    time_str = line[1:idx_close].strip()
                    text_content = line[idx_close+1:].strip()
                    
                    try:
                        p = time_str.split(":")
                        if len(p) == 2: secs = int(p[0]) * 60 + int(p[1])
                        elif len(p) == 3: secs = int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])
                        else: secs = 0
                    except ValueError: secs = 0
                    
                    if st.button(f"[{time_str}]  {text_content}", key=f"row_{secs}_{idx}"):
                        st.session_state.seek_seconds = secs
                        st.session_state.auto_play = True
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 🔴 マウスホバー時に中央に文字を表示するための軽量なJavaScript
    st.markdown(
        """
        <script>
        function updateHoverInfo(text) {
            const el = document.getElementById('colorbar-hover-info');
            if (el) { el.innerText = text; el.style.color = '#00b4d8'; }
        }
        function clearHoverInfo() {
            const el = document.getElementById('colorbar-hover-info');
            if (el) { el.innerText = 'バーにマウスを乗せてください'; el.style.color = '#8b949e'; }
        }
        </script>
        """,
        unsafe_allow_html=True
    )

    # スタイルCSS
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-bottom: 8px; }
        .player-panel { background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; }
        .player-panel audio { width: 100%; filter: invert(0.9) hue-rotate(180deg); }
        .time-display-mock { text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }
        
        .color-bar-container { display: flex; height: 18px; border-radius: 4px; overflow: hidden; border: 1px solid #00b4d8; margin-top: 5px; margin-bottom: 5px; background-color: #161b22; }
        .bar-tick { flex: 1; height: 100%; cursor: pointer; }
        .bar-tick:hover { opacity: 0.4; background-color: #ffffff !important; } /* ホバーしたマスを白く光らせる */
        
        .log-container { background-color: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 10px; max-height: 380px; overflow-y: auto; }
        
        div[data-testid="stButton"] { width: 100% !important; margin-bottom: 2px !important; }
        div[data-testid="stButton"] button {
            width: 100% !important; background: transparent !important; border: none !important;
            color: #c9d1d9 !important; text-align: left !important; padding: 8px 12px !important;
            font-size: 14px !important; border-radius: 4px !important; justify-content: flex-start !important;
        }
        div[data-testid="stButton"] button:hover { background-color: #21262d !important; color: #ffffff !important; }
        div[data-testid="stButton"] button::first-line { color: #00b4d8 !important; font-family: monospace !important; }
        
        .mock-btn { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px; }
        div[data-baseweb="select"] > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }
        div[data-testid="stStatusWidget"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
