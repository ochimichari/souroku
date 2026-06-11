import os
import streamlit as st

# 1. ページ全体をダークモード風の背景色に固定するためのCSS設定
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
    
    # 2. セレクトボックス部分（青い縦線付きのラベルを配置）
    st.markdown('<p class="section-title">Select session</p>', unsafe_allow_html=True)
    selected_folder = st.selectbox(
        "再生する音声を選択してください", 
        options=available_folders,
        label_visibility="collapsed" # 標準のラベルは隠す
    )
    
    if "_" in selected_folder:
        selected_file_name = selected_folder.split("_")[-1]
    else:
        selected_file_name = selected_folder
        
    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{selected_file_name}.m4a")

    # 3. オーディオプレイヤーを包むパネル枠
    st.markdown('<div class="player-panel">', unsafe_allow_html=True)
    st.audio(physical_path, format="audio/mp4")
    
    # 画像にある「00:00 / 12:12」のような水色の時間表示を再現
    st.markdown('<div class="time-display-mock">00:00 / 12:12</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # カラフルなインジケーター（ダミーのビジュアル要素として配置）
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

    # 4. ログセクション（Session Logs）の再現
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

    # 画像に表示されている文字起こしテキストの再現（スクロール付きの黒い枠）
    st.markdown(
        """
        <div class="log-container">
            <div class="log-line"><span class="timestamp">[00:25]</span> トロンボーンだけで行きましょう</div>
            <div class="log-line"><span class="timestamp">[00:36]</span> 今日トロンボーン7人来てくれました</div>
            <div class="log-line"><span class="timestamp">[00:42]</span> 素晴らしい</div>
            <div class="log-line"><span class="timestamp">[00:46]</span> 素晴らしいですね</div>
            <div class="log-line"><span class="timestamp">[00:53]</span> ちょっと熱いな</div>
            <div class="log-line"><span class="timestamp">[02:12]</span> 基礎合奏気分で、よく鳴らしていきましょう。</div>
            <div class="log-line"><span class="timestamp">[02:16]</span> この曲はハッキリ短くて、タカタカタカタ、ダンダガダガダンダンではないです。</div>
            <div class="log-line"><span class="timestamp">[02:56]</span> メロディーも伴奏も、あと音の長さ半分にできますか？</div>
            <div class="log-line"><span class="timestamp">[03:02]</span> 半分にするためには息のスピードが必要なんですよね。</div>
            <div class="log-line"><span class="timestamp">[03:11]</span> 長いでしょう？</div>
            <div class="log-line"><span class="timestamp">[03:14]</span> スピードが絶対必要になるからね</div>
            <div class="log-line"><span class="timestamp">[03:20]</span> 裏拍の人です</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 🔴 画像の「黒基調・水色アクセント」を完全に適用するCSS
    st.markdown(
        """
        <style>
        /* ページ全体の背景と文字色をダークに矯正 */
        .stApp {
            background-color: #0e1117 !important;
            color: #e2e8f0 !important;
        }
        
        /* 青い縦線の入ったタイトルラベル */
        .section-title {
            font-weight: bold;
            color: #ffffff;
            font-size: 16px;
            border-left: 4px solid #00b4d8;
            padding-left: 8px;
            margin-top: 15px;
            margin-bottom: 8px;
        }

        /* プレイヤーを囲む黒いパネル枠（水色の境界線） */
        .player-panel {
            background-color: #161b22;
            border: 1px solid #00b4d8;
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
        }
        
        /* プレイヤー自体の透過カスタム */
        .player-panel audio {
            width: 100%;
            filter: invert(0.9) hue-rotate(180deg); /* プレイヤーをダーク化しつつ水色になじませる */
        }
        
        /* 水色の時間表示テキスト */
        .time-display-mock {
            text-align: right;
            color: #00b4d8;
            font-family: monospace;
            font-size: 14px;
            margin-top: 5px;
        }

        /* カラフルなインジケーターのバー */
        .color-bar {
            display: flex;
            height: 15px;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
            border: 1px solid #00b4d8;
        }

        /* セッションログのスクロール枠 */
        .log-container {
            background-color: #161b22;
            border: 1px solid #21262d;
            border-radius: 8px;
            padding: 15px;
            max-height: 400px;
            overflow-y: auto;
        }
        
        /* ログの1行ごとの装飾 */
        .log-line {
            font-size: 14px;
            color: #c9d1d9;
            margin-bottom: 16px;
            line-height: 1.5;
            font-family: sans-serif;
        }
        
        /* タイムスタンプ [00:25] のグレー文字 */
        .timestamp {
            color: #8b949e;
            font-family: monospace;
            margin-right: 8px;
        }

        /* 右上のダミーボタン */
        .mock-btn {
            background: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 13px;
            margin-left: 5px;
            cursor: pointer;
        }
        
        /* Streamlit標準のセレクトボックスの見た目をダーク化 */
        div[data-baseweb="select"] > div {
            background-color: #161b22 !important;
            border: 1px solid #30363d !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
