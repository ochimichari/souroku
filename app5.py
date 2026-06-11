import os
import streamlit as st
import streamlit.components.v1 as components

st.title("🎵 カスタムHTMLプレイヤー (自動検索版)")

STATIC_DIR = "static"

# 1. static フォルダが存在しない場合は空のリストにする
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
    st.info(f"'{STATIC_DIR}' フォルダを作成しました。音声フォルダを配置してください。")

# 2. static配下のフォルダを自動リサーチして、有効な音声フォルダの一覧を作る
available_folders = []

if os.path.exists(STATIC_DIR):
    for folder in os.listdir(STATIC_DIR):
        folder_path = os.path.join(STATIC_DIR, folder)
        
        # ディレクトリ（フォルダ）である場合のみ処理
        if os.path.isdir(folder_path):
            # フォルダ名からファイル名を計算 (例: 20260607_airs -> airs)
            if "_" in folder:
                file_name = folder.split("_")[-1]
            else:
                file_name = folder
                
            # 実際に m4a ファイルが存在するかチェック
            m4a_path = os.path.join(folder_path, f"{file_name}.m4a")
            if os.path.exists(m4a_path):
                available_folders.append(folder)

# 3. 画面に選択肢（セレクトボックス）を表示
if available_folders:
    # 昇順で並び替え（日付順などに見やすくするため）
    available_folders.sort()
    
    selected_folder = st.selectbox(
        "再生する音声を選択してください", 
        options=available_folders
    )
    
    # 4. 選択されたフォルダからURLを特定
    if "_" in selected_folder:
        selected_file_name = selected_folder.split("_")[-1]
    else:
        selected_file_name = selected_folder
        
    audio_url = f"/static/{selected_folder}/{selected_file_name}.m4a"
    
    # 画面に現在選択中の情報を表示
    st.caption(f"再生中: {selected_folder}/{selected_file_name}.m4a")

    # 5. player.html を読み込んで埋め込み
    if os.path.exists("player.html"):
        with open("player.html", "r", encoding="utf-8") as f:
            html_code = f.read()

        components.html(
            html_code + f"""
            <script>
                window.audioUrlFromPython = "{audio_url}";
                if (typeof initPlayer === "function") {{
                    initPlayer();
                }}
            </script>
            """,
            height=200,
        )
    else:
        st.error("⚠️ `player.html` が見つかりません。")
else:
    st.warning("`static` フォルダ内に、有効な音声ファイル（フォルダ名と一致するm4a）が見つかりません。")
