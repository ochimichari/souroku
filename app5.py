import os
import streamlit as st

st.set_page_config(layout="centered")
st.markdown('<div style="text-align:center;margin-bottom:20px;"><h2 style="color:#00b4d8;font-family:sans-serif;letter-spacing:1px;">奏録 / SOUROKU</h2></div>', unsafe_allow_html=True)

STATIC_DIR = "static"
folders = sorted([f for f in os.listdir(STATIC_DIR) if os.path.isdir(os.path.join(STATIC_DIR, f))]) if os.path.exists(STATIC_DIR) else []
valid_folders = []

if folders:
    for f in folders:
        name = f.split("_")[-1] if "_" in f else f
        if os.path.exists(os.path.join(STATIC_DIR, f, f"{name}.m4a")) or os.path.exists(os.path.join(STATIC_DIR, f, f"{name}.M4A")):
            valid_folders.append(f)

if valid_folders:
    st.markdown('<p class="section-title">Select session</p>', unsafe_allow_html=True)
    sel = st.selectbox("選択", options=valid_folders, label_visibility="collapsed")
    f_name = sel.split("_")[-1] if "_" in sel else sel
    
    if "last" not in st.session_state or st.session_state.last != sel:
        st.session_state.last, st.session_state.seek, st.session_state.play = sel, 0, False

    audio_file = f"{f_name}.m4a" if os.path.exists(os.path.join(STATIC_DIR, sel, f"{f_name}.m4a")) else f"{f_name}.M4A"
    txt_p, col_p = os.path.join(STATIC_DIR, sel, f"{f_name}.txt"), os.path.join(STATIC_DIR, sel, f"{f_name}_color.txt")

    st.markdown('<div class="player-panel" id="audio-root">', unsafe_allow_html=True)
    st.audio(os.path.join(STATIC_DIR, sel, audio_file), format="audio/mp4", start_time=st.session_state.seek, autoplay=st.session_state.play)
    st.markdown('<div class="time-display-mock" id="time-view">00:00 / 00:00</div><div class="canvas-container"><canvas id="timeline-canvas" height="22"></canvas></div></div>', unsafe_allow_html=True)
    st.markdown('<div id="hover-info" style="height:20px;color:#8b949e;font-family:monospace;font-size:13px;text-align:center;margin-top:5px;">バーにマウスを乗せてください</div>', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;justify-content:space-between;align-items:center;margin-top:25px;margin-bottom:15px;"><span class="section-title" style="margin:0;">Session Logs</span><div><button class="mock-btn">設定</button><button class="mock-btn" style="background:#00b4d8;color:#0e1117;border:none;">編集</button></div></div>', unsafe_allow_html=True)

    log_html = ""
    if os.path.exists(txt_p):
        with open(txt_p, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if line.startswith("[") and "]" in line:
                    idx_close = line.find("]")
                    t_str, text = line[1:idx_close].strip(), line[idx_close+1:].strip()
                    p = t_str.split(":")
                    s = int(p)*60 + int(p) if len(p)==2 else int(p)*3600 + int(p)*60 + int(p) if len(p)==3 else 0
                    log_html += f'<div class="log-line" onclick="remoteSeek({s})"><span class="ts">[{t_str}]</span><span class="txt">{text}</span></div>\n'
    st.markdown(f'<div class="log-container">{log_html}</div>', unsafe_allow_html=True)

    color_lines, total_secs = [], 0
    if os.path.exists(col_p):
        with open(col_p, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip().startswith("[") and "]" in l]
            total_secs = len(lines)
            color_lines = "||".join(lines)

    st.markdown(f'<div id="hidden-color-data" style="display:none;" data-total="{total_secs}">{color_lines}</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <script>
        (function() {
            const audio = document.querySelector('#audio-root audio'), timeDisplay = document.getElementById('time-view'), canvas = document.getElementById('timeline-canvas'), hoverInfo = document.getElementById('hover-info'), dataEl = document.getElementById('hidden-color-data');
            if (!dataEl || !canvas || !audio) return;
            
            const totalDuration = parseInt(dataEl.getAttribute('data-total'), 10) || 0, rawText = dataEl.textContent || "";
            let colorData = {};

            if (rawText) {
                rawText.split('||').forEach((piece, idx) => {
                    const idxClose = piece.indexOf(']');
                    if (idxClose !== -1) colorData[idx] = piece.substring(idxClose + 1).trim().toUpperCase();
                });
            }

            window.drawTimeline = function(currentSec = 0) {
                if (!totalDuration) return;
                if (canvas.width !== canvas.clientWidth) canvas.width = canvas.clientWidth;
                const ctx = canvas.getContext('2d'), secWidth = canvas.width / totalDuration;
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                for (let s = 0; s < totalDuration; s++) {
                    const status = colorData[s] || "SILENT";
                    ctx.fillStyle = status === "SPEECH" ? "#ff4b4b" : status === "MUSIC" ? "#00b4d8" : "#2a3247";
                    ctx.fillRect(s * secWidth, 0, secWidth + 0.6, canvas.height);
                }
                ctx.fillStyle = "#ffffff";
                ctx.fillRect((currentSec / totalDuration) * canvas.width - 1, 0, 2, canvas.height);
            };

            function updateTimeLabel() {
                const curM = String(Math.floor(audio.currentTime / 60)).padStart(2, '0'), curS = String(Math.floor(audio.currentTime % 60)).padStart(2, '0');
                const totM = String(Math.floor(totalDuration / 60)).padStart(2, '0'), totS = String(Math.floor(totalDuration % 60)).padStart(2, '0');
                timeDisplay.innerText = curM + ":" + curS + " / " + totM + ":" + totS;
            }

            window.remoteSeek = function(seconds) {
                const btns = document.querySelectorAll('div[data-testid="stButton"] button');
                for (let btn of btns) {
                    if (btn.innerText.includes("[" + String(Math.floor(seconds/60)).padStart(2,'0') + ":")) { btn.click(); break; }
                }
            };

            audio.addEventListener('loadedmetadata', () => { updateTimeLabel(); drawTimeline(0); });
            audio.addEventListener('timeupdate', () => { updateTimeLabel(); drawTimeline(Math.floor(audio.currentTime)); });

            canvas.addEventListener('mousemove', (e) => {
                if (!totalDuration) return;
                const secs = Math.floor(((e.clientX - canvas.getBoundingClientRect().left) / canvas.width) * totalDuration);
                const m = String(Math.floor(secs / 60)).padStart(2, '0'), s = String(Math.floor(secs % 60)).padStart(2, '0');
                if (hoverInfo) hoverInfo.innerText = "[" + m + ":" + s + "] " + (colorData[secs] || "SILENT");
            });
            canvas.addEventListener('mouseleave', () => { if (hoverInfo) hoverInfo.innerText = 'バーにマウスを乗せてください'; });
            window.addEventListener('resize', () => { drawTimeline(Math.floor(audio.currentTime)); });
            setTimeout(() => { drawTimeline(0); }, 100);
        })();
        </script>
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-bottom: 8px; }
        .player-panel { background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; width: 100% !important; box-sizing: border-box; }
        .player-panel audio { width: 100%; filter: invert(0.9) hue-rotate(180deg); }
        .time-display-mock { text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }
        .canvas-container { width: 100%; margin-top: 15px; }
        canvas { width: 100% !important; height: 22px; border-radius: 4px; border: 1px solid #00b4d8; background-color: #161b22; display: block; }
        div.log-container { background-color: #161b22 !important; border: 1px solid #21262d !important; border-radius: 8px !important; padding: 10px !important; max-height: 380px !important; overflow-y: auto; width: 100% !important; box-sizing: border-box; }
        div[data-testid="element-container"]:has(div[data-testid="stButton"]) { width: 100% !important; max-width: 100% !important; margin-bottom: 0px !important; }
        div[data-testid="stButton"] { width: 100% !important; margin-bottom: 2px !important; }
        div[data-testid="stButton"] button { width: 100% !important; background: transparent !important; border: none !important; color: #c9d1d9 !important; text-align: left !important; padding: 8px 12px !important; font-size: 14px !important; border-radius: 4px !important; justify-content: flex-start !important; }
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
