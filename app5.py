import os
import streamlit as st

st.set_page_config(layout="centered")

st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #00b4d8; font-family: sans-serif; letter-spacing: 1px;">奏録 / SOUROKU</h2>
    </div>
    """,
    unsafe_allow_html=True
)

STATIC_DIR = "static"

# 有効な音声フォルダを自動リサーチ
available_folders = []
if os.path.exists(STATIC_DIR):
    for folder in os.listdir(STATIC_DIR):
        folder_path = os.path.join(STATIC_DIR, folder)
        if os.path.isdir(folder_path):
            if "_" in folder:
                file_name = folder.split("_")[-1]
            else:
                file_name = folder
            m4a_path = os.path.join(folder_path, f"{file_name}.m4a")
            if os.path.exists(m4a_path):
                available_folders.append(folder)

if available_folders:
    available_folders.sort()
    
    st.markdown('<p class="section-title">Select session</p>', unsafe_allow_html=True)
    selected_folder = st.selectbox(
        "再生する音声を選択してください", 
        options=available_folders,
        label_visibility="collapsed"
    )
    
    if "_" in selected_folder:
        selected_file_name = selected_folder.split("_")[-1]
    else:
        selected_file_name = selected_folder
        
    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{selected_file_name}.m4a")
    text_physical_path = os.path.join(STATIC_DIR, selected_folder, f"{selected_file_name}.txt")

    # 🔴 後着のJavaScriptから公式プレイヤーを特定できるように、外枠に明示的なID「target-audio-box」を付与します
    st.markdown('<div class="player-panel" id="target-audio-box">', unsafe_allow_html=True)
    st.audio(physical_path, format="audio/mp4")
    st.markdown('<div class="time-display-mock">00:00 / 12:12</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # カラフルなインジケーター（ダミー）
    st.markdown(
        """
        <div class="color-bar">
            <div style="flex: 2; background: #00b4d8;"></div>
            <div style="flex: 1; background: #ff4b4b;"></div>
            <div style="flex: 3; background: #00b4d8;"></div>
            <div style="flex: 1; background: #ff4b4b;"></div>
            <div style="flex: 1; background: #00b4d8;"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 25px; margin-bottom: 15px;">
            <span class="section-title" style="margin:0;">Session Logs</span>
            <div>
                <button class="mock-btn">設定</button>
                <button class="mock-btn" style="background:#00b4d8; color:#0e1117; border:none;">編集</button>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    log_html_content = ""
    
    if os.path.exists(text_physical_path):
        try:
            with open(text_physical_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith("[") and "]" in line:
                    parts = line.split("]", 1)
                    timestamp_str = parts[0].replace("[", "").strip()
                    text = parts[1].strip()
                    
                    try:
                        time_parts = timestamp_str.split(":")
                        if len(time_parts) == 2:
                            seconds = int(time_parts[0]) * 60 + int(time_parts[1])
                        elif len(time_parts) == 3:
                            seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
                        else:
                            seconds = 0
                    except ValueError:
                        seconds = 0
                    
                    # 🔴【変更点1】行全体のDIVタグに「onclick="remoteSeek({seconds})"」を付与
                    # これにより、時間だけでなく横のテキスト部分を含めた「全域」がクリック可能になります
                    log_html_content += (
                        f'<div class="log-row-clickable" onclick="remoteSeek({seconds})">'
                        f'<span class="timestamp">[{timestamp_str}]</span>'
                        f'<span class="log-text-content">{text}</span>'
                        f'</div>\n'
                    )
                else:
                    log_html_content += f'<div class="log-line-normal">{line}</div>\n'
        except Exception as e:
            log_html_content = '<div class="log-line-normal" style="color: #ff4b4b;">ログの読み込みに失敗しました</div>'
    else:
        log_html_content = '<div class="log-line-normal" style="color: #8b949e;">ログファイルが見つかりません</div>'

    # 🔴【変更点2】HTMLコンポーネント（components.html）を画面上に直接配置するのではなく、
    # ログコンテナの下部に「見えないスクリプト（制御室）」として埋め込み、CORSをバイパスして親のプレイヤーを直接操作します
    st.markdown(
        f"""
        <div class="log-container">
            {log_html_content}
        </div>

        <script>
        // 行全体をクリックしたときに、親画面の公式プレイヤーを探して直接命令を送り込む関数
        function remoteSeek(seconds) {{
            // 画面内からStreamlitが自動生成した、非公開のaudio要素をルートID経由で捕捉します
            const audioNode = document.querySelector('#target-audio-box audio');
            if (audioNode) {{
                audioNode.currentTime = seconds; // 時間をセット
                
                // 🔴【重要】時間のセットと同時に、ブラウザに強制的に「play()」命令を投げます
                audioNode.play().catch(function(error) {{
                    console.log("ブラウザのポリシーにより自動再生が制限されました。一度画面をクリックしてください。", error);
                }});
            }} else {{
                console.error("再生対象のオーディオプレイヤーが見つかりません。");
            }}
        }}
        </script>
        """,
        unsafe_allow_html=True
    )

    # 配色のCSS設定
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-top: 15px; margin-bottom: 8px; }
        .player-panel { background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; }
        .player-panel audio { width: 100%; filter: invert(0.9) hue-rotate(180deg); }
        .time-display-mock { text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }
        .color-bar { display: flex; height: 15px; border-radius: 4px; overflow: hidden; margin-top: 10px; border: 1px solid #00b4d8; }
        
        /* ログ外枠 */
        .log-container { background-color: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 15px; max-height: 400px; overflow-y: auto; }
        .log-line-normal { font-size: 14px; color: #8b949e; margin-bottom: 16px; font-family: sans-serif; }
        
        /* 🔴【デザイン調整】クリック可能な行全体にホバー効果とポインタを適用 */
        .log-row-clickable {
            display: flex;
            align-items: flex-start;
            padding: 6px 8px;
            margin-bottom: 8px;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.15s ease;
            user-select: none;
        }
        
        /* 行全体にマウスを乗せたときに、少し明るい背景にする（画像のような直感的なUI） */
        .log-row-clickable:hover {
            background-color: #21262d;
        }
        .log-row-clickable:hover .log-text-content {
            color: #ffffff; /* ホバー時に文字を白く際立たせる */
        }
        
        .timestamp {
            color: #00b4d8;
            font-family: monospace;
            font-size: 14px;
            margin-right: 12px;
            white-space: nowrap;
        }
        .log-text-content {
            font-size: 14px;
            color: #c9d1d9;
            line-height: 1.5;
            font-family: sans-serif;
            transition: color 0.15s ease;
        }
        
        .mock-btn { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px; cursor: pointer; }
        div[data-baseweb="select"] > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
