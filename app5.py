import os
import streamlit as st
import streamlit.components.v1 as components

st.title("🎵 カスタムHTMLプレイヤー")

# テスト用の入力欄（例: "groupA" など）
folder_name = st.text_input("フォルダ名を入力してください", value="groupA")

if folder_name:
    # JavaScriptのセキュリティ制限を回避するため、
    # Python側で先に「正しいURLのパス」を計算して組み立てておきます
    if "_" in folder_name:
        file_name = folder_name.split("_")[-1]
    else:
        file_name = folder_name
        
    # 静的配信機能により、ブラウザからは "/static/..." でアクセス可能になります
    audio_url = f"/static/{folder_name}/{file_name}.m4a"

    # HTMLファイルを読み込む
    with open("player.html", "r", encoding="utf-8") as f:
        html_code = f.read()

    # --- 重要: HTMLにデータを渡す仕組み ---
    # HTML内の専用スクリプト（Render用）へ、安全に音声URLを引き渡します
    components.html(
        html_code + f"""
        <script>
            // Streamlitからデータを受け取るための関数をセット
            function onStreamlitMessage(event) {{
                if (event.data.type === 'streamlit:render') {{
                    // app.py から渡されたデータを直接受け取ることはできないため
                    // 今回はURLをあらかじめ埋め込むか、以下の標準的な通信を行います
                }}
            }}
            // シンプルに動かすため、HTML側の変数に直接URLを流し込みます
            window.audioUrlFromPython = "{audio_url}";
            if (typeof initPlayer === "function") {{
                initPlayer();
            }}
        </script>
        """,
        height=200, # HTMLの大きさに合わせて調整してください
    )
