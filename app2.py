import streamlit as st
import streamlit.components.v1 as components
import json
import base64
import requests
from pydub import AudioSegment
import io
from google import genai
from google.genai import types

# 画面幅を中央に最適化
st.set_page_config(layout="centered", page_title="奏録 / SOUROKU Web版")

# --- サーバーサイドでのGitHub API連携 ---
GITHUB_BASE = f"https://github.com{st.secrets['GITHUB_REPO']}/contents"
HEADERS = {
    "Authorization": f"token {st.secrets['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github.v3+json"
}

def get_github_file(path):
    """GitHubからファイルを読み込む（無ければ空を返す）"""
    res = requests.get(f"{GITHUB_BASE}/{path}", headers=HEADERS)
    if res.status_code == 200:
        j = res.json()
        content = base64.b64decode(j['content']).decode('utf-8')
        return content, j['sha']
    return "", None

def save_github_file(path, text, sha=None):
    """GitHubにファイルを上書き保存する"""
    payload = {
        "message": f"Log updated via Souroku Web Editor [{path.split('/')[-1]}]",
        "content": base64.b64encode(text.encode('utf-8')).decode('utf-8')
    }
    if sha:
        payload["sha"] = sha
    res = requests.put(f"{GITHUB_BASE}/{path}", headers=HEADERS, json=payload)
    return res.status_code in [200, 201]

def update_learning_dictionary(old_text, new_text):
    """旧テキストと手動修正後テキストを比較し、自動で正誤リストに蓄積する"""
    old_lines = [l.strip() for l in old_text.split('\n') if l.strip()]
    new_lines = [l.strip() for l in new_text.split('\n') if l.strip()]

    dict_content, dict_sha = get_github_file("data/learning_dict.json")
    dictionary = json.loads(dict_content) if dict_content else []

    for o, n in zip(old_lines, new_lines):
        if o != n and ']' in o and ']' in n:
            o_msg = o.split(']', 1)[1].strip()
            n_msg = n.split(']', 1)[1].strip()
            if o_msg and n_msg and o_msg != n_msg:
                if not any(d['wrong'] == o_msg for d in dictionary):
                    dictionary.append({"wrong": o_msg, "correct": n_msg})

    save_github_file("data/learning_dict.json", json.dumps(dictionary, ensure_ascii=False, indent=2), dict_sha)

# --- メイン画面表示 ---
list_raw, _ = get_github_file("data/list.txt")
folders = [f.strip() for f in list_raw.split('\n') if f.strip()] if list_raw else []

st.title("🎼 奏録 / SOUROKU Web版")

with st.expander("🎙️ 新しい練習音声を Gemini AI で文字起こしする"):
    uploaded_file = st.file_uploader("録音ファイルを選択 (MP3/WAV/M4A)", type=["mp3", "wav", "m4a"])
    session_name = st.text_input("セッション名（例: 20260608_Practice）")

    if uploaded_file and session_name and st.button("AI音声認識を実行"):
        with st.spinner("音声を16kHzモノラルに超軽量化中..."):
            audio_seg = AudioSegment.from_file(io.BytesIO(uploaded_file.read()))
            audio_seg = audio_seg.set_frame_rate(16000).set_channels(1)
            compressed_io = io.BytesIO()
            audio_seg.export(compressed_io, format="mp3", bitrate="32k")
            audio_bytes = compressed_io.getvalue()

        with st.spinner("過去の修正データを読み込んで、Geminiに音声解析を命令中..."):
            dict_content, _ = get_github_file("data/learning_dict.json")
            dictionary = json.loads(dict_content) if dict_content else []
            dict_text = "\n".join([f"- {d['wrong']} ➔ {d['correct']}" for d in dictionary])

            prompt = f"合奏音声から指揮者の発言を `[分:秒] 発言` 形式で抽出して。演奏区間は無視して。\n【補正辞書】\n{dict_text}"

            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")
            response = client.models.generate_content(
                model='gemini-2.5-flash', contents=[prompt, audio_part],
                config=types.GenerateContentConfig(http_options={'timeout': 300.0})
            )

            # タイムライン描画用の擬似color.txtとセッションの保存
            color_lines = [f"[{s//60:02d}:{s%60:02d}] MUSIC" for s in range(int(audio_seg.duration_seconds))]
            fileName = session_name.split('_')[-1] if '_' in session_name else session_name
            save_github_file(f"data/{session_name}/{fileName}.txt", response.text)
            save_github_file(f"data/{session_name}/{fileName}_color.txt", "\n".join(color_lines))

            if session_name not in folders:
                folders.insert(0, session_name)
                save_github_file("data/list.txt", "\n".join(folders))
            st.success("完了しました！")
            st.rerun()

st.subheader("🎵 セッションプレイヤー ＆ ログエディタ")
if folders:
    selected_folder = st.selectbox("Select session", folders)
    fileName = selected_folder.split('_')[-1] if '_' in selected_folder else selected_folder
    text_raw, text_sha = get_github_file(f"data/{selected_folder}/{fileName}.txt")
    color_raw, _ = get_github_file(f"data/{selected_folder}/{fileName}_color.txt")
    audio_url = f"https://githubusercontent.com{st.secrets['GITHUB_REPO']}/main/data/{selected_folder}/{fileName}.m4a"

    # 横幅の折り返しとはみ出しを防ぐため、CSSスタイルを最適化
    html_code = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            * {{ box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding: 0; background: #0c0e12; color: #f0f2f5; display: flex; justify-content: center; }}
            .container {{ width: 100%; max-width: 480px; height: 95vh; background: #0c0e12; padding: 16px; display: flex; flex-direction: column; overflow: hidden; }}
            .fixed-header-panel {{ display: flex; flex-direction: column; flex-shrink: 0; background: #0c0e12; z-index: 10; }}
            h3 {{ margin: 5px 0 15px 0; color: #00d2ff; text-align: center; font-size: 18px; font-weight: bold; border-bottom: 1px solid #1a1e26; padding-bottom: 10px; }}
            .player-panel {{ background: #131722; padding: 12px; border-radius: 8px; border: 1px solid #00d2ff; box-shadow: 0 0 10px rgba(0,210,255,0.2); margin-bottom: 12px; display: flex; flex-direction: column; gap: 6px; }}
            audio {{ width: 100%; height: 38px; filter: invert(90%) hue-rotate(180deg); }}
            .time-display {{ font-family: monospace; font-size: 13px; font-weight: bold; text-align: right; color: #00d2ff; }}
            .timeline-container {{ width: 100%; margin-bottom: 15px; height: 35px; }}
            canvas {{ width: 100%; height: 100%; background: #131722; border-radius: 6px; cursor: pointer; display: block; border: 1px solid #1e2433; }}
            .log-header-container {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
            .log-header-title {{ font-size: 14px; font-weight: bold; color: #00d2ff; padding-left: 4px; border-left: 3px solid #00d2ff; }}
            .btn-edit {{ padding: 4px 10px; font-size: 11px; font-weight: bold; border-radius: 4px; cursor: pointer; border: none; background: #00d2ff; color: #0c0e12; }}
            .btn-edit.editing {{ background: #4caf50; color: #fff; }}
            .editor-container {{ border: 1px solid #1e2433; border-radius: 8px; flex: 1; overflow-y: auto; background: #131722; padding: 4px; }}
            .line {{ padding: 14px 12px; border-bottom: 1px solid #1c2230; font-size: 13.5px; line-height: 1.6; cursor: pointer; color: #cdd4e0; display: flex; align-items: center; }}
            .line:hover {{ background: #1c2230; }}
            .edit-input {{ width: 100%; padding: 6px 10px; font-size: 13.5px; background: #1c2230; border: 1px solid #00d2ff; color: #fff; border-radius: 4px; outline: none; }}
            .highlight {{ background: #1c2c42 !important; font-weight: bold; color: #fff; border-left: 5px solid #00d2ff; padding-left: 7px; }}
        </style>
    </head>
    <body>
    <div class="container">
        <div class="fixed-header-panel">
            <h3>奏録 / SOUROKU</h3>
            <div class="player-panel">
                <audio id="audio" src="{audio_url}" controls></audio>
                <div class="time-display" id="time-display">00:00 / 00:00</div>
            </div>
            <div class="timeline-container"><canvas id="timeline-canvas"></canvas></div>
            <div class="log-header-container">
                <div class="log-header-title">Session Logs</div>
                <button id="btn-edit" class="btn-edit" onclick="toggleEditMode()">編集</button>
            </div>
        </div>
        <div class="editor-container" id="editor">読み込み中...</div>
    </div>
    """

    # 分割3/4のhtml_codeの末尾にJavaScriptをドッキングして、閉じタグを補完します
    html_code += f"""
    <script>
        const audio = document.getElementById('audio');
        const canvas = document.getElementById('timeline-canvas');
        const ctx = canvas.getContext('2d');
        const editor = document.getElementById('editor');
        const timeDisplay = document.getElementById('time-display');
        const btnEdit = document.getElementById('btn-edit');

        let totalDuration = 0, colorData = {{}}, textTimestamps = [], isEditing = false;
        const rawColor = `{color_raw}`, rawText = `{text_raw}`;

        function parseColor(raw) {{
            raw.split('\\n').forEach(line => {{
                const trimmed = line.trim(); if (!trimmed || !trimmed.includes(' ')) return;
                const parts = trimmed.split(' ');
                try {{
                    const [m, s] = parts[0].replace('[', '').replace(']', '').split(':').map(Number);
                    colorData[m * 60 + s] = parts[1].trim();
                }} catch(e) {{}}
            }});
        }}

        function parseText(raw) {{
            editor.innerHTML = ''; textTimestamps = [];
            let idx = 0;
            raw.split('\\n').forEach(line => {{
                const trimmed = line.trim(); if (!trimmed) return;
                const div = document.createElement('div');
                div.className = 'line'; div.innerText = trimmed; div.id = `line-${{idx}}`;
                let seconds = -1;
                if (trimmed.startsWith('[') && trimmed.includes(']')) {{
                    try {{
                        const [m, s] = trimmed.split(']')[0].replace('[', '').split(':').map(Number);
                        seconds = m * 60 + s;
                    }} catch(e) {{}}
                }}
                textTimestamps.push(seconds);
                div.addEventListener('click', () => {{
                    if (!isEditing && seconds !== -1) {{ audio.currentTime = seconds; audio.play(); }}
                }});
                editor.appendChild(div); idx++;
            }});
        }}

        function syncEditorScroll(currentSec) {{
            let targetIdx = -1;
            for (let i = 0; i < textTimestamps.length; i++) {{
                if (textTimestamps[i] !== -1 && textTimestamps[i] <= currentSec) {{ targetIdx = i; }}
                else {{ break; }}
            }}
            document.querySelectorAll('.line').forEach(el => el.classList.remove('highlight'));
            if (targetIdx !== -1) {{
                const activeLine = document.getElementById(`line-${{targetIdx}}`);
                if (activeLine) {{
                    activeLine.classList.add('highlight');
                    editor.scrollTo({{ top: activeLine.offsetTop - editor.offsetTop - 20, behavior: 'smooth' }});
                }}
            }}
        }}

        audio.addEventListener('loadedmetadata', () => {{ totalDuration = Math.floor(audio.duration); resizeCanvas(); }});
        audio.addEventListener('timeupdate', () => {{
            const currentSeconds = Math.floor(audio.currentTime);
            const curM = String(Math.floor(currentSeconds / 60)).padStart(2, '0');
            const curS = String(Math.floor(currentSeconds % 60)).padStart(2, '0');
            const totM = String(Math.floor(totalDuration / 60)).padStart(2, '0');
            const totS = String(Math.floor(totalDuration % 60)).padStart(2, '0');
            timeDisplay.innerText = `${{curM}}:${{curS}} / ${{totM}}:${{totS}}`;

            // タイムライン描画
            if (!totalDuration) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const secWidth = canvas.width / totalDuration;
            for (let s = 0; s < totalDuration; s++) {{
                ctx.fillStyle = colorData[s] === "SPEECH" ? "#cc4a5a" : (colorData[s] === "MUSIC" ? "#00a2cc" : "#2a3247");
                ctx.fillRect(s * secWidth, 0, secWidth + 0.6, canvas.height);
            }}
            ctx.fillStyle = "#00d2ff";
            ctx.fillRect(((currentSeconds / totalDuration) * canvas.width) - 1, 0, 3, canvas.height);

            if (!isEditing) syncEditorScroll(currentSeconds);
        }});

        canvas.addEventListener('click', (e) => {{
            if (!totalDuration) return;
            audio.currentTime = Math.floor(((e.clientX - canvas.getBoundingClientRect().left) / canvas.width) * totalDuration);
        }});

        function resizeCanvas() {{ canvas.width = canvas.parentElement.clientWidth; canvas.height = canvas.parentElement.clientHeight; }}
        window.addEventListener('resize', resizeCanvas);

        function toggleEditMode() {{
            const lines = document.querySelectorAll('.line');
            if (!isEditing) {{
                isEditing = true; btnEdit.innerText = "保存"; btnEdit.classList.add('editing');
                lines.forEach(div => {{
                    const input = document.createElement('input'); input.type = 'text'; input.className = 'edit-input'; input.value = div.innerText;
                    div.innerHTML = ''; div.appendChild(input);
                }});
            }} else {{
                let updatedLines = [];
                lines.forEach(div => {{ const input = div.querySelector('.edit-input'); if (input) updatedLines.push(input.value.trim()); }});

                // 💡 window.parent.postMessage でStreamlit（Python側）へデータを送信
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: updatedLines.join('\\n')}}, '*');
                btnEdit.innerText = "通信中..."; btnEdit.disabled = true;
            }}
        }}

        parseColor(rawColor);
        parseText(rawText);
        setTimeout(resizeCanvas, 500);
    </script>
    </body>
    </html>
    """

    # HTMLの描画と、JS側から受け取った保存データの処理
    edited_text = components.html(html_code, height=650, scrolling=False)

    if edited_text and edited_text.strip() != text_raw.strip():
        with st.spinner("GitHubに上書き保存し、自動精度向上リストを更新中..."):
            if save_github_file(f"data/{selected_folder}/{fileName}.txt", edited_text, text_sha):
                update_learning_dictionary(text_raw, edited_text)
                st.success("保存と自動学習が成功しました！")
                st.rerun()
            else:
                st.error("GitHubへの保存に失敗しました。")
else:
    st.info("データがありません。上のメニューから文字起こしを開始してください。")
