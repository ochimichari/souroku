import os
import streamlit as st

st.set_page_config(layout="centered")
st.markdown('<div style="text-align: center; margin-bottom: 20px;"><h2 style="color: #00b4d8; font-family: sans-serif; letter-spacing: 1px;">奏録 / SOUROKU</h2></div>', unsafe_allow_html=True)

STATIC_DIR = "static"
available_folders = []

# 音声が実在するフォルダだけを厳選
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

    # 1. 🔴 カラーバーを安全に組み立て（ここではボタンは配置しません）
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
                        else: secs = idx
                    except: secs = idx

                    color_code = "#ff4b4b" if "SPEECH" in status else "#00b4d8" if "MUSIC" in status else "#30363d"
                    
                    # 🔴 バーをクリックしたとき、同じ秒数（secs）を持つ「ログセクションのボタン」を探してリモートクリックさせる仕様に変更
                    colorbar_inner_html += f'<div class="bar-tick" style="background: {color_code};" onclick="triggerLogClick({secs});" onmouseover="updateHoverInfo(\'[{time_str}] {status}\')" onmouseout="clearHoverInfo()"></div>'

    # ホバーテキストエリア
    st.markdown('<div id="colorbar-hover-info" style="height: 20px; color: #8b949e; font-family: monospace; font-size: 13px; text-align: center; margin-top: 5px;">バーにマウスを乗せてください</div>', unsafe_allow_html=True)

    if colorbar_inner_html:
        st.markdown(f'<div class="color-bar-container">{colorbar_inner_html}</div>', unsafe_allow_html=True)

    st.markdown('<div class="color-bar" style="margin-top:0px;"><div style="flex: 2; background: #00b4d8;"></div><div style="flex: 1; background: #ff4b4b;"></div><div style="flex: 3; background: #00b4d8;"></div><div style="flex: 1; background: #ff4b4b;"></div><div style="flex: 1; background: #00b4d8;"></div></div>', unsafe_allow_html=True)

    # ログヘッダー
    st.markdown('<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 25px; margin-bottom: 15px;"><span class="section-title" style="margin:0;">Session Logs</span><div><button class="mock-btn">設定</button><button class="mock-btn" style="background:#00b4d8; color:#0e1117; border:none;">編集</button></div></div>', unsafe_allow_html=True)

    # 2. 🔴 ログリストを表示（外枠のDIVタグを st.markdown で挟まず、CSSで直接スクロール枠に変形します）
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
                    
                    # 🔴 ログボタンを生成。HTMLに閉じ込めないため、100%確実に画面に復活します
                    # あとでカラーバーから見つけられるように、data-sec属性に秒数を記録しておきます
                    if st.button(f"[{time_str}]  {text_content}", key=f"row_{secs}_{idx}"):
                        st.session_state.seek_seconds = secs
                        st.session_state.auto_play = True
                        st.rerun()

    # 3. 🔴 ホバー表示＆カラーバーからログボタンを連動キックする安全なJavaScript
    st.markdown(
        """
        <script>
        function updateHoverInfo(t){var e=document.getElementById("colorbar-hover-info");e&&(e.innerText=t,e.style.color="#00b4d8")}
        function clearHoverInfo(){var t=document.getElementById("colorbar-hover-info");t&&(t.innerText="バーにマウスを乗せてください",t.style.color="#8b949e")}
        
        // 🔴 バーをクリックしたときに、対応するログの st.button を探し出して強制クリックする関数
        function triggerLogClick(targetSec) {
            // 画面内にあるすべての st.button を巡回
            const btns = document.querySelectorAll('div[data-testid="stButton"] button');
            for (let btn of btns) {
                // ボタン内のテキスト（例: "[00:14]  MUSIC"）から、クリック箇所を推測してマッチングさせます
                if (btn.innerText.includes('[')) {
                    const timeParts = btn.innerText.split(']')[0].replace('[', '').trim().split(':');
                    let btnSec = 0;
                    if (timeParts.length === 2) btnSec = parseInt(timeParts[0], 10) * 60 + parseInt(timeParts[1], 10);
                    else if (timeParts.length === 3) btnSec = parseInt(timeParts[0], 10) * 3600 + parseInt(timeParts[1], 10) * 60 + parseInt(timeParts[2], 10);
                    
                    // 秒数が完全に一致したら、そのログボタンを身代わりにクリックしてリランを起動
                    if (btnSec === targetSec) {
                        btn.click();
                        break;
                    }
                }
            }
        }
        </script>
        """,
        unsafe_allow_html=True
    )

    # 4. 🔴 画面を崩さず、ボタンを画像のような美しいスクロールコンテナに仕立て上げる完成版CSS
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
        .bar-tick:hover { opacity: 0.4; background-color: #ffffff !important; }
        .color-bar { display: flex; height: 15px; border-radius: 4px; overflow: hidden; border: 1px solid #00b4d8; margin-bottom: 15px; }

        /* 🔴【大復活】並べた st.button たちを強制的に1つのスクロール枠（Log Container）の中に閉じ込める画期的なCSSハック */
        .stMainBlock > div:nth-last-child(2), 
        div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stButton"]) {
            background-color: #161b22 !important;
            border: 1px solid #21262d !important;
            border-radius: 8px !important;
            padding: 10px !important;
            max-height: 380px !important;
            overflow-y: auto !important;
        }
        
        /* ボタンを行全体のフラットなデザインに整形 */
        div[data-testid="stButton"] { width: 100% !important; margin-bottom: 0px !important; }
        div[data-testid="stButton"] button {
            width: 100% !important; background: transparent !important; border: none !important;
            color: #c9d1d9 !important; text-align: left !important; padding: 6px 12px !important;
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
