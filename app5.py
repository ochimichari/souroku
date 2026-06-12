import os
import streamlit as st
import base64

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
    selected_folder = st.selectbox("選択", options=available_folders, label_visibility="collapsed")
    
    file_name = selected_folder.split("_")[-1] if "_" in selected_folder else selected_folder
    
    if "last_folder" not in st.session_state or st.session_state.last_folder != selected_folder:
        st.session_state.last_folder = selected_folder
        st.session_state.seek_seconds = 0
        st.session_state.trigger_seek = False

    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.m4a")
    txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.txt")
    color_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}_color.txt") # カラーファイルのパス

    # 音声ファイルをBase64エンコード
    with open(physical_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()

    # JSシーク制御
    seek_js = ""
    if st.session_state.trigger_seek:
        seek_js = f"""
        <script>
            var audio = window.parent.document.getElementById("custom-audio-player");
            if (audio) {{
                audio.currentTime = {st.session_state.seek_seconds};
                audio.play();
            }}
        </script>
        """
        st.session_state.trigger_seek = False

    # プレイヤーの描画
    st.markdown(
        f"""
        <div class="player-panel">
            <audio id="custom-audio-player" controls src="data:audio/mp4;base64,{audio_base64}" style="width:100%;"></audio>
            {seek_js}
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- 追加ポイント: color.txt のパースとCanvasによるカラーバー描画 ---
    color_segments = []
    if os.path.exists(color_path):
        with open(color_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("[") and "]" in line:
                    idx_close = line.find("]")
                    time_str = line[1:idx_close].strip()
                    status = line[idx_close+1:].strip() # SPEECH または MUSIC
                    
                    try:
                        p = time_str.split(":")
                        if len(p) == 2: secs = int(p[0]) * 60 + int(p[1])
                        elif len(p) == 3: secs = int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])
                        else: secs = 0
                    except ValueError:
                        secs = 0
                    
                    # 該当秒数における色を決定
                    color = "#00b4d8" if status == "SPEECH" else "#ff4b4b"
                    color_segments.append({"time": secs, "color": color})
    
    # データを時間順にソート
    color_segments.sort(key=lambda x: x["time"])
    
    # JavaScriptに安全に渡すため、色の配列（文字列）を生成
    # 例: ['#ff4b4b', '#ff4b4b', '#00b4d8', ...]
    color_array_js = str([seg["color"] for seg in color_segments])

    # Canvas描画用HTML/JSの埋め込み
    st.markdown(
        f"""
        <div class="color-bar-container">
            <canvas id="color-bar-canvas" style="width: 100%; height: 15px; display: block;"></canvas>
        </div>
        <script>
            (function() {{
                var canvas = window.parent.document.getElementById("color-bar-canvas");
                if (!canvas) return;
                var ctx = canvas.getContext("2d");
                var colors = {color_array_js};
                
                if (colors.length === 0) return;
                
                // 解像度をあげるため内部サイズを高める（ボケ防止）
                canvas.width = canvas.clientWidth * 2;
                canvas.height = 30;
                
                var totalPoints = colors.length;
                var segmentWidth = canvas.width / totalPoints;
                
                // 各秒のブロックをCanvasに敷き詰めて描画
                for (var i = 0; i < totalPoints; i++) {{
                    ctx.fillStyle = colors[i];
                    // 隙間ができないように1ピクセル多めに重ねて描画
                    ctx.fillRect(Math.floor(i * segmentWidth), 0, Math.ceil(segmentWidth) + 1, canvas.height);
                }}
            }})();
        </script>
        """,
        unsafe_allow_html=True
    )
    # -----------------------------------------------------------------

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
                    
                    if st.button(f"[{time_str}]  {text_content}", key=f"row_{secs}_{idx}"):
                        st.session_state.seek_seconds = secs
                        st.session_state.trigger_seek = True
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # スタイル調整（カラーバー用のクラスを追加）
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-bottom: 8px; }
        .player-panel { background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; width: 100% !important; }
        .player-panel audio { filter: invert(0.9) hue-rotate(180deg); }
        
        /* 新しいカラーバー容器のデザイン */
        .color-bar-container { 
            width: 100%; 
            height: 15px; 
            border-radius: 4px; 
            overflow: hidden; 
            border: 1px solid #00b4d8; 
            margin-top: 15px;
            background-color: #161b22;
        }
        
        .log-container { background-color: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 10px; max-height: 380px; overflow-y: auto; }
        
        div[data-testid="element-container"]:has(div[data-testid="stButton"]) { width: 100% !important; max-width: 100% !important; margin-bottom: 0px !important; }
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
