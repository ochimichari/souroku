import streamlit as st
import streamlit.components.v1 as components
import json
import base64
import requests
from pydub import AudioSegment
import io
from google import genai
from google.genai import types

# 画面設定
st.set_page_config(layout="centered", page_title="奏録 / SOUROKU Web版")

# 安全なURLとドメインの定義
API_SCHEME = "https"
API_HOST = "://github.com"
repo_clean = st.secrets['GITHUB_REPO'].strip().strip("/")

HEADERS = {
    "Authorization": f"token {st.secrets['GITHUB_TOKEN'].strip()}",
    "Accept": "application/vnd.github.v3+json"
}

def get_github_file(path):
    """GitHubからファイルを安全に読み込む"""
    url = f"{API_SCHEME}://{API_HOST}/repos/{repo_clean}/contents/{path.lstrip('/')}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            j = res.json()
            content = base64.b64decode(j['content']).decode('utf-8')
            return content, j['sha']
    except Exception:
        pass
    return "", None

def save_github_file(path, text, sha=None):
    """GitHubにファイルを安全に上書き保存する"""
    url = f"{API_SCHEME}://{API_HOST}/repos/{repo_clean}/contents/{path.lstrip('/')}"
    file_name = path.lstrip('/').split('/')[-1]
    payload = {
        "message": f"Log updated via Souroku Web Editor [{file_name}]",
        "content": base64.b64encode(text.encode('utf-8')).decode('utf-8')
    }
    if sha:
        payload["sha"] = sha
    try:
        res = requests.put(url, headers=HEADERS, json=payload, timeout=10)
        return res.status_code in [200, 201]
    except Exception:
        return False

def update_learning_dictionary(old_text, new_text):
    """旧テキストと手動修正後テキストを比較し、自動で正誤リストに蓄積する"""
    old_lines = [l.strip() for l in old_text.split('\n') if l.strip()]
    new_lines = [l.strip() for l in new_text.split('\n') if l.strip()]
    
    dict_content, dict_sha = get_github_file("data/learning_dict.json")
    dictionary = json.loads(dict_content) if dict_content else []
    
    for o, n in zip(old_lines, new_lines):
        if o != n and ']' in o and ']' in n:
            o_msg = o.split(']', 1)[-1].strip()
            n_msg = n.split(']', 1)[-1].strip()
            if o_msg and n_msg and o_msg != n_msg:
                if not any(d['wrong'] == o_msg for d in dictionary):
                    dictionary.append({"wrong": o_msg, "correct": n_msg})
                    
    save_github_file("data/learning_dict.json", json.dumps(dictionary, ensure_ascii=False, indent=2), dict_sha)

# メイン画面初期読み込み
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
            
            # 💡 google-genai 最新SDKのメモリバイナリ送信仕様に完全適合
            audio_part = types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/mp3"
            )
            
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt, audio_part],
                config=types.GenerateContentConfig(http_options={'timeout': 300.0})
            )
            
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

    raw_domain = "https://githubusercontent.com"
    audio_url = f"{raw_domain}/{repo_clean}/main/data/{selected_folder}/{fileName}.m4a"

    # HTMLテンプレートをリストの結合で安全に定義（はみ出し・切断対策）
    html_lines = [
        "<!DOCTYPE html><html lang='ja'><head><meta charset='UTF-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'>",
        "<style>",
        "*{box-sizing:border-box;} body{font-family:-apple-system,sans-serif;margin:0;padding:0;background:#0c0e12;color:#f0f2f5;display:flex;justify-content:center;}",
        ".container{width:100%;max-width:480px;height:95vh;background:#0c0e12;padding:16px;display:flex;flex-direction:column;overflow:hidden;}",
        ".fixed-header-panel{display:flex;flex-direction:column;flex-shrink:0;background:#0c0e12;z-index:10;}",
        "h3{margin:5px 0 15px 0;color:#00d2ff;text-align:center;font-size:18px;font-weight:bold;border-bottom:1px solid #1a1e26;padding-bottom:10px;}",
        ".player-panel{background:#131722;padding:12px;border-radius:8px;border:1px solid #00d2ff;box-shadow:0 0 10px rgba(0,210,255,0.2);margin-bottom:12px;display:flex;flex-direction:column;gap:6px;}",
        "audio{width:100%;height:38px;filter:invert(90%) hue-rotate(180deg);}",
        ".time-display{font-family:monospace;font-size:13px;font-weight:bold;text-align:right;color:#00d2ff;}",
        ".timeline-container{width:100%;margin-bottom:15px;height:35px;}",
        "canvas{width:100%;height:100%;background:#131722;border-radius:6px;cursor:pointer;display:block;border:1px solid #1e2433;}",
        ".log-header-container{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;}",
        ".log-header-title{font-size:14px;font-weight:bold;color:#00d2ff;padding-left:4px;border-left:3px solid #00d2ff;}",
        ".btn-edit{padding:4px 10px;font-size:11px;font-weight:bold;border-radius:4px;cursor:pointer;border:none;background:#00d2ff;color:#0c0e12;}",
        ".btn-edit.editing{background:#4caf50;color:#fff;}",
        ".editor-container{border:1px solid #1e2433;border-radius:8px;flex:1;overflow-y:auto;background:#131722;padding:4px;}",
        ".line{padding:14px 12px;border-bottom:1px solid #1c2230;font-size:13.5px;line-height:1.6;cursor:pointer;color:#cdd4e0;display:flex;align-items:center;}",
        ".line:hover{background:#1c2230;} .edit-input{width:100%;padding:6px 10px;font-size:13.5px;background:#1c2230;border:1px solid #00d2ff;color:#fff;border-radius:4px;outline:none;}",
        ".highlight{background:#1c2c42 !important;font-weight:bold;color:#fff;border-left:5px solid #00d2ff;padding-left:7px;}",
        "</style></head><body>",
        "<div class='container'><div class='fixed-header-panel'><h3>奏録 / SOUROKU</h3>",
        "<div class='player-panel'><audio id='audio' src='__AUDIO_URL__' controls></audio><div class='time-display' id='time-display'>00:00 / 00:00</div></div>",
        "<div class='timeline-container'><canvas id='timeline-canvas'></canvas></div>",
        "<div class='log-header-container'><div class='log-header-title'>Session Logs</div><button id='btn-edit' class='btn-edit' onclick='toggleEditMode()'>編集</button></div></div>",
        "<div class='editor-container' id='editor'>読み込み中...</div></div>",
        "<script>",
        "const audio=document.getElementById('audio'),canvas=document.getElementById('timeline-canvas'),ctx=canvas.getContext('2d'),editor=document.getElementById('editor'),timeDisplay=document.getElementById('time-display'),btnEdit=document.getElementById('btn-edit');",
        "let totalDuration=0,colorData={},textTimestamps=[],isEditing=false;",
        "const rawColor=`__COLOR_RAW__`,rawText=`__TEXT_RAW__`;",
        "function parseColor(r){r.split('\\n').forEach(l=>{const t=l.trim();if(!t||!t.includes(' '))return;const p=t.split(' ');try{const[m,s]=p[0].replace('[','').replace(']','').split(':').map(Number);colorData[m*60+s]=p[1].trim();}catch(e){}})}",
        "function parseText(r){editor.innerHTML='';textTimestamps=[];let idx=0;r.split('\\n').forEach(l=>{const t=l.trim();if(!t)return;const d=document.createElement('div');d.className='line';d.innerText=t;d.id=`line-${idx}`;let s=-1;if(t.startsWith('[')&&t.includes(']')){try{const[m,sec]=t.split(']')[0].replace('[','').split(':').map(Number);s=m*60+sec;}catch(e){}}textTimestamps.push(s);d.addEventListener('click',()=>{if(!isEditing&&s!==-1){audio.currentTime=s;audio.play();}});editor.appendChild(d);idx++;})}",
        "function syncEditorScroll(c){let t=-1;for(let i=0;i<textTimestamps.length;i++){if(textTimestamps[i]!==-1&&textTimestamps[i]<=c){t=i;}else{break;}}document.querySelectorAll('.line').forEach(e=>e.classList.remove('highlight'));if(t!==-1){const a=document.getElementById(`line-${t}`);if(a){a.classList.add('highlight');editor.scrollTo({top:a.offsetTop-editor.offsetTop-20,behavior:'smooth'});}}}",
        "audio.addEventListener('loadedmetadata',()=>{totalDuration=Math.floor(audio.duration);resizeCanvas();});",
        "audio.addEventListener('timeupdate',()=>{const c=Math.floor(audio.currentTime);const curM=String(Math.floor(c/60)).padStart(2,'0'),curS=String(Math.floor(c%60)).padStart(2,'0'),totM=String(Math.floor(totalDuration/60)).padStart(2,'0'),totS=String(Math.floor(totalDuration%60)).padStart(2,'0');timeDisplay.innerText=`${curM}:${curS} / ${totM}:${totS}`;if(!totalDuration)return;ctx.clearRect(0,0,canvas.width,canvas.height);const w=canvas.width/totalDuration;for(let s=0;s<totalDuration;s++){const st=colorData[s]||'SILENT';ctx.fillStyle=st==='SPEECH'?'#cc4a5a':(st==='MUSIC'?'#00a2cc':'#2a3247');ctx.fillRect(s*w,0,w+0.6,canvas.height);}ctx.fillStyle='#00d2ff';ctx.fillRect(((c/totalDuration)*canvas.width)-1,0,3,canvas.height);if(!isEditing)syncEditorScroll(c);});",
        "canvas.addEventListener('click',(e)=>{if(!totalDuration)return;audio.currentTime=Math.floor(((e.clientX-canvas.getBoundingClientRect().left)/canvas.width)*totalDuration);});",
        "function resizeCanvas(){canvas.width=canvas.parentElement.clientWidth;canvas.height=canvas.parentElement.clientHeight;}",
        "window.addEventListener('resize',resizeCanvas);",
        "function toggleEditMode(){const lines=document.querySelectorAll('.line');if(!isEditing){isEditing=true;btnEdit.innerText='保存';btnEdit.classList.add('editing');lines.forEach(d=>{const i=document.createElement('input');i.type='text';i.className='edit-input';i.value=d.innerText;d.innerHTML='';d.appendChild(i);});}else{let u=[];lines.forEach(d=>{const i=d.querySelector('.edit-input');if(i)u.push(i.value.trim());});window.parent.postMessage({type:'streamlit:setComponentValue',value:u.join('\\n')},'*');btnEdit.innerText='通信中...';btnEdit.disabled=true;}}",
        "parseColor(rawColor); parseText(rawText); setTimeout(resizeCanvas,500);",
        "</script></body></html>"
    ]

    # 配列を1つの文字列に結合し、安全にキーワード置換
    html_code = "\n".join(html_lines)
    html_code = html_code.replace("__AUDIO_URL__", audio_url)
    html_code = html_code.replace("__COLOR_RAW__", color_raw.replace('\n', '\\n'))
    html_code = html_code.replace("__TEXT_RAW__", text_raw.replace('\n', '\\n'))

    # 画面描画とデータの回収
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
