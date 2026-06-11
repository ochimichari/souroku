import os
import streamlit as st

# 1. ページ全体をダークモード風の背景色に固定
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
        
    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{selected_file_name}.m4a")
    text_physical_path = os.path.join(STATIC_DIR, selected_folder, f"{selected_file_name}.txt")

    # 🔴【ジャンプの仕組み】クリックされた秒数を記憶するセッション状態（State）を作成
    if "seek_seconds" not in st.session_state:
        st.session_state.seek_seconds = 0

    # 🔴 確実に音が鳴る公式プレイヤーに、記憶した秒数（start_time）を流し込みます
    st.markdown('<div class="player-panel">', unsafe_allow_html=True)
    st.audio(physical_path, format="audio/mp4", start_time=st.session_state.seek_seconds)
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

    # ログコンテナの開始
    st.markdown('<div class="log-container">', unsafe_allow_html=True)

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
                    
                    # タイムスタンプを秒数に変換
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
                    
                    # 🔴【最大の変更点】JavaScriptのボタンではなく、Streamlit公式の st.button を配置
                    # クリックされると、指定の秒数を保存してアプリ全体を安全に再起動（リラン）させます
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        if st.button(f"[{timestamp_str}]", key=f"btn_{seconds}_{line[:5]}"):
                            st.session_state.seek_seconds = seconds
                            st.rerun() # 画面を再描画して、プレイヤーの位置を動かす
                    with col2:
                        st.markdown(f'<div class="log-text">{text}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="log-line">{line}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error("ファイルの読み込みエラーが発生しました。")
    else:
        st.caption("ログファイルが見つかりません。")

    # ログコンテナの終了
    st.markdown('</div>', unsafe_allow_html=True)

    # 🔴 画像の「黒基調・水色アクセント」を再現するCSS
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-top: 15px; margin-bottom: 8px; }
        
        /* プレイヤーを囲む黒いパネル枠（水色の境界線） */
        .player-panel { background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; }
        .player-panel audio { width: 100%; filter: invert(0.9) hue-rotate(180deg); }
        
        .color-bar { display: flex; height: 15px; border-radius: 4px; overflow: hidden; margin-top: 10px; border: 1px solid #00b4d8; }
        
        /* ログコンテナ枠（スクロール可能にする） */
        .log-container { background-color: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 15px; max-height: 400px; overflow-y: auto; }
        
        /* 🔴 Streamlitのボタンを画像の水色リンク風に魔改造するCSS */
        div[data-testid="stButton"] button {
            background: transparent !important;
            border: none !important;
            color: #00b4d8 !important;
            font-family: monospace !important;
            padding: 0 !important;
            font-size: 14px !important;
            cursor: pointer !important;
        }
        div[data-testid="stButton"] button:hover {
            text-decoration: underline !important;
            color: #33c2df !important;
        }
        
        .log-text { font-size: 14px; color: #c9d1d9; line-height: 2.2; font-family: sans-serif; }
        .mock-btn { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px; cursor: pointer; }
        div[data-baseweb="select"] > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
