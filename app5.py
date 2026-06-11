import os
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
    # 🔴 カラーバー専用テキストのパス (例: static/20260607_airs/airs_color.txt)
    color_txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}_color.txt")

    # 音声プレイヤー
    st.markdown('<div class="player-panel" id="target-audio-box">', unsafe_allow_html=True)
    st.audio(physical_path, format="audio/mp4", start_time=st.session_state.seek_seconds, autoplay=st.session_state.auto_play)
    st.markdown('<div class="time-display-mock">00:00 / 12:12</div></div>', unsafe_allow_html=True)

    # 🔴【新規実装】[ファイル名]_color.txt を解析して、1秒ごとのカラーバーHTMLを生成
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
                        secs = int(p[0]) * 60 + int(p[1]) if len(p) == 2 else 0
                    except ValueError:
                        secs = idx # 予期せぬエラー時は行インデックスを割り当て

                    # SPEECHは赤（#ff4b4b）、MUSICは青（#00b4d8）、それ以外はグレー
                    if "SPEECH" in status:
                        color_code = "#ff4b4b"
                    elif "MUSIC" in status:
                        color_code = "#00b4d8"
                    else:
                        color_code = "#30363d"
                    
                    # 1秒ごとに幅1マスの均等なブロックを生成。データ属性としてジャンプ秒数（data-sec）を記録
                    colorbar_inner_html += f'<div class="bar-tick" style="background: {color_code};" data-sec="{secs}" title="[{time_str}] {status}"></div>'

    # 完成したカラーバーを画面に描画
    if colorbar_inner_html:
        st.markdown(f'<div class="color-bar-container" id="custom-colorbar">{colorbar_inner_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="color-bar-container"><div style="flex:1; background:#30363d;"></div></div>', unsafe_allow_html=True)

    # ログセクションヘッダー
    st.markdown('<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 25px; margin-bottom: 15px;"><span class="section-title" style="margin:0;">Session Logs</span><div><button class="mock-btn">設定</button><button class="mock-btn" style="background:#00b4d8; color:#0e1117; border:none;">編集</button></div></div>', unsafe_allow_html=True)

    # ログリスト（Session Logs）の描画
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
                    
                    # 行全体を模した st.button を配置（隔離空間の壁がないため、ここからJavaScriptで連動できます）
                    if st.button(f"[{time_str}]  {text_content}", key=f"row_{secs}_{idx}"):
                        st.session_state.seek_seconds = secs
                        st.session_state.auto_play = True
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 🔴【新規実装】ログ行クリックに加えて、カラーバーをクリックした時にも瞬時にジャンプ＆自動再生させるJavaScript
    st.markdown(
        """
        <script>
        // 画面上のカラーバー要素を取得
        const barContainer = document.getElementById('custom-colorbar');
        if (barContainer) {
            // バー内の細かな1秒ごとのブロック（bar-tick）のどれかがクリックされたかを検知
            barContainer.addEventListener('click', function(e) {
                const tick = e.target;
                // クリックされた要素が秒数データ（data-sec）を持っているか確認
                if (tick && tick.classList.contains('bar-tick')) {
                    const targetSec = parseInt(tick.getAttribute('data-sec'), 10);
                    
                    // 親画面の公式プレイヤーを特定
                    const audioNode = document.querySelector('#target-audio-box audio');
                    if (audioNode) {
                        audioNode.currentTime = targetSec; // 指定秒数にジャンプ
                        audioNode.play().catch(err => console.log("再生開始制限", err)); // 自動再生キック
                    }
                }
            });
        }
        </script>
        """,
        unsafe_allow_html=True
    )

    # スタイルCSS（色の調整と配置）
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-bottom: 8px; }
        .player-panel { background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; }
        .player-panel audio { width: 100%; filter: invert(0.9) hue-rotate(180deg); }
        .time-display-mock { text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }
        
        /* 🔴 カラーバー外枠（1秒ごとのデータを横並びに均等にフィットさせる） */
        .color-bar-container { 
            display: flex; 
            height: 18px; 
            border-radius: 4px; 
            overflow: hidden; 
            border: 1px solid #00b4d8; 
            margin-top: 15px; 
            margin-bottom: 5px; 
            background-color: #161b22;
        }
        /* 🔴 1秒ごとの極細の縦線要素のスタイル。flex: 1 で全体の長さに自動で均等分配されます */
        .bar-tick {
            flex: 1;
            height: 100%;
            transition: opacity 0.05s;
        }
        .bar-tick:hover {
            opacity: 0.6; /* マウスを当てた箇所をわかりやすくハイライト */
        }
        
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
