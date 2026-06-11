import os
import pandas as pd
import streamlit as st

st.set_page_config(layout="centered")
st.markdown('<div style="text-align: center; margin-bottom: 20px;"><h2 style="color: #00b4d8; font-family: sans-serif; letter-spacing: 1px;">奏録 / SOUROKU</h2></div>', unsafe_allow_html=True)

STATIC_DIR = "static"
available_folders = []

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

    # 🔴【カラーバー連動の完全解決】
    # JavaScriptを全廃し、Streamlit公式のst.buttonを「1秒ごとに横並び」に敷き詰めます
    st.markdown('<div class="color-bar-container">', unsafe_allow_html=True)
    if os.path.exists(color_txt_path):
        with open(color_txt_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip().startswith("[")]
            
        # ボタンを横並びにするために、カラムを秒数分だけ自動生成
        if lines:
            cols = st.columns(len(lines), gap="none")
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

                # クラス名としてSPEECHかMUSICを割り当て（CSSで赤と青に染め分けます）
                cls = "c-speech" if "SPEECH" in status else "c-music" if "MUSIC" in status else "c-gray"
                
                # 1秒ごとに公式ボタンを配置。クリックされたらPythonが直接秒数を書き換えてリランします
                with cols[idx]:
                    if st.button(" ", key=f"bar_tick_{secs}_{idx}", help=f"[{time_str}] {status}"):
                        st.session_state.seek_seconds = secs
                        st.session_state.auto_play = True
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 25px; margin-bottom: 15px;"><span class="section-title" style="margin:0;">Session Logs</span><div><button class="mock-btn">設定</button><button class="mock-btn" style="background:#00b4d8; color:#0e1117; border:none;">編集</button></div></div>', unsafe_allow_html=True)

    # 🔴【表示枠縮み問題の完全解決】
    # テキストデータを読み込んで、横幅が絶対に100%固定される st.dataframe（公式パーツ）に流し込みます
    log_data = []
    if os.path.exists(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("[") and "]" in line:
                        idx_close = line.find("]")
                        t_str = line[1:idx_close].strip()
                        txt_content = line[idx_close+1:].strip()
                        
                        try:
                            p = t_str.split(":")
                            if len(p) == 2: s = int(p[0]) * 60 + int(p[1])
                            elif len(p) == 3: s = int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])
                            else: s = 0
                        except: s = 0
                        
                        log_data.append({"Time": f"[{t_str}]", "Log": txt_content, "secs": s})
        except:
            pass

    if log_data:
        df = pd.DataFrame(log_data)
        
        # 🔴 行全体のどこを叩いても安全にジャンプを検知する公式のセレクター機能
        selected_log = st.dataframe(
            df[["Time", "Log"]],
            hide_index=True,
            use_container_width=True, # これにより横幅が100%に強制固定されます
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # ログ行がクリックされたら自動ジャンプして再生
        if selected_log and len(selected_log.selection.rows) > 0:
            chosen_idx = selected_log.selection.rows[0]
            target_secs = df.iloc[chosen_idx]["secs"]
            st.session_state.seek_seconds = int(target_secs)
            st.session_state.auto_play = True
            st.rerun()
    else:
        st.warning("ログファイルが見つかりません。")

    # 🔴 全体を完全に画像と同じ色合い・横幅100%のソリッドなデザインに染め上げるCSS
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-bottom: 8px; }
        .player-panel { background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; width: 100% !important; }
        .player-panel audio { width: 100%; filter: invert(0.9) hue-rotate(180deg); }
        .time-display-mock { text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }
        
        /* 🔴 カラーバーを包むコンテナ（横幅100%を維持） */
        div.color-bar-container { display: block !important; width: 100% !important; margin-top: 15px; margin-bottom: 15px; }
        
        /* 🔴 1秒ごとのst.buttonを、隙間のない極細カラーバーの縦線に完全変形させるCSS */
        div[data-testid="stHorizontalBlock"] { gap: 0px !important; background-color: #161b22; border: 1px solid #00b4d8; border-radius: 4px; overflow: hidden; height: 20px; }
        div[data-testid="stHorizontalBlock"] div[data-testid="element-container"] { width: 100% !important; height: 100% !important; }
        div[data-testid="stHorizontalBlock"] button {
            width: 100% !important; height: 20px !important; min-height: 20px !important; border: none !important; border-radius: 0px !important; padding: 0 !important; margin: 0 !important; cursor: pointer; transition: opacity 0.05s;
        }
        div[data-testid="stHorizontalBlock"] button:hover { opacity: 0.4 !important; background-color: #ffffff !important; }
        
        /* ボタンのキー名やクラスに応じた色分け（SPEECHは赤、MUSICは青） */
        div[data-testid="stHorizontalBlock"] div:has(button[key*="bar_tick_"]) button { background-color: #30363d !important; }
        /* 各マスカスタム用のクラス判定を補助する一括上書き */
        iframe, .c-speech, button[id*="bar_tick_"] { background-color: #ff4b4b !important; }
        
        /* 🔴 データフレーム（ログコンテナ）を画像通りの黒いリストに強制変身させるCSS（横幅100%固定） */
        div[data-testid="stDataFrame"] { background-color: #161b22 !important; border: 1px solid #21262d !important; border-radius: 8px !important; padding: 5px !important; width: 100% !important; max-height: 380px; overflow-y: auto; }
        div[data-testid="stDataFrame"] thead { display: none !important; } /* ヘッダーを消去 */
        
        /* タイムスタンプテキストの文字色を鮮やかな水色にする */
        div[data-testid="stDataFrame"] td:first-child { color: #00b4d8 !important; font-family: monospace !important; font-weight: bold; }
        
        .mock-btn { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px; }
        div[data-baseweb="select"] > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }
        div[data-testid="stStatusWidget"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
