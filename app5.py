import os
import streamlit as st

# ページ設定
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
    
    # セレクトボックス部分
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
        
    # 🔴 クラウザ上で100%読み込み拒否されない、正しい静的ルート相対URLパス
    audio_url = f"/static/{selected_folder}/{selected_file_name}.m4a"
    text_physical_path = os.path.join(STATIC_DIR, selected_folder, f"{selected_file_name}.txt")

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

    # ログセクションヘッダー
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

    # テキストファイル（.txt）を読み込んでHTMLを組み立てる処理
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
                    timestamp_str = parts[0].replace("[", "").strip() # 例: "00:25"
                    text = parts[1].strip()     
                    
                    # 「分:秒」を秒数に変換
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
                    
                    log_html_content += (
                        f'<div class="log-line">'
                        f'<span class="timestamp-btn" onclick="seekToAudio({seconds})">[{timestamp_str}]</span>'
                        f' {text}'
                        f'</div>\n'
                    )
                else:
                    log_html_content += f'<div class="log-line">{line}</div>\n'
        except Exception as e:
            log_html_content = f'<div class="log-line" style="color: #ff4b4b;">ファイルの読み込みエラー</div>'
    else:
        log_html_content = f'<div class="log-line" style="color: #8b949e; font-style: italic;">ログファイルが見つかりません</div>'

    # 🔴【最大の変更点】
    # 隔離された st.audio を使わず、1つの大きなHTMLブロックの中に「プレイヤー」と「ログリスト」と「制御JavaScript」を完全に同居させます。
    # これにより、同一空間内の通信となり、タイムスタンプクリックによるジャンプが100%阻害されずに動作します。
    integrated_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ margin: 0; padding: 0; background-color: transparent; font-family: sans-serif; }}
            
            /* プレイヤー外枠パネルのデザイン（画像準拠） */
            .player-panel {{
                background-color: #161b22;
                border: 1px solid #00b4d8;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                box-sizing: border-box;
            }}
            .player-panel audio {{
                width: 100%;
                filter: invert(0.9) hue-rotate(180deg); /* プレイヤーのダーク水色化 */
            }}
            .time-display-mock {{
                text-align: right;
                color: #00b4d8;
                font-family: monospace;
                font-size: 14px;
                margin-top: 5px;
            }}

            /* ログコンテナのデザイン */
            .log-container {{
                background-color: #161b22;
                border: 1px solid #21262d;
                border-radius: 8px;
                padding: 15px;
                max-height: 400px;
                overflow-y: auto;
                box-sizing: border-box;
            }}
            .log-line {{
                font-size: 14px;
                color: #c9d1d9;
                margin-bottom: 16px;
                line-height: 1.5;
            }}
            .timestamp-btn {{
                color: #00b4d8;
                font-family: monospace;
                margin-right: 8px;
                cursor: pointer;
                user-select: none;
                display: inline-block;
            }}
            .timestamp-btn:hover {{
                text-decoration: underline;
                color: #33c2df;
            }}
        </style>
    </head>
    <body>

        <!-- 同一のHTML内にプレイヤーを配置（/static/ からストリーミングされるため大容量でもパンクしません） -->
        <div class="player-panel">
            <audio id="custom-internal-audio" controls src="{audio_url}"></audio>
            <div class="time-display-mock" id="internal-time-display">00:00 / 00:00</div>
        </div>

        <!-- ログリスト -->
        <div class="log-container">
            {log_html_content}
        </div>

        <script>
            const audioEl = document.getElementById('custom-internal-audio');
            const timeDisplay = document.getElementById('internal-time-display');

            // 秒数を 00:00 形式にする関数
            function formatTime(seconds) {{
                if (isNaN(seconds)) return "00:00";
                const mins = Math.floor(seconds / 60);
                const secs = Math.floor(seconds % 60);
                return String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
            }}

            // プレイヤー右下の時間カウントを本物のデータとリアルタイム連動させる
            audioEl.addEventListener('loadedmetadata', () => {{
                timeDisplay.innerText = formatTime(audioEl.currentTime) + " / " + formatTime(audioEl.duration);
            }});
            audioEl.addEventListener('timeupdate', () => {{
                timeDisplay.innerText = formatTime(audioEl.currentTime) + " / " + formatTime(audioEl.duration);
            }});

            // 🔴 同じ部屋の中にあるので、このジャンプ処理が完全に成功します
            function seekToAudio(seconds) {{
                if (audioEl) {{
                    audioEl.currentTime = seconds;
                    audioEl.play().catch(e => console.log("再生開始がブロックされました", e));
                }}
            }}
        </script>
    </body>
    </html>
    """

    # Streamlitのコンポーネントとして一体化HTMLを流し込む（高さを十分に確保）
    import streamlit.components.v1 as components
    components.html(integrated_html, height=600)

    # 画面背景などのスタイル補正
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-top: 15px; margin-bottom: 8px; }
        .mock-btn { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px; cursor: pointer; }
        div[data-baseweb="select"] > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
