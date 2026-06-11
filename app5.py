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
    selected_folder = st.selectbox("選択", options=available_folders, label_visibility="collapsed")
    
    file_name = selected_folder.split("_")[-1] if "_" in selected_folder else selected_folder
    
    if "last_folder" not in st.session_state or st.session_state.last_folder != selected_folder:
        st.session_state.last_folder = selected_folder
        st.session_state.seek_seconds = 0
        st.session_state.auto_play = False

    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.m4a")
    txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.txt")
    color_txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}_color.txt")

    # 音声プレイヤー（ID「audio-root」を付与してJavaScriptから見つけやすくします）
    st.markdown('<div class="player-panel" id="audio-root">', unsafe_allow_html=True)
    st.audio(physical_path, format="audio/mp4", start_time=st.session_state.seek_seconds, autoplay=st.session_state.auto_play)
    st.markdown('<div class="time-display-mock" id="time-view">00:00 / 00:00</div>', unsafe_allow_html=True)
    
    # 🔴【新規実装】ここにCanvasの器を配置します（外枠のサイズに合わせて横幅100%で広がります）
    st.markdown('<div class="canvas-container"><canvas id="timeline-canvas" height="22"></canvas></div></div>', unsafe_allow_html=True)

    # ホバーテキストエリア
    st.markdown('<div id="hover-info" style="height: 20px; color: #8b949e; font-family: monospace; font-size: 13px; text-align: center; margin-top: 5px;">バーにマウスを乗せてください</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 25px; margin-bottom: 15px;"><span class="section-title" style="margin:0;">Session Logs</span><div><button class="mock-btn">設定</button><button class="mock-btn" style="background:#00b4d8; color:#0e1117; border:none;">編集</button></div></div>', unsafe_allow_html=True)

    # 🔴【一切いじらないログの表示構造】
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

    # 🔴【Canvas用の色分け生データ準備】
    # JavaScript側でインデックスバグを引き起こさないよう、Python側で先に秒数を安全に計算して渡します
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
                        if len(p) == 2: s = int(p[0]) * 60 + int(p[1])
                        elif len(p) == 3: s = int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])
                        else: s = 0
                        color_array_js.append(f"'{s}={status}'")
                    except:
                        continue
    js_str = "[" + ",".join(color_array_js) + "]"
    # 🔴【新規実装】Canvasへの描画・時間更新・ホバー追従を行うJavaScriptとCSS
    st.markdown(
        f"""
        <script>
        const audio = document.querySelector('#audio-root audio');
        const timeDisplay = document.getElementById('time-view');
        const canvas = document.getElementById('timeline-canvas');
        const hoverInfo = document.getElementById('hover-info');
        let colorData = {{}}, totalDuration = 0;

        // Python側で計算済みの秒数データ配列を、JavaScriptの辞書形式（colorData）に展開
        ({js_str}).forEach(item => {{
            const parts = item.split('=');
            if (parts.length === 2) colorData[parseInt(parts[0], 10)] = parts[1];
        }});

        // 🔴 ご提示いただいたCanvasタイムライン描画（drawTimeline）を完全統合
        function drawTimeline(currentSec = 0) {{
            if (!totalDuration) return;
            // 画面の幅（レスポンシブ）に合わせてCanvasの横幅を引き伸ばす
            if (canvas.width !== canvas.clientWidth) canvas.width = canvas.clientWidth;
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const secWidth = canvas.width / totalDuration;
            
            // 1秒ごとのデータを赤（SPEECH）と青（MUSIC）に1ピクセル単位で正確に色分け
            for (let s = 0; s < totalDuration; s++) {{
                const status = colorData[s] || "SILENT";
                ctx.fillStyle = status === "SPEECH" ? "#ff4b4b" : status === "MUSIC" ? "#00b4d8" : "#2a3247";
                ctx.fillRect(s * secWidth, 0, secWidth + 0.6, canvas.height);
            }}
            // 再生中のホワイトインジケーター（縦線）を描画
            ctx.fillStyle = "#ffffff";
            ctx.fillRect((currentSec / totalDuration) * canvas.width - 1, 0, 2, canvas.height);
        }}

        // 🔴 ご提示いただいた時間ラベル更新（updateTimeLabel）を完全統合
        function updateTimeLabel() {{
            if (!audio) return;
            const curM = String(Math.floor(audio.currentTime / 60)).padStart(2, '0'), curS = String(Math.floor(audio.currentTime % 60)).padStart(2, '0');
            const totM = String(Math.floor(totalDuration / 60)).padStart(2, '0'), totS = String(Math.floor(totalDuration % 60)).padStart(2, '0');
            timeDisplay.innerText = curM + ":" + curS + " / " + totM + ":" + totS;
        }}

        // 音声プレイヤーのデータ読み込み完了イベント連動
        if (audio) {{
            audio.addEventListener('loadedmetadata', () => {{ totalDuration = Math.floor(audio.duration); updateTimeLabel(); drawTimeline(0); }});
            // 🔴 プレイヤー再生中に1秒単位で時間とCanvasの位置を同期
            audio.addEventListener('timeupdate', () => {{ updateTimeLabel(); drawTimeline(Math.floor(audio.currentTime)); }});
        }}

        // 🔴 ご提示いただいたCanvasクリックによる指定秒数への直接シーク（ジャンプ）
        if (canvas) {{
            canvas.addEventListener('click', (e) => {{
                if (!totalDuration) return;
                const clickSec = Math.floor(((e.clientX - canvas.getBoundingClientRect().left) / canvas.width) * totalDuration);
                if (audio) {{
                    audio.currentTime = clickSec;
                    audio.play().catch(err => console.log(err));
                }}
            }});
            
            // 🔴 マウスホバー追従テキスト処理
            canvas.addEventListener('mousemove', (e) => {{
                if (!totalDuration) return;
                const secs = Math.floor(((e.clientX - canvas.getBoundingClientRect().left) / canvas.width) * totalDuration);
                const status = colorData[secs] || "SILENT";
                if (hoverInfo) {{
                    hoverInfo.innerText = "[" + String(Math.floor(secs/60)).padStart(2,'0') + ":" + String(secs%60).padStart(2,'0') + "] " + status;
                    hoverInfo.style.color = status === "SPEECH" ? "#ff4b4b" : status === "MUSIC" ? "#00b4d8" : "#8b949e";
                }}
            }});
            canvas.addEventListener('mouseleave', () => {{ if (hoverInfo) {{ hoverInfo.innerText = 'バーにマウスを乗せてください'; hoverInfo.style.color = '#8b949e'; }} }});
        }}
        window.addEventListener('resize', () => {{ if(audio) drawTimeline(Math.floor(audio.currentTime)); }});
        </script>
        <style>
        .stApp {{ background-color: #0e1117 !important; color: #e2e8f0 !important; }}
        .section-title {{ font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-bottom: 8px; }}
        .player-panel {{ background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; width: 100% !important; box-sizing: border-box; }}
        .player-panel audio {{ width: 100%; filter: invert(0.9) hue-rotate(180deg); }}
        .time-display-mock {{ text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }}
        
        /* 🔴 Canvasタイムライン用のスタイル */
        .canvas-container {{ width: 100%; margin-top: 15px; }}
        canvas {{ width: 100% !important; height: 22px; border-radius: 4px; border: 1px solid #00b4d8; background-color: #161b22; display: block; }}
        
        /* 🔴 以前大成功していたログの幅100%維持CSSを完全に死守 */
        div.log-container {{ background-color: #161b22 !important; border: 1px solid #21262d !important; border-radius: 8px !important; padding: 10px !important; max-height: 380px !important; overflow-y: auto; }}
        div[data-testid="element-container"]:has(div[data-testid="stButton"]) {{ width: 100% !important; max-width: 100% !important; margin-bottom: 0px !important; }}
        div[data-testid="stButton"] {{ width: 100% !important; margin-bottom: 2px !important; }}
        div[data-testid="stButton"] button {{
            width: 100% !important; background: transparent !important; border: none !important;
            color: #c9d1d9 !important; text-align: left !important; padding: 8px 12px !important;
            font-size: 14px !important; border-radius: 4px !important; justify-content: flex-start !important;
        }
        div[data-testid="stButton"] button:hover { background-color: #21262d !important; color: #ffffff !important; }
        div[data-testid="stButton"] button::first-line { color: #00b4d8 !important; font-family: monospace !important; }
        
        .mock-btn {{ background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px; }}
        div[data-baseweb="select"] > div {{ background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }}
        div[data-testid="stStatusWidget"] {{ display: none !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
