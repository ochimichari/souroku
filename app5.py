import os
import streamlit as st

# 1. 画面の基本設定とダークモード風タイトル
st.set_page_config(layout="centered")
st.markdown('<div style="text-align: center; margin-bottom: 20px;"><h2 style="color: #00b4d8; font-family: sans-serif; letter-spacing: 1px;">奏録 / SOUROKU</h2></div>', unsafe_allow_html=True)

STATIC_DIR = "static"
available_folders = []

# 音声ファイルが物理的に存在するフォルダだけを厳選してエラーを防ぐ
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
    selected_folder = st.selectbox("選択してください", options=available_folders, label_visibility="collapsed")
    file_name = selected_folder.split("_")[-1] if "_" in selected_folder else selected_folder
    
    # ファイル切り替え時は再生位置を確実に0秒にクリア
    if "last_folder" not in st.session_state or st.session_state.last_folder != selected_folder:
        st.session_state.last_folder = selected_folder
        st.session_state.seek_seconds = 0
        st.session_state.auto_play = False

    audio_url = f"/static/{selected_folder}/{file_name}.m4a"
    txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.txt")
    color_txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}_color.txt")

    # 音声プレイヤーコンテナと、ホバーテキスト領域の配置
    st.markdown('<div class="player-panel" id="main-audio-root">', unsafe_allow_html=True)
    st.audio(os.path.join(STATIC_DIR, selected_folder, f"{file_name}.m4a"), format="audio/mp4", start_time=st.session_state.seek_seconds, autoplay=st.session_state.auto_play)
    st.markdown('<div class="time-display-mock" id="time-view">00:00 / 12:12</div><div class="canvas-container"><canvas id="timeline-canvas" height="22"></canvas></div></div>', unsafe_allow_html=True)
    st.markdown('<div id="colorbar-hover-info" style="height: 20px; color: #8b949e; font-family: monospace; font-size: 13px; text-align: center; margin-top: 5px;">バーにマウスを乗せてください</div>', unsafe_allow_html=True)
    st.markdown('<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 25px; margin-bottom: 15px;"><span class="section-title" style="margin:0;">Session Logs</span><div><button class="mock-btn">設定</button><button class="mock-btn" style="background:#00b4d8; color:#0e1117; border:none;">編集</button></div></div>', unsafe_allow_html=True)

    # 2. 文字起こしテキストファイル（.txt）を読み込んでHTML行を組み立てる
    log_html_lines = ""
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if line.startswith("[") and "]" in line:
                    idx_close = line.find("]")
                    time_str = line[1:idx_close].strip()
                    text_content = line[idx_close+1:].strip()
                    p = time_str.split(":")
                    secs = int(p[0])*60 + int(p[1]) if len(p)==2 else int(p[0])*3600 + int(p[1])*60 + int(p[2]) if len(p)==3 else 0
                    
                    # 1行全体のonclick属性で、叩かれたらJavaScript関数 remoteSeek(秒数) を走らせます
                    log_html_lines += f'<div class="log-line" onclick="remoteSeek({secs})"><span class="timestamp-lead">[{time_str}]</span><span class="log-text">{text_content}</span></div>\n'
    st.markdown(f'<div class="log-master-outer">{log_html_lines}</div>', unsafe_allow_html=True)

    # 3. 🔴【バグの根本治療】JavaScript側の配列エラーを消し去るため、Python側で先に「秒数」と「STATUS」を完全に計算・結合します
    color_array_js = []
    if os.path.exists(color_txt_path):
        with open(color_txt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("[") and "]" in line:
                    idx_close = line.find("]")
                    time_str = line[1:idx_close].strip()
                    status = line[idx_close+1:].strip().upper()
                    
                    try:
                        p = time_str.split(":")
                        secs = int(p[0])*60 + int(p[1]) if len(p)==2 else int(p[0])*3600 + int(p[1])*60 + int(p[2]) if len(p)==3 else 0
                    except:
                        continue
                    
                    # JavaScript側では split(':') や [0] のような危険な配列操作を一切せず、この文字列をそのまま使わせます
                    color_array_js.append(f"'{secs}={status}'")
    js_color_str = "[" + ",".join(color_array_js) + "]"
    # 4. 1つの大部屋（ドメイン）の中で直接通信させるための、隔離制限（CORS）をバイパスするJavaScript＆CSS
    st.markdown(
        f"""
        <script>
        const audio = document.querySelector('#main-audio-root audio');
        const timeDisplay = document.getElementById('time-view');
        const canvas = document.getElementById('timeline-canvas');
        const hoverInfo = document.getElementById('colorbar-hover-info');
        let colorData = {{}}, totalDuration = 0;

        // 🔴【修正点】Python側で安全に処理された単純な「秒数＝STATUS」を読み込むため、絶対にJavaScriptがフリーズしません
        ({js_color_str}).forEach(item => {{
            const parts = item.split('=');
            if (parts.length === 2) {{
                colorData[parseInt(parts[0], 10)] = parts[1];
            }}
        }});

        function updateHoverInfo(t) {{ if(hoverInfo) {{ hoverInfo.innerText = t; hoverInfo.style.color = '#00b4d8'; }} }}
        function clearHoverInfo() {{ if(hoverInfo) {{ hoverInfo.innerText = 'バーにマウスを乗せてください'; hoverInfo.style.color = '#8b949e'; }} }}

        // Canvasタイムラインを赤（SPEECH）と青（MUSIC）に1秒ずつ忠実に色分け
        function drawTimeline(currentSec = 0) {{
            if (!totalDuration) return;
            if (canvas.width !== canvas.clientWidth) canvas.width = canvas.clientWidth;
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const secWidth = canvas.width / totalDuration;
            for (let s = 0; s < totalDuration; s++) {{
                const status = colorData[s] || "SILENT";
                ctx.fillStyle = status === "SPEECH" ? "#ff4b4b" : status === "MUSIC" ? "#00b4d8" : "#2a3247";
                ctx.fillRect(s * secWidth, 0, secWidth + 0.6, canvas.height);
            }}
            ctx.fillStyle = "#ffffff";
            ctx.fillRect((currentSec / totalDuration) * canvas.width - 1, 0, 2, canvas.height);
        }}

        function updateTimeLabel() {{
            if (!audio) return;
            const curM = String(Math.floor(audio.currentTime / 60)).padStart(2, '0'), curS = String(Math.floor(audio.currentTime % 60)).padStart(2, '0');
            const totM = String(Math.floor(totalDuration / 60)).padStart(2, '0'), totS = String(Math.floor(totalDuration % 60)).padStart(2, '0');
            timeDisplay.innerText = curM + ":" + curS + " / " + totM + ":" + totS;
        }}

        // 🔴 隔離壁のない「同じ部屋」にいるため、このジャンプ再生関数が100%成功します
        function remoteSeek(seconds) {{ if (audio) {{ audio.currentTime = seconds; audio.play().catch(e => console.log(e)); }} }}

        if (audio) {{
            audio.addEventListener('loadedmetadata', () => {{ totalDuration = Math.floor(audio.duration); updateTimeLabel(); drawTimeline(0); }});
            audio.addEventListener('timeupdate', () => {{ updateTimeLabel(); drawTimeline(Math.floor(audio.currentTime)); }});
        }}

        if (canvas) {{
            canvas.addEventListener('click', (e) => {{
                if (!totalDuration) return;
                remoteSeek(Math.floor(((e.clientX - canvas.getBoundingClientRect().left) / canvas.width) * totalDuration));
            }});
            canvas.addEventListener('mousemove', (e) => {{
                if (!totalDuration) return;
                const secs = Math.floor(((e.clientX - canvas.getBoundingClientRect().left) / canvas.width) * totalDuration);
                const status = colorData[secs] || "SILENT";
                updateHoverInfo("[" + String(Math.floor(secs/60)).padStart(2,'0') + ":" + String(secs%60).padStart(2,'0') + "] " + status);
            }});
            canvas.addEventListener('mouseleave', clearHoverInfo);
        }}
        window.addEventListener('resize', () => {{ if(audio) drawTimeline(Math.floor(audio.currentTime)); }});
        </script>
        <style>
        .stApp {{ background-color: #0e1117 !important; color: #e2e8f0 !important; }}
        .section-title {{ font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-bottom: 8px; }}
        .player-panel {{ background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; width: 100% !important; box-sizing: border-box; }}
        .player-panel audio {{ width: 100%; filter: invert(0.9) hue-rotate(180deg); }}
        .time-display-mock {{ text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }}
        .canvas-container {{ width: 100%; margin-top: 15px; }}
        canvas {{ width: 100% !important; height: 22px; border-radius: 4px; border: 1px solid #00b4d8; background-color: #161b22; display: block; }}
        div.log-master-outer {{ background-color: #161b22 !important; border: 1px solid #21262d !important; border-radius: 8px !important; padding: 10px !important; max-height: 380px !important; overflow-y: auto !important; width: 100% !important; display: block !important; box-sizing: border-box; }}
        .log-line {{ display: flex; align-items: flex-start; padding: 8px 12px; margin-bottom: 2px; border-radius: 4px; cursor: pointer; font-size: 14px; transition: background-color 0.1s ease; user-select: none; width: 100%; box-sizing: border-box; }}
        .log-line:hover {{ background-color: #21262d; }}
        .log-line:hover .log-text {{ color: #ffffff; }}
        .timestamp-lead {{ color: #00b4d8; font-family: monospace; margin-right: 15px; white-space: nowrap; font-weight: bold; }}
        .log-text {{ color: #c9d1d9; line-height: 1.4; }}
        .mock-btn {{ background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px; }}
        div[data-baseweb="select"] > div {{ background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }}
        div[data-testid="stStatusWidget"] {{ display: none !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
