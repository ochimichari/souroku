import os
import streamlit as st

st.set_page_config(layout="centered")
st.markdown('<div style="text-align: center; margin-bottom: 20px;"><h2 style="color: #00b4d8; font-family: sans-serif; letter-spacing: 1px;">🎵 奏録 / SOUROKU</h2></div>', unsafe_allow_html=True)

STATIC_DIR = "static"
available_folders = []

if os.path.exists(STATIC_DIR):
    for folder in os.listdir(STATIC_DIR):
        folder_path = os.path.join(STATIC_DIR, folder)
        if os.path.isdir(folder_path):
            file_name = folder.split("_")[-1] if "_" in folder else folder
            m4a_path = os.path.join(folder_path, f"{file_name}.m4a")
            if os.path.exists(m4a_path):
                available_folders.append(folder)

available_folders.sort()

if available_folders:
    st.markdown('<p class="section-title">Select session</p>', unsafe_allow_html=True)
    selected_folder = st.selectbox("再生する音声を選択してください", options=available_folders, label_visibility="collapsed")
    
    file_name = selected_folder.split("_")[-1] if "_" in selected_folder else selected_folder
    
    if "last_folder" not in st.session_state or st.session_state.last_folder != selected_folder:
        st.session_state.last_folder = selected_folder
        st.session_state.seek_seconds = 0
        st.session_state.auto_play = False

    physical_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.m4a")
    txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}.txt")
    color_txt_path = os.path.join(STATIC_DIR, selected_folder, f"{file_name}_color.txt")

    # 🔴【スマホ軽量化の鍵】
    # スマホがタップした秒数（スマホからのジャンプ命令）を受け取るための、画面に見えない隠し入力欄
    # 大量のボタンの代わりに、この「1つのテキストボックス」だけでカラーバー全員分のクリックを中継します
    if "js_seek_trigger" not in st.session_state:
        st.session_state.js_seek_trigger = ""

    # スクリプトから文字列が届いたら、秒数に変換して再生位置を動かす
    if st.session_state.js_seek_trigger != "":
        st.session_state.seek_seconds = int(st.session_state.js_seek_trigger)
        st.session_state.auto_play = True
        st.session_state.js_seek_trigger = "" # 即座にクリアしてループを防止

    # 音声プレイヤー
    st.markdown('<div class="player-panel">', unsafe_allow_html=True)
    st.audio(physical_path, format="audio/mp4", start_time=st.session_state.seek_seconds, autoplay=st.session_state.auto_play)
    st.markdown('<div class="time-display-mock">00:00 / 12:12</div></div>', unsafe_allow_html=True)

    # 🔴【軽量化カラーバー】1秒ごとの大量のタグを作らず、CSSグラデーションの文字列「1本の線」に圧縮します
    gradient_stops = []
    total_seconds = 0
    
    if os.path.exists(color_txt_path):
        with open(color_txt_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip().startswith("[")]
        
        total_seconds = len(lines)
        if total_seconds > 0:
            for idx, line in enumerate(lines):
                status = line.split("]")[-1].strip().upper()
                color_code = "#ff4b4b" if "SPEECH" in status else "#00b4d8" if "MUSIC" in status else "#30363d"
                
                # パーセンテージ位置を割り出し、グラデーションの色の繋ぎ目を作ります
                pos = (idx / total_seconds) * 100
                pos_next = ((idx + 1) / total_seconds) * 100
                gradient_stops.append(f"{color_code} {pos}%, {color_code} {pos_next}%")
                
    # 1本に合体させた美しいCSSグラデーションバー。タグの総数はわずか「1個」なのでスマホでも超軽量です
    gradient_style = f"background: linear-gradient(to right, {', '.join(gradient_stops)});" if gradient_stops else "background: #30363d;"

    st.markdown(f'<div class="color-bar-container" id="pure-css-bar" style="{gradient_style}" onclick="handleBarClick(event, {total_seconds})"></div>', unsafe_allow_html=True)

    st.markdown('<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 25px; margin-bottom: 15px;"><span class="section-title" style="margin:0;">Session Logs</span><div><button class="mock-btn">設定</button><button class="mock-btn" style="background:#00b4d8; color:#0e1117; border:none;">編集</button></div></div>', unsafe_allow_html=True)

    # ログ全体のコンテナ
    st.markdown('<div class="log-master-outer">', unsafe_allow_html=True)

    # ログリストの表示
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if line.startswith("[") and "]" in line:
                    idx_close = line.find("]")
                    time_str = line[1:idx_close].strip()
                    text_content = line[idx_close+1:].strip()
                    try:
                        p = time_str.split(":")
                        if len(p) == 2: secs = int(p[0]) * 60 + int(p[1])
                        elif len(p) == 3: secs = int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])
                        else: secs = 0
                    except: secs = 0
                    
                    if st.button(f"[{time_str}]  {text_content}", key=f"row_{secs}_{idx}"):
                        st.session_state.seek_seconds = secs
                        st.session_state.auto_play = True
                        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    # 🔴【後半】スマホからのタップ位置（パーセンテージ）を正確に秒数に換算して裏写しする最新スクリプト
    # 画面からは文字入力欄（st.text_input）をCSSで完全に覆い隠し、通信のトンネルとしてのみ利用します
    st.markdown(
        """
        <script>
        function handleBarClick(event, totalSec) {
            if (totalSec <= 0) return;
            
            // タップされたカラーバーの要素の正確な横幅を取得
            const bar = document.getElementById('pure-css-bar');
            const rect = bar.getBoundingClientRect();
            
            // バーの左端から、タップされた位置までのピクセル距離を計測
            const clickX = event.clientX - rect.left;
            
            // 横幅のうち、何％の地点が叩かれたかの比率を割り出す
            const ratio = clickX / rect.width;
            
            // 総再生秒数にその比率を掛け算して、「タップされた正確な秒数」を割り出す
            const targetSecond = Math.floor(ratio * totalSec);
            
            // 🔴 iframeの壁やセキュリティに一切弾かれない、Streamlitの隠しテキストボックスを探し出す
            const inputs = window.parent.document.querySelectorAll('div[data-testid="stTextInput"] input');
            if (inputs.length > 0) {
                // 見えないテキストボックスに割り出した秒数（例: "75"）を文字として書き込む
                inputs[0].value = targetSecond;
                
                // 文字が入力された瞬間に、Streamlit側に「値が変わったから再描画（リラン）して！」という確定信号（Enterキーのイベント）を送信
                inputs[0].dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
        </script>
        """,
        unsafe_allow_html=True
    )

    # 🔴 画面上の通信用テキストボックスを非表示にし、横幅を画像通りに固定するCSS
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117 !important; color: #e2e8f0 !important; }
        .section-title { font-weight: bold; color: #ffffff; font-size: 16px; border-left: 4px solid #00b4d8; padding-left: 8px; margin-bottom: 8px; }
        .player-panel { background-color: #161b22; border: 1px solid #00b4d8; border-radius: 8px; padding: 15px; margin-top: 10px; width: 100% !important; box-sizing: border-box; }
        .player-panel audio { width: 100%; filter: invert(0.9) hue-rotate(180deg); }
        .time-display-mock { text-align: right; color: #00b4d8; font-family: monospace; font-size: 14px; margin-top: 5px; }
        
        /* 🔴 HTMLタグを1個だけに集約した、超軽量CSSグラデーションバー */
        .color-bar-container { 
            height: 20px; 
            border-radius: 4px; 
            border: 1px solid #00b4d8; 
            margin-top: 15px; 
            margin-bottom: 15px; 
            width: 100% !important; 
            box-sizing: border-box;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,180,216,0.1);
        }
        .color-bar-container:hover {
            filter: brightness(1.2); /* ホバー時にバー全体を少し明るくしてタップ可能であることを示唆 */
        }

        /* ログコンテナ全体の横幅100%維持ルール */
        div.log-master-outer {
            background-color: #161b22 !important;
            border: 1px solid #21262d !important;
            border-radius: 8px !important;
            padding: 10px !important;
            max-height: 380px !important;
            overflow-y: auto !important;
            width: 100% !important;
            display: block !important;
            box-sizing: border-box;
        }
        
        div.log-master-outer div[data-testid="element-container"],
        div.log-master-outer div[data-testid="stButton"] { 
            width: 100% !important; 
            max-width: 100% !important;
            margin-bottom: 0px !important; 
            display: block !important; 
        }
        
        div.log-master-outer div[data-testid="stButton"] button {
            width: 100% !important; background: transparent !important; border: none !important;
            color: #c9d1d9 !important; text-align: left !important; padding: 6px 12px !important;
            font-size: 14px !important; border-radius: 4px !important; justify-content: flex-start !important;
            display: block !important;
        }
        div.log-master-outer div[data-testid="stButton"] button:hover { background-color: #21262d !important; color: #ffffff !important; }
        div.log-master-outer div[data-testid="stButton"] button::first-line { color: #00b4d8 !important; font-family: monospace !important; }
        
        .mock-btn { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-left: 5px; }
        div[data-baseweb="select"] > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: white !important; }
        div[data-testid="stStatusWidget"] { display: none !important; }
        
        /* 🔴 通信用に配置した st.text_input を画面から完全に消し去る魔法のCSS */
        div[data-testid="stTextInput"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 🔴【最重要・通信の心臓部】
    # JavaScriptから秒数を受け取るための公式テキスト入力欄。上のCSS（display:none）でユーザーからは1ミリも見えません
    st.text_input("hidden_communicator", key="js_seek_trigger")

else:
    st.warning("`static` フォルダ内に有効な音声フォルダが見つかりません。")
