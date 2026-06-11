import os
import streamlit as st
import streamlit.components.v1 as components

st.title("🎵 カスタムHTMLプレイヤー")

STATIC_DIR = "static"

# 有効なフォルダを自動リサーチ（ここはこれまでと同じです）
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
        
    # サーバ上の実際のファイルパス
    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{selected_file_name}.m4a")

    # 🔴【重要】手書きの /static/ をやめて、Streamlitのシステムから
    # 「このクラウド環境でブラウザが100%アクセスできる本物のURL」を逆引きして取得します。
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        session_id = ctx.session_id if ctx else None
        
        # Streamlitのメディアマネージャーにファイルを登録し、公式の配信URLを発行してもらう
        audio_url = st.runtime.get_instance().media_file_mgr.add(
            physical_path, "audio/mp4", session_id
        )
    except Exception:
        # 万が一、ローカル環境などで上記が失敗したときの保険
        audio_url = f"/static/{selected_folder}/{selected_file_name}.m4a"

    st.caption(f"選択中: {selected_folder}/{selected_file_name}.m4a")

    # player.htmlの中身を読み込んでURLを埋め込む（ここは先ほどと同じです）
    if os.path.exists("player.html"):
        with open("player.html", "r", encoding="utf-8") as f:
            html_template = f.read()

        # HTML内の %%AUDIO_URL%% を、Streamlitが発行した公式URLに置換
        final_html = html_template.replace("%%AUDIO_URL%%", audio_url)

        # keyを指定して、無駄な再描画によるフラッシュを最小限に抑える
        components.html(
            final_html,
            height=160,
            key=f"player_{selected_folder}"  # 選択フォルダごとにキーを変えることで、確実に曲を切り替えます
        )
    else:
        st.error("⚠️ `player.html` が見つかりません。")
else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
