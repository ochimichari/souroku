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
        
    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{selected_file_name}.m4a")
    # 🔴 テキストファイルの物理パスを計算 (例: static/20260607_airs/airs.txt)
    text_physical_path = os.path.join(STATIC_DIR, selected_folder, f"{selected_file_name}.txt")

    # オーディオプレイヤーを包むパネル枠
    st.markdown('<div class="player-panel">', unsafe_allow_html=True)
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

    # ログセクション（Session Logs）のヘッダー部分
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

    # 🔴 選択されたフォルダ内のテキストファイル（.txt）を自動で読み込んでHTMLを組み立てる処理
    log_html_content = ""
    
    if os.path.exists(text_physical_path):
        try:
            with open(text_physical_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 行の先頭が「[00:25]」などのタイムスタンプ形式になっているか簡易チェックして分解
                if line.startswith("[") and "]" in line:
                    parts = line.split("]", 1)
                    timestamp = parts[0] + "]" # [00:25]
                    text = parts[1].strip()     # トロンボーンだけで行きましょう
                    
                    log_html_content += f'<div class="log-line"><span class="timestamp">{timestamp}</span> {text}</div>\n'
                else:
                    # タイムスタンプの形になっていない行はそのまま表示
                    log_html_content += f'<div class="log-line">{line}</div>\n'
        except Exception as e:
            log_html_content = f'<div class="log-line" style="color: #ff4b4b;">ファイルの読み込み中にエラーが発生しました。</div>'
    else:
        # テキストファイルがまだ用意されていない場合のメッセージ
        log_html_content = f'<div class="log-line" style="color: #8b949e; font-style: italic;">ログファイルが見つかりません: {selected_file_name}.txt</div>'

    # スクロール付きの黒い枠の中に、自動生成したテキストログを流し込む
    st.markdown(
        f"""
        <div class="log-container">
            {log_html_content}
        </div>
        """,
        unsafe_allow_html=True
    )

    # 配色のCSS設定（ここは前回と同じです）
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-top: 15px; margin-bottom: 8px; }
        .player-panel { background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; }
        .player-panel audio { width: 100%; filter: invert(0.9) hue-rotate(180deg); }
        .time-display-mock { text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }
        .color-bar { display: flex; height: 15px; border-radius: 4px; overflow: hidden; margin-top: 10px; border: 1px solid #00b4d8; }
        .log-container { background-color: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 15px; max-height: 400px; overflow-y: auto; }
        .log-line { font-size: 14px; color: #c9d1d9; margin-bottom: 16px; line-height: 1.5; font-family: sans-serif; }
        .timestamp { color: #8b949e; font-family: monospace; margin-right: 8px; }
        .mock-btn { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px; cursor: pointer; }
        div[data-baseweb="select"] > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
