import os
import streamlit as st

st.set_page_config(layout="centered")

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
    st.markdown('<div style="text-align: center; margin-bottom: 20px;"><h2 style="color: #00b4d8; font-family: sans-serif; letter-spacing: 1px;">奏録 / SOUROKU</h2></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Select session</p>', unsafe_allow_html=True)
    
    selected_folder = st.selectbox("再生する音声を選択してください", options=available_folders, label_visibility="collapsed")
    
    file_name = selected_folder.split("_")[-1] if "_" in selected_folder else selected_folder
    
    # クラウドサーバー上の本物の静的相対URLを確定（/static/...）
    audio_url = f"/static/{selected_folder}/{file_name}.m4a"
    txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.txt")
    color_txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}_color.txt")

    # ログテキスト（文字起こし）を生データとして読み込み
    raw_txt_content = ""
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            raw_txt_content = f.read()

    # カラーバーデータ（SPEECH/MUSIC）を生データとして読み込み
    raw_color_content = ""
    if os.path.exists(color_txt_path):
        with open(color_txt_path, "r", encoding="utf-8") as f:
            raw_color_content = f.read()

    # 🔴【フロントエンド一体型構造】
    # ご提示いただいたJavaScriptの高度なコア機能をそっくりそのままHTML/CanvasUIへ移植
    # 変数のバッティングを防ぐため、PythonからJavaScriptへテキストデータを直接安全に流し込みます
    import streamlit.components.v1 as components

    # Python側で読み込んだ生データをJavaScriptの文字列変数へ直接埋め込みます
    integrated_frontend_html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ background-color: #0e1117; color: #e2e8f0; font-family: sans-serif; margin: 0; padding: 0; overflow: hidden; }}
            .player-panel {{ background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-bottom: 10px; box-sizing: border-box; }}
            audio {{ width: 100%; filter: invert(0.9) hue-rotate(180deg); margin-bottom: 5px; }}
            .time-display {{ text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }}
            .canvas-container {{ width: 100%; margin-top: 15px; position: relative; }}
            canvas {{ width: 100%; height: 22px; border-radius: 4px; border: 1px solid #00b4d8; background-color: #161b22; cursor: pointer; display: block; }}
            .header-row {{ display: flex; justify-content: space-between; align-items: center; margin-top: 20px; margin-bottom: 12px; }}
            .section-title-internal {{ font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; }}
            .log-container {{ background-color: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 10px; height: 320px; overflow-y: auto; box-sizing: border-box; }}
            .log-line {{ display: flex; align-items: flex-start; padding: 8px 12px; margin-bottom: 2px; border-radius: 4px; cursor: pointer; font-size: 14px; transition: background-color 0.1s ease; user-select: none; }}
            .log-line:hover {{ background-color: #21262d; }}
            .log-line:hover .log-text {{ color: #ffffff; }}
            .timestamp-lead {{ color: #00b4d8; font-family: monospace; margin-right: 15px; white-space: nowrap; font-weight: bold; }}
            .log-text {{ color: #c9d1d9; line-height: 1.4; transition: color 0.1s; }}
            .mock-btn {{ background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px; }}
        </style>
    </head>
    <body>
        <div class="player-panel">
            <audio id="main-audio" controls src="{audio_url}"></audio>
            <div class="time-display" id="time-view">00:00 / 00:00</div>
            <div class="canvas-container"><canvas id="timeline-canvas" height="22"></canvas></div>
        </div>
        <div class="header-row">
            <span class="section-title-internal">Session Logs</span>
            <div>
                <button class="mock-btn">設定</button>
                <button class="mock-btn" style="background:#00b4d8; color:#0e1117; border:none;">編集</button>
            </div>
        </div>
        <div class="log-container" id="editor-log-view"></div>

        <script>
            const audio = document.getElementById('main-audio');
            const timeDisplay = document.getElementById('time-view');
            const canvas = document.getElementById('timeline-canvas');
            const ctx = canvas.getContext('2d');
            const editor = document.getElementById('editor-log-view');

            const rawColorText = `{raw_color_content.replace('`', '\\`').replace('$', '\\$')}`;
            const rawLogText = `{raw_txt_content.replace('`', '\\`').replace('$', '\\$')}`;
            let colorData = {};
            let totalDuration = 0;

            function parseColor(raw) {{
                const lines = raw.split('\\n');
                lines.forEach(line => {{
                    const trimmed = line.trim();
                    if (!trimmed || !trimmed.includes(' ')) return;
                    const parts = trimmed.split(' ');
                    const tStr = parts[0];
                    const status = parts[1];
                    try {{
                        const [m, s] = tStr.replace('[', '').replace(']', '').split(':').map(Number);
                        colorData[m * 60 + s] = status.trim();
                    }} catch(e) {{}}
                }});
            }}
            function parseText(raw) {{
                editor.innerHTML = '';
                const lines = raw.split('\\n');
                lines.forEach((line) => {{
                    const trimmed = line.trim();
                    if (!trimmed) return;
                    let seconds = -1;
                    let displayTime = "[00:00]";
                    let displayText = trimmed;
                    if (trimmed.startsWith('[') && trimmed.includes(']')) {{
                        try {{
                            const parts = trimmed.split(']');
                            displayTime = parts[0] + ']';
                            displayText = parts[1].trim();
                            const tStr = parts[0].replace('[', '');
                            const timeParts = tStr.split(':').map(Number);
                            if (timeParts.length === 2) seconds = timeParts[0] * 60 + timeParts[1];
                            else if (timeParts.length === 3) seconds = timeParts[0] * 3600 + timeParts[1] * 60 + timeParts[2];
                        }} catch(e) {{}}
                    }}
                    const rowDiv = document.createElement('div');
                    rowDiv.className = 'log-line';
                    rowDiv.innerHTML = `<span class="timestamp-lead">${{displayTime}}</span><span class="log-text">${{displayText}}</span>`;
                    rowDiv.addEventListener('click', () => {{
                        if (seconds !== -1) {{ audio.currentTime = seconds; audio.play().catch(e => console.log(e)); }}
                    }});
                    editor.appendChild(rowDiv);
                }});
            }}

            function drawTimeline(currentSec = 0) {{
                if (!totalDuration) return;
                if (canvas.width !== canvas.clientWidth) canvas.width = canvas.clientWidth;
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                const secWidth = canvas.width / totalDuration;
                for (let s = 0; s < totalDuration; s++) {{
                    const x0 = s * secWidth;
                    const status = colorData[s] || "SILENT";
                    if (status === "SPEECH") ctx.fillStyle = "#ff4b4b";
                    else if (status === "MUSIC") ctx.fillStyle = "#00b4d8";
                    else ctx.fillStyle = "#2a3247";
                    ctx.fillRect(x0, 0, secWidth + 0.6, canvas.height);
                }}
                const indX = (currentSec / totalDuration) * canvas.width;
                ctx.fillStyle = "#ffffff";
                ctx.fillRect(indX - 1, 0, 2, canvas.height);
            }}

            function updateTimeLabel() {{
                const curM = String(Math.floor(audio.currentTime / 60)).padStart(2, '0');
                const curS = String(Math.floor(audio.currentTime % 60)).padStart(2, '0');
                const totM = String(Math.floor(totalDuration / 60)).padStart(2, '0');
                const totS = String(Math.floor(totalDuration % 60)).padStart(2, '0');
                timeDisplay.innerText = `${{curM}}:${{curS}} / ${{totM}}:${{totS}}`;
            }}

            audio.addEventListener('loadedmetadata', () => {{
                totalDuration = Math.floor(audio.duration);
                updateTimeLabel();
                drawTimeline(0);
            }});

            audio.addEventListener('timeupdate', () => {
                const currentSeconds = Math.floor(audio.currentTime);
                updateTimeLabel();
                drawTimeline(currentSeconds);
            });

            canvas.addEventListener('click', (e) => {
                if (!totalDuration) return;
                const rect = canvas.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                const targetSec = Math.floor((clickX / canvas.width) * totalDuration);
                audio.currentTime = targetSec;
                audio.play().catch(err => console.log(err));
            });

            window.addEventListener('resize', () => {
                drawTimeline(Math.floor(audio.currentTime));
            });

            parseColor(rawColorText);
            parseText(rawLogText);
        </script>
    </body>
    </html>
    """

    components.html(integrated_frontend_html, height=580)

    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-bottom: 8px; }
        div[data-baseweb="select"] > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }
        div[data-testid="stStatusWidget"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
