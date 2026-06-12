import os
import streamlit as st

st.set_page_config(layout="centered")
st.markdown('<div style="text-align: center; margin-bottom: 20px;"><h2 style="color: #00b4d8; font-family: sans-serif; letter-spacing: 1px;">奏録 / SOUROKU</h2></div>', unsafe_allow_html=True)

STATIC_DIR = "static"
available_folders = []

# 音声ファイルが物理的に実在するフォルダだけを厳選してエラーを防ぐ
if os.path.exists(STATIC_DIR):
    for folder in os.listdir(STATIC_DIR):
        folder_path = os.path.join(STATIC_DIR, folder)
        if os.path.isdir(folder_path):
            file_name = folder.split("_")[-1] if "_" in folder else folder
            m4a_path = os.path.join(folder_path, f"{file_name}.m4a")
            if os.path.exists(m4a_path):
                available_folders.append(folder)

available_folders.sort()

if available_folders:
    st.markdown('<p class="section-title">Select session</p>', unsafe_allow_html=True)
    selected_folder = st.selectbox("選択", options=available_folders, label_visibility="collapsed")
    
    file_name = selected_folder.split("_")[-1] if "_" in selected_folder else selected_folder
    
    # --- 修正ポイント：セッション状態の安全な初期化 ---
    if "seek_seconds" not in st.session_state:
        st.session_state.seek_seconds = 0
    if "auto_play" not in st.session_state:
        st.session_state.auto_play = False

    # ファイル切り替え時にタイマーを確実に0秒にクリア
    if "last_folder" not in st.session_state or st.session_state.last_folder != selected_folder:
        st.session_state.last_folder = selected_folder
        st.session_state.seek_seconds = 0
        st.session_state.auto_play = False

    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.m4a")
    txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.txt")
    color_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}_color.txt")

    # 音声プレイヤー
    st.markdown('<div class="player-panel">', unsafe_allow_html=True)
    st.audio(physical_path, format="audio/mp4", start_time=st.session_state.seek_seconds, autoplay=st.session_state.auto_play)
    st.markdown('<div class="time-display-mock">00:00 / 12:12</div></div>', unsafe_allow_html=True)

    # --- CSSグラデーション方式のカラーバー ---
    gradient_steps = []
    if os.path.exists(color_path):
        with open(color_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip().startswith("[") and "]" in line]
            total_lines = len(lines)
            
            if total_lines > 0:
                for idx, line in enumerate(lines):
                    idx_close = line.find("]")
                    status = line[idx_close+1:].strip()
                    color = "#00b4d8" if status == "SPEECH" else "#ff4b4b"
                    
                    # 1秒ごとの区間をパーセンテージで計算
                    start_pct = (idx / total_lines) * 100
                    end_pct = ((idx + 1) / total_lines) * 100
                    
                    # 境界線がボケないようにソリッドな色の塊を作る
                    gradient_steps.append(f"{color} {start_pct}%")
                    gradient_steps.append(f"{color} {end_pct}%")
                
                gradient_css = f"background: linear-gradient(to right, {', '.join(gradient_steps)});"
            else:
                gradient_css = "background: #161b22;"
    else:
        gradient_css = "background: #161b22;"

    # 計算した背景色を適用したカラーバーをMarkdownで直接出力
    st.markdown(f'<div class="color-bar" style="{gradient_css}"></div>', unsafe_allow_html=True)
    
    # ログヘッダー
    st.markdown('<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 25px; margin-bottom: 15px;"><span class="section-title" style="margin:0;">Session Logs</span><div><button class="mock-btn">設定</button><button class="mock-btn" style="background:#00b4d8; color:#0e1117; border:none;">編集</button></div></div>', unsafe_allow_html=True)

    # 行全域クリックの文字起こしログ枠
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
                    
                    # 1行全体をひとつの st.button にし、CSSで文字起こし行に変形
                    if st.button(f"[{time_str}]  {text_content}", key=f"row_{secs}_{idx}"):
                        st.session_state.seek_seconds = secs
                        st.session_state.auto_play = True  # クリックされたら即座に再生ON
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 画面全体を画像通りの黒基調に染め、ボタンを行全体クリックに変形させる完成版CSS
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-bottom: 8px; }
        .player-panel { background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; width: 100% !important; }
        .player-panel audio { width: 100%; filter: invert(0.9) hue-rotate(180deg); }
        .time-display-mock { text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }
        .color-bar { display: flex; height: 15px; border-radius: 4px; overflow: hidden; border: 1px solid #00b4d8; margin-top: 15px; }
        
        /* ログコンテナ枠を横幅100%いっぱいに固定 */
        .log-container { background-color: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 10px; max-height: 380px; overflow-y: auto; }
        
        /* 四角いボタンを行全体のフラットな美しい文字起こしデザインに完全変形 */
        div[data-testid="element-container"]:has(div[data-testid="stButton"]) { width: 100% !important; max-width: 100% !important; margin-bottom: 0px !important; }
        div[data-testid="stButton"] { width: 100% !important; margin-bottom: 2px !important; }
        div[data-testid="stButton"] button {
            width: 100% !important; background: transparent !important; border: none !important;
            color: #c9d1d9 !important; text-align: left !important; padding: 8px 12px !important;
            font-size: 14px !important; border-radius: 4px !important; justify-content: flex-start !important;
        }
        /* マウスを乗せたら行全体が明るくなり、文字が白くハイライトされる */
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
