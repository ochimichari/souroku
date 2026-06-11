import os
import streamlit as st
import streamlit.components.v1 as components

st.title("🎵 カスタムHTMLプレイヤー")

# 1. 入力フォーム
folder_name = st.text_input("フォルダ名を入力してください", value="20260607_airs")

# 入力があり、かつ「_」が含まれている場合のみ動かす
if folder_name and "_" in folder_name:
    
    # ファイル名切り出しルール (20260607_airs -> airs)
    file_name = folder_name.split("_")[-1]
    
    # ブラウザがアクセスする用のURLパス
    audio_url = f"/static/{folder_name}/{file_name}.m4a"
    
    # クラウドサーバー上の実際の物理パス（存在確認用）
    # ※staticフォルダ内に音声がある前提です
    physical_path = os.path.join("static", folder_name, f"{file_name}.m4a")

    # サーバー上に本当にファイルがあるか確認
    if os.path.exists(physical_path):
        
        # HTMLファイルを読み込む（player.htmlに変更）
        with open("player.html", "r", encoding="utf-8") as f:
            html_code = f.read()

        # HTMLをブラウザにレンダリングし、同時にURLを安全に流し込む
        components.html(
            html_code + f"""
            <script>
                // 変数に安全に代入
                window.audioUrlFromPython = "{audio_url}";
                // プレイヤーの読み込み関数を実行
                if (typeof initPlayer === "function") {{
                    initPlayer();
                }}
            </script>
            """,
            height=200,
        )
    else:
        st.error(f"⚠️ サーバ上にファイルが見つかりません。配置を再確認してください:\n`{physical_path}`")
else:
    st.warning("有効なフォルダ名（例: 20260607_airs）を入力してください。")
