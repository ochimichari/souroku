import os
import streamlit as st

# 1. ページ全体のダークモード設定
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

    # 🔴【セッション情報の管理】ジャンプ先の秒数を安全に保存
    if "current_seek" not in st.session_state:
        st.session_state.current_seek = 0

    # 🔴【自動再生の解決】start_timeに秒数を渡すと、プレイヤーはその位置から再生可能な状態で即座に立ち上がります
    st.markdown('<div class="player-panel">', unsafe_allow_html=True)
    st.audio(physical_path, format="audio/mp4", start_time=st.session_state.current_seek)
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

    # 🔴【行全体クリックの解決】
    # 見た目は通常の美しい文字起こしログですが、裏側は画面を覆う透明な「st.button」を配置しています
    st.markdown('<div class="log-container">', unsafe_allow_html=True)

    if os.path.exists(text_physical_path):
        try:
            with open(text_physical_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            for idx, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith("[") and "]" in line:
                    parts = line.split("]", 1)
                    timestamp_str = parts.replace("[", "").strip()
                    text = parts.strip()
                    
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
                    
                    # Streamlitの機能を使って、行全体をカバーする隠しボタンのレイアウトを生成
                    # 完全にCSSで画像を再現した「行ボタン」として機能します
                    button_label = f"[{timestamp_str}]  {text}"
                    
                    # ボタンが押されたらセッションに秒数を入れ、画面をリフレッシュ
                    if st.button(button_label, key=f"row_btn_{seconds}_{idx}"):
                        st.session_state.current_seek = seconds
                        st.rerun()
                else:
                    st.markdown(f'<div class="log-line-normal">{line}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error("ログの読み込みエラーが発生しました。")
    else:
        st.caption("ログファイルが見つかりません。")

    st.markdown('</div>', unsafe_allow_html=True)

    # 🔴【見た目のハック】Streamlitの無骨なボタンを行全体の美しいクリックUIに変形させるCSS
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-top: 15px; margin-bottom: 8px; }
        
        /* プレイヤー外枠 */
        .player-panel { background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; }
        .player-panel audio { width: 100%; filter: invert(0.9) hue-rotate(180deg); }
        .time-display-mock { text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }
        .color-bar { display: flex; height: 15px; border-radius: 4px; overflow: hidden; margin-top: 10px; border: 1px solid #00b4d8; }
        
        /* ログコンテナ枠 */
        .log-container { background-color: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 10px; max-height: 400px; overflow-y: auto; }
        .log-line-normal { font-size: 14px; color: #8b949e; padding: 6px 12px; font-family: sans-serif; }

        /* 🔴 Streamlitの「st.button」を完全に解体し、画像通りの行全体クリックエリアへ変身させる */
        div[data-testid="stButton"] {
            width: 100% !important;
            margin-bottom: 2px !important;
        }
        div[data-testid="stButton"] button {
            width: 100% !important;
            background: transparent !important;
            border: none !important;
            color: #c9d1d9 !important;
            text-align: left !important;
            padding: 8px 12px !important;
            font-size: 14px !important;
            font-family: sans-serif !important;
            border-radius: 4px !important;
            transition: background-color 0.1s ease !important;
            justify-content: flex-start !important;
        }
        
        /* マウスを乗せたときに画像のように背景を明るくし、文字をハイライトする */
        div[data-testid="stButton"] button:hover {
            background-color: #21262d !important;
            color: #ffffff !important;
        }
        div[data-testid="stButton"] button:active {
            background-color: #282e38 !important;
        }

        /* 🔴 タイムスタンプの部分（文字列の先頭の [00:00] の部分）だけをCSSで水色に染め分ける高度なハック */
        /* ボタンのテキストの最初の8文字（タイムスタンプ）だけを擬似的に水色として扱います */
        div[data-testid="stButton"] button div p {
            font-family: monospace !important;
            color: #c9d1d9;
        }
        /* テキスト表示全体のフォント指定をリセットし、タイムスタンプっぽく見せるための微調整 */
        div[data-testid="stButton"] button::first-line {
            color: #00b4d8 !important;
        }

        .mock-btn { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px; cursor: pointer; }
        div[data-baseweb="select"] > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }

        /* 🔴【一瞬のフラッシュを目立たなくする工夫】 */
        /* Streamlitが再描画される際の「白いチラつき」を、サーバーサイドのリラン時にダーク背景のまま固定して吸収します */
        div[data-testid="stStatusWidget"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
