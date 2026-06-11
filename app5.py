import os
import pandas as pd
import streamlit as st

# 1. ページ全体のダークモード風の背景色設定
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

    # 🔴【セッション管理】再生開始位置と自動再生フラグを保存
    if "seek_seconds" not in st.session_state:
        st.session_state.seek_seconds = 0
    if "auto_play_flag" not in st.session_state:
        st.session_state.auto_play_flag = False

    # 🔴【完璧な再生連動】
    # 行がクリックされたら、指定された秒数から「autoplay=True（自動再生）」でプレイヤーを起動します
    st.markdown('<div class="player-panel">', unsafe_allow_html=True)
    st.audio(
        physical_path, 
        format="audio/mp4", 
        start_time=st.session_state.seek_seconds,
        autoplay=st.session_state.auto_play_flag
    )
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

    # 🔴【安全なログ解析とデータ化】
    # テキストファイルを開き、エラーを起こさない頑丈なロジックで表データ（DataFrame）に変換します
    log_data = []
    
    if os.path.exists(text_physical_path):
        try:
            with open(text_physical_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or not line.startswith("[") or "]" not in line:
                        continue
                    
                    # 確実に [00:25] と テキスト に分離する
                    idx_close = line.find("]")
                    timestamp_str = line[1:idx_close].strip() # "00:25"
                    text_content = line[idx_close+1:].strip() # "トロンボーンだけで..."
                    
                    # タイムスタンプを秒数に換算
                    try:
                        time_parts = timestamp_str.split(":")
                        if len(time_parts) == 2:
                            secs = int(time_parts[0]) * 60 + int(time_parts[1])
                        elif len(time_parts) == 3:
                            secs = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
                        else:
                            secs = 0
                    except ValueError:
                        secs = 0
                        
                    log_data.append({
                        "Time": f"[{timestamp_str}]",
                        "Log": text_content,
                        "seconds_hidden": secs # 裏側で管理するジャンプ用の秒数
                    })
        except Exception:
            st.error("⚠️ テキストファイルの読み込み中にエラーが発生しました。")

    # 🔴【行全体クリックとジャンプの完全実現】
    # 公式の st.dataframe を表線なし・クリックイベント付きでログ枠として配置します
    if log_data:
        df = pd.DataFrame(log_data)
        
        # ユーザーが行を選択（クリック）したときのイベントをキャッチ
        selected_row = st.dataframe(
            df[["Time", "Log"]], # 画面に見せる列だけを指定
            hide_index=True,
            use_container_width=True,
            on_select="rerun", # クリックしたら瞬時にPythonを動かす設定
            selection_mode="single-row" # 行全体の選択を許可
        )
        
        # 行が実際にクリックされたら、その行の「seconds_hidden」を取得してプレイヤーをキック
        if selected_row and len(selected_row.selection.rows) > 0:
            row_idx = selected_row.selection.rows[0]
            target_seconds = df.iloc[row_idx]["seconds_hidden"]
            
            # セッションに値を保存して自動再生を有効化
            st.session_state.seek_seconds = int(target_seconds)
            st.session_state.auto_play_flag = True
            st.rerun()

    else:
        st.warning("有効なログデータが見つかりません。")

    # 🔴 画像通りの色合いに染め上げるCSSカスタム
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-top: 15px; margin-bottom: 8px; }
        .player-panel { background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; }
        .player-panel audio { width: 100%; filter: invert(0.9) hue-rotate(180deg); }
        .time-display-mock { text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }
        .color-bar { display: flex; height: 15px; border-radius: 4px; overflow: hidden; margin-top: 10px; border: 1px solid #00b4d8; }
        
        /* 🔴 データフレーム（ログテーブル）を画像のような黒いリストに強制変身させるCSS */
        div[data-testid="stDataFrame"] {
            background-color: #161b22 !important;
            border: 1px solid #21262d !important;
            border-radius: 8px !important;
            padding: 5px !important;
        }
        /* テーブルのヘッダー（Time, Logという文字）を非表示にしてスッキリさせる */
        div[data-testid="stDataFrame"] thead { display: none !important; }
        
        /* タイムスタンプテキストの文字色を水色にする */
        div[data-testid="stDataFrame"] td:first-child {
            color: #00b4d8 !important;
            font-family: monospace !important;
            font-weight: bold;
        }
        
        .mock-btn { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px; cursor: pointer; }
        div[data-baseweb="select"] > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
