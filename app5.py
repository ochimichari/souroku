import os
import streamlit as st
import streamlit.components.v1 as components

st.title("🎵 カスタムHTMLプレイヤー (完全解決版)")

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
    selected_folder = st.selectbox("再生する音声を選択してください", options=available_folders)
    
    if "_" in selected_folder:
        selected_file_name = selected_folder.split("_")[-1]
    else:
        selected_file_name = selected_folder
        
    # 🔴 クラウド環境でも100%エラーにならない安全なパスURLを作ります
    # 頭にスラッシュを1つだけつけた「/static/...」は、ブラウザがドメインを自動補完してくれる最強の書き方です
    audio_url = f"/static/{selected_folder}/{selected_file_name}.m4a"

    st.caption(f"選択中: {selected_folder}/{selected_file_name}.m4a")

    # HTMLにデザインとJavaScriptを埋め込みます
    html_code = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ margin: 0; padding: 0; background: transparent; font-family: sans-serif; }}
            /* 🔴 ここであなたの好きなデザイン（CSS）を無限にいじることができます */
            .player-panel {{ background: #f0f2f6; padding: 15px; border-radius: 10px; box-sizing: border-box; }}
            .time-display {{ font-family: monospace; margin-top: 5px; color: #31333f; font-size: 14px; }}
            audio {{ width: 100%; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="player-panel">
            <div style="font-weight: bold; color: #31333f; font-size: 14px;">再生中: {selected_file_name}.m4a</div>
            <audio id="audio" controls src="{audio_url}"></audio>
            <div class="time-display" id="time-display">00:00 / 00:00</div>
        </div>

        <script>
            const audio = document.getElementById('audio');
            const timeDisplay = document.getElementById('time-display');

            // 🔴 タイムカウンターを動かすJavaScript
            function formatTime(seconds) {{
                if (isNaN(seconds)) return "00:00";
                const mins = Math.floor(seconds / 60);
                const secs = Math.floor(seconds % 60);
                return String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
            }}

            audio.addEventListener('loadedmetadata', () => {{
                timeDisplay.innerText = formatTime(audio.currentTime) + " / " + formatTime(audio.duration);
            }});

            audio.addEventListener('timeupdate', () => {{
                timeDisplay.innerText = formatTime(audio.currentTime) + " / " + formatTime(audio.duration);
            }});

            // 🔴【重要】クラウド上の「ぐるぐるフリーズ（読み込み遅延）」を強制解除する処理
            // Streamlitの静的配信は起動直後に一瞬遅れることがあるため、失敗したら0.5秒後に自動リロードさせます
            audio.addEventListener('error', () => {{
                console.log("音声の読み込みに失敗しました。再試行します...");
                setTimeout(() => {{
                    audio.load();
                }}, 500);
            }});
        </script>
    </body>
    </html>
    """

    # 🔴 key引数を完全に排除。これで最新Streamlit環境の内部バグ（TypeError）を完全に回避します
    components.html(
        html_code,
        height=160
    )

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
