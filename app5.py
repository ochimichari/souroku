import os
import streamlit as st

# 画面設定
st.set_page_config(layout="centered")
st.markdown('<div style="text-align: center; margin-bottom: 20px;"><h2 style="color: #00b4d8; font-family: sans-serif; letter-spacing: 1px;">奏録 / SOUROKU</h2></div>', unsafe_allow_html=True)

STATIC_DIR = "static"
available_folders = []

# 音声ファイルが物理的に存在するフォルダだけを選択肢に入れる
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
    selected_folder = st.selectbox("再生する音声を選択してください", options=available_folders, label_visibility="collapsed")
    
    file_name = selected_folder.split("_")[-1] if "_" in selected_folder else selected_folder
    
    # ファイル切り替え時にタイマーを0秒にクリア
    if "last_folder" not in st.session_state or st.session_state.last_folder != selected_folder:
        st.session_state.last_folder = selected_folder
        st.session_state.seek_seconds = 0
        st.session_state.auto_play = False

    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.m4a")
    txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.txt")
    color_txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}_color.txt")

    # 音声プレイヤー
    st.markdown('<div class="player-panel">', unsafe_allow_html=True)
    st.audio(physical_path, format="audio/mp4", start_time=st.session_state.seek_seconds, autoplay=st.session_state.auto_play)
    st.markdown('<div class="time-display-mock">00:00 / 12:12</div></div>', unsafe_allow_html=True)

    # 🔴【カラーバーの生成】
    # 確実に色が効くように、ボタンのテキストの中身に隠し区別文字を仕込みます
    if os.path.exists(color_txt_path):
        with open(color_txt_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip().startswith("[")]
            
        if lines:
            cols = st.columns(len(lines), gap="small")
            for idx, line in enumerate(lines):
                idx_close = line.find("]")
                time_str = line[1:idx_close].strip()
                status = line[idx_close+1:].strip().upper()
                
                try:
                    p = time_str.split(":")
                    if len(p) == 2: secs = int(p[0]) * 60 + int(p[1])
                    elif len(p) == 3: secs = int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])
                    else: secs = idx
                except: secs = idx

                # 🔴 CSSで安全にテキストを識別するためのマーク（S / M）を配置します
                # 文字は透明化（color:transparent）されるため画面には映りません
                btn_label = "S" if "SPEECH" in status else "M" if "MUSIC" in status else "G"
                
                with cols[idx]:
                    if st.button(btn_label, key=f"bar_{idx}_{secs}", help=f"[{time_str}] {status}"):
                        st.session_state.seek_seconds = secs
                        st.session_state.auto_play = True
                        st.rerun()

    st.markdown('<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 25px; margin-bottom: 15px;"><span class="section-title" style="margin:0;">Session Logs</span><div><button class="mock-btn">設定</button><button class="mock-btn" style="background:#00b4d8; color:#0e1117; border:none;">編集</button></div></div>', unsafe_allow_html=True)

    # ログ全体のコンテナ
    st.markdown('<div class="log-master-outer">', unsafe_allow_html=True)

    # ログリスト（st.button）を表示
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
                    except: secs = 0
                    
                    if st.button(f"[{time_str}]  {text_content}", key=f"row_{secs}_{idx}"):
                        st.session_state.seek_seconds = secs
                        st.session_state.auto_play = True
                        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


    # 🔴【完璧な色分けの復活】ボタン内の隠しマークをCSSで直接染め分ける確実なスタイル定義
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-bottom: 8px; }
        .player-panel { background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; width: 100% !important; box-sizing: border-box; }
        .player-panel audio { width: 100%; filter: invert(0.9) hue-rotate(180deg); }
        .time-display-mock { text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }
        
        /* カラーバーの基本レイアウト設定 */
        div[data-testid="stHorizontalBlock"] { gap: 0px !important; background-color: #161b22; border: 1px solid #00b4d8; border-radius: 4px; overflow: hidden; height: 22px; width: 100% !important; margin-top: 10px; margin-bottom: 5px; box-sizing: border-box; }
        div[data-testid="stHorizontalBlock"] div[data-testid="element-container"] { width: 100% !important; height: 100% !important; padding: 0 !important; margin: 0 !important; }
        div[data-testid="stHorizontalBlock"] button {
            width: 100% !important; height: 22px !important; min-height: 22px !important; border: none !important; border-radius: 0px !important; padding: 0 !important; margin: 0 !important; cursor: pointer; transition: opacity 0.05s;
            color: transparent !important; /* 🔴 内側の「S」「M」の文字を完全に非表示（透明化）にします */
        }
        div[data-testid="stHorizontalBlock"] button:hover { opacity: 0.4 !important; background-color: #ffffff !important; }
        
        /* 🔴【最重要】ボタン内部のテキストノードの条件（S ＝ 赤、M ＝ 青）を正確にキャッチして背景を着色 */
        div[data-testid="stHorizontalBlock"] button:has(p:contains("S")),
        div[data-testid="stHorizontalBlock"] button:has(div:contains("S")) { background-color: #ff4b4b !important; }
        
        div[data-testid="stHorizontalBlock"] button:has(p:contains("M")),
        div[data-testid="stHorizontalBlock"] button:has(div:contains("M")) { background-color: #00b4d8 !important; }
        
        div[data-testid="stHorizontalBlock"] button:has(p:contains("G")),
        div[data-testid="stHorizontalBlock"] button:has(div:contains("G")) { background-color: #30363d !important; }

        /* ログコンテナ全体の横幅100%維持ルール（以前最も安定していたものを完全維持） */
        div.log-master-outer {
            background-color: #161b22 !important;
            border: 1px solid #21262d !important;
            border-radius: 8px !important;
            padding: 10px !important;
            max-height: 380px !important;
            overflow-y: auto !important;
            width: 100% !important;
            display: block !important;
            box-sizing: border-box;
        }
        
        div.log-master-outer div[data-testid="element-container"],
        div.log-master-outer div[data-testid="stButton"] { 
            width: 100% !important; 
            max-width: 100% !important;
            margin-bottom: 0px !important; 
            display: block !important; 
        }
        
        div.log-master-outer div[data-testid="stButton"] button {
            width: 100% !important; background: transparent !important; border: none !important;
            color: #c9d1d9 !important; text-align: left !important; padding: 6px 12px !important;
            font-size: 14px !important; border-radius: 4px !important; justify-content: flex-start !important;
            display: block !important;
        }
        div.log-master-outer div[data-testid="stButton"] button:hover { background-color: #21262d !important; color: #ffffff !important; }
        div.log-master-outer div[data-testid="stButton"] button::first-line { color: #00b4d8 !important; font-family: monospace !important; }
        
        .mock-btn { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px; }
        div[data-baseweb="select"] > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }
        div[data-testid="stStatusWidget"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
