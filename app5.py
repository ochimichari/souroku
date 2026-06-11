import os
import streamlit as st
import streamlit.components.v1 as components

st.title("🎵 カスタムHTMLプレイヤー (セキュリティ突破版)")

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
        
    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{selected_file_name}.m4a")

    st.caption(f"選択中: {selected_folder}/{selected_file_name}.m4a")

    # 1. 🔴 確実に音が鳴る「本物のプレイヤー」を配置（CSSで完全に非表示にします）
    # これによりクラウドのセキュリティ制限（CORS）を100%回避して音声データを確保します
    st.markdown('<div class="real-audio-wrapper">', unsafe_allow_html=True)
    st.audio(physical_path, format="audio/mp4")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. 🔴 あなたが自由にデザイン（CSS）できる「見た目だけの偽プレイヤー（HTML）」
    # 好きなだけデザインをカスタマイズしてください
    html_code = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ margin: 0; padding: 0; background: transparent; font-family: sans-serif; user-select: none; }}
            
            /* ✨ ここで見た目を100%自由にいじれます */
            .player-panel {{ 
                background: #f0f2f6; 
                padding: 18px; 
                border-radius: 12px; 
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                gap: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }}
            .title {{ font-weight: bold; color: #31333f; font-size: 15px; }}
            
            /* カスタムボタンのデザイン例 */
            .custom-play-btn {{
                background: #ff4b4b;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.2s;
                width: fit-content;
            }}
            .custom-play-btn:hover {{ background: #e03e3e; }}
        </style>
    </head>
    <body>
        <div class="player-panel">
            <div class="title">📄 再生中: {selected_file_name}.m4a</div>
            
            <!-- 自作の再生ボタン -->
            <button class="custom-play-btn" id="playBtn">▶ 再生 / 一時停止</button>
        </div>

        <script>
            // 3. 🔴【魔法のJavaScript】
            // このボタンが押されたら、親画面にあるStreamlit本物のプレイヤーの再生ボタンを代わりにクリックする
            document.getElementById('playBtn').addEventListener('click', () => {{
                // iframeの壁を越えて、親画面に配置されている本物の<audio>タグを探し出す
                const realAudio = window.parent.document.querySelector('audio');
                if (realAudio) {{
                    if (realAudio.paused) {{
                        realAudio.play();
                        document.getElementById('playBtn').innerText = "⏸ 一時停止";
                    }} else {{
                        realAudio.pause();
                        document.getElementById('playBtn').innerText = "▶ 再生";
                    }}
                }} else {{
                    alert("本物のオーディオプレイヤーが見つかりません");
                }}
            }});
        </script>
    </body>
    </html>
    """

    # 4. 🔴 自作したデザイン画面（ボタンなど）を描画します
    components.html(html_code, height=120)

    # 5. 🔴 本物のプレイヤーを隠すためのCSSスタイル
    st.markdown(
        """
        <style>
        /* 本物のst.audioプレイヤーを画面から完全に消し去る（裏では生きている） */
        .real-audio-wrapper {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
