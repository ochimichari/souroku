import os
import streamlit as st
import streamlit.components.v1 as components

# 1. 画面全体の表示設定
st.set_page_config(
    page_title="奏録 / SOUROKU Web",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Streamlit標準の余白を強制的に消すCSS
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            padding-left: 0px !important;
            padding-right: 0px !important;
            max-width: 100% !important;
        }
        iframe {
            display: block;
            border: none;
            width: 100vw;
            height: 100vh;
        }
    </style>
""", unsafe_allow_html=True)

# 2. 移植するHTML/CSS/JSコードの組み立て
html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>奏録 / SOUROKU Web版</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding: 0; background: #0c0e12; color: #f0f2f5; display: flex; justify-content: center; height: 100vh; overflow: hidden; }
        .container { width: 100%; max-width: 480px; height: 100vh; background: #0c0e12; padding: 16px; display: flex; flex-direction: column; overflow: hidden; }
        .fixed-header-panel { display: flex; flex-direction: column; flex-shrink: 0; background: #0c0e12; z-index: 10; }
        h3 { margin: 5px 0 15px 0; color: #00d2ff; text-align: center; font-size: 18px; font-weight: bold; letter-spacing: 0.5px; border-bottom: 1px solid #1a1e26; padding-bottom: 10px; }
        .selector-panel { background: #131722; padding: 12px; border-radius: 8px; border: 1px solid #1e2433; margin-bottom: 12px; }
        .panel-title { font-size: 14px; font-weight: bold; color: #00d2ff; margin-bottom: 8px; padding-left: 4px; border-left: 3px solid #00d2ff; }
        select { width: 100%; padding: 12px; font-size: 14px; border-radius: 6px; border: 1px solid #2a3247; background: #1c2230; color: #fff; font-weight: bold; outline: none; }
        .player-panel { background: #131722; padding: 12px; border-radius: 8px; border: 1px solid #00d2ff; box-shadow: 0 0 10px rgba(0,210,255,0.2); margin-bottom: 12px; display: flex; flex-direction: column; gap: 6px; }
        audio { width: 100%; height: 38px; filter: invert(90%) hue-rotate(180deg); }
        .time-display { font-family: monospace; font-size: 13px; font-weight: bold; text-align: right; padding-right: 4px; color: #00d2ff; }
        .timeline-container { width: 100%; margin-bottom: 15px; height: 35px; }
        canvas { width: 100%; height: 100%; background: #131722; border-radius: 6px; cursor: pointer; display: block; border: 1px solid #1e2433; }
        .log-header-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .log-header-title { font-size: 14px; font-weight: bold; color: #00d2ff; padding-left: 4px; border-left: 3px solid #00d2ff; }
        .btn-group { display: flex; gap: 6px; }
        .btn { padding: 4px 10px; font-size: 11px; font-weight: bold; border-radius: 4px; cursor: pointer; border: none; outline: none; transition: background 0.2s; }
        .btn-edit { background: #00d2ff; color: #0c0e12; }
        .btn-edit.editing { background: #4caf50; color: #fff; }
        .btn-setting { background: #1e2433; color: #8892b0; border: 1px solid #2a3247; }
        .editor-container { border: 1px solid #1e2433; border-radius: 8px; flex: 1; overflow-y: auto; background: #131722; -webkit-overflow-scrolling: touch; padding: 4px; }
        .line { padding: 14px 12px; border-bottom: 1px solid #1c2230; font-size: 13.5px; line-height: 1.6; cursor: pointer; color: #cdd4e0; -webkit-tap-highlight-color: transparent; transition: background 0.1s; display: flex; align-items: center; }
        .line:hover { background: #1c2230; }
        .edit-input { width: 100%; padding: 6px 10px; font-size: 13.5px; background: #1c2230; border: 1px solid #00d2ff; color: #fff; border-radius: 4px; outline: none; font-family: inherit; }
        .highlight { background: #1c2c42 !important; font-weight: bold; color: #fff; border-left: 5px solid #00d2ff; padding-left: 7px; }
    </style>
</head>
<body>
<div class="container">
    <div class="fixed-header-panel">
        <h3>奏録 / SOUROKU</h3>
        <div class="selector-panel">
            <div class="panel-title">Select session</div>
            <select id="folder-selector" onchange="changeFolder(this.value)"></select>
        </div>
        <div class="player-panel">
            <audio id="audio" controls></audio>
            <div class="time-display" id="time-display">00:00 / 00:00</div>
        </div>
        <div class="timeline-container">
            <canvas id="timeline-canvas"></canvas>
        </div>
        <div class="log-header-container">
            <div class="log-header-title">Session Logs</div>
            <div class="btn-group">
                <button class="btn btn-setting" onclick="setupGitConfig()">設定</button>
                <button id="btn-edit" class="btn btn-edit" onclick="toggleEditMode()">編集</button>
            </div>
        </div>
    </div>
    <div class="editor-container" id="editor">
        <div style="color: #64748b; text-align: center; padding-top: 60px; font-size:13px;">データを読み込み中...</div>
    </div>
</div>
"""
# 1回目の変数 html_content の末尾に文字列を追加します
html_content += """
<script>
    const audio = document.getElementById('audio');
    const canvas = document.getElementById('timeline-canvas');
    const ctx = canvas.getContext('2d');
    const editor = document.getElementById('editor');
    const timeDisplay = document.getElementById('time-display');
    const selector = document.getElementById('folder-selector');
    const btnEdit = document.getElementById('btn-edit');

    let totalDuration = 0;
    let colorData = {};
    let textTimestamps = [];
    
    let isEditing = false;
    let currentLoadedFolder = "";
    let currentFileSha = ""; 

    // 環境に依存する静的ファイルのルートパス（app/static/ か static/ を自動判別）
    let staticRoot = "";

    function resizeCanvas() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
        drawTimeline();
    }
    window.addEventListener('resize', resizeCanvas);

    function setupGitConfig() {
        const repo = prompt("GitHubの『ユーザー名/リポジトリ名』を入力してください\\n(例: myusername/souroku-repo)", localStorage.getItem('git_repo') || "");
        if (repo) localStorage.setItem('git_repo', repo.trim());
        
        const token = prompt("GitHubの個人用アクセストークン(PAT)を入力してください", localStorage.getItem('git_token') || "");
        if (token) localStorage.setItem('git_token', token.trim());
    }

    function loadFolderList() {
        // まずは標準の static/ から試します
        fetch(staticRoot + 'list.txt?nocache=' + new Date().getTime())
            .then(res => {
                if (!res.ok) throw new Error();
                return res.text();
            })
            .then(rawText => { processFolderList(rawText); })
            .catch(() => {
                // 失敗した場合は、Streamlit内部の別ルート app/static/ でリトライします
                staticRoot = "app/static/";
                fetch(staticRoot + 'list.txt?nocache=' + new Date().getTime())
                    .then(res => { if (!res.ok) throw new Error(); return res.text(); })
                    .then(rawText => { processFolderList(rawText); })
                    .catch(() => {
                        editor.innerHTML = `<div style="color:#ef5350; text-align:center; padding-top:40px; font-size:13px;">.streamlit/static/list.txt を読み込めませんでした。<br>配置場所を確認してください。</div>`;
                    });
            });
    }

    function processFolderList(rawText) {
        selector.innerHTML = '';
        const folders = rawText.split('\\n').map(f => f.trim()).filter(f => f.length > 0);
        folders.forEach(folder => {
            const opt = document.createElement('option');
            opt.value = folder;
            opt.innerText = folder.replace(/_/g, ' ');
            selector.appendChild(opt);
        });
        // 【修正】配列全体ではなく、最初の要素（folders[0]）を渡すように直しました
        if (folders.length > 0) changeFolder(folders[0]);
    }

    function fallbackFetch(folderName, fileName) {
        fetch(`${staticRoot}${folderName}/${fileName}.txt?nocache=` + new Date().getTime())
            .then(res => { if (!res.ok) throw new Error(); return res.text(); })
            .then(textRaw => {
                parseText(textRaw);
                resizeCanvas();
            }).catch(() => { logLoadError(); });
    }

    function logLoadError() {
        editor.innerHTML = `<div style="color:#ef5350; text-align:center; padding-top:40px; font-size:13px;">データ配置を確認するか、設定ボタンからGitHub連携情報を入力してください。</div>`;
    }

    function parseColor(raw) {
        const lines = raw.split('\\n');
        lines.forEach(line => {
            const trimmed = line.trim();
            if (!trimmed || !trimmed.includes(' ')) return;
            
            const parts = trimmed.split(' ');
            const tStr = parts[0];
            const status = parts[1];
            try {
                const [m, s] = tStr.replace('[', '').replace(']', '').split(':').map(Number);
                colorData[m * 60 + s] = status.trim();
            } catch(e) {}
        });
    }

    audio.addEventListener('loadedmetadata', () => {
        totalDuration = Math.floor(audio.duration);
        updateTimeLabel();
        resizeCanvas();
    });

    audio.addEventListener('timeupdate', () => {
        const currentSeconds = Math.floor(audio.currentTime);
        updateTimeLabel();
        drawTimeline(currentSeconds);
        if (!isEditing) {
            syncEditorScroll(currentSeconds);
        }
    });

    function drawTimeline(currentSec = 0) {
        if (!totalDuration) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const secWidth = canvas.width / totalDuration;
        
        for (let s = 0; s < totalDuration; s++) {
            const x0 = s * secWidth;
            const status = colorData[s] || "SILENT";
            if (status === "SPEECH") ctx.fillStyle = "#cc4a5a";
            else if (status === "MUSIC") ctx.fillStyle = "#00a2cc";
            else ctx.fillStyle = "#2a3247";
            ctx.fillRect(x0, 0, secWidth + 0.6, canvas.height);
        }
        const indX = (currentSec / totalDuration) * canvas.width;
        ctx.fillStyle = "#00d2ff";
        ctx.fillRect(indX - 1, 0, 3, canvas.height);
    }

    canvas.addEventListener('click', (e) => {
        if (!totalDuration) return;
        const rect = canvas.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const targetSec = Math.floor((clickX / canvas.width) * totalDuration);
        audio.currentTime = targetSec;
    });

    function updateTimeLabel() {
        const curM = String(Math.floor(audio.currentTime / 60)).padStart(2, '0');
        const curS = String(Math.floor(audio.currentTime % 60)).padStart(2, '0');
        const totM = String(Math.floor(totalDuration / 60)).padStart(2, '0');
        const totS = String(Math.floor(totalDuration % 60)).padStart(2, '0');
        timeDisplay.innerText = `${curM}:${curS} / ${totM}:${totS}`;
    }
"""
# 中盤パートの変数 html_content の末尾にさらに文字列を追加し、最後に描画します
html_content += """
    function changeFolder(folderName) {
        audio.pause();
        editor.innerHTML = `<div style="color: #64748b; text-align: center; padding-top: 60px;">読み込み中...</div>`;
        
        if (isEditing) {
            isEditing = false;
            btnEdit.innerText = "編集";
            btnEdit.classList.remove('editing');
        }

        colorData = {};
        textTimestamps = [];
        totalDuration = 0;
        currentLoadedFolder = folderName;
        currentFileSha = ""; 

        let fileName = folderName;
        if (folderName.includes('_')) {
            const parts = folderName.split('_');
            fileName = parts[parts.length - 1];
        }
        
        audio.src = `${staticRoot}${folderName}/${fileName}.m4a`;
        audio.load();

        fetch(`${staticRoot}${folderName}/${fileName}_color.txt?nocache=` + new Date().getTime())
            .then(res => { if (!res.ok) throw new Error(); return res.text(); })
            .then(colorRaw => {
                parseColor(colorRaw);
                
                const repo = (localStorage.getItem('git_repo') || "").trim();
                const token = (localStorage.getItem('git_token') || "").trim();
                const path = `data/${folderName}/${fileName}.txt`;
                
                if (repo && token) {
                    const apiDomain = ["https:", "", "://github.com", "repos", ""].join("/");
                    
                    fetch(apiDomain + repo + "/contents/" + path, {
                        headers: { 
                            "Authorization": "Bearer " + token,
                            "Accept": "application/vnd.github+json"
                        }
                    })
                    .then(res => { if (!res.ok) throw new Error(); return res.json(); })
                    .then(json => {
                        currentFileSha = json.sha;
                        const binaryString = atob(json.content.replace(/\\s/g, ''));
                        const bytes = new Uint8Array(binaryString.length);
                        for (let i = 0; i < binaryString.length; i++) {
                            bytes[i] = binaryString.charCodeAt(i);
                        }
                        const decodedText = new TextDecoder('utf-8').decode(bytes);
                        parseText(decodedText);
                        resizeCanvas();
                    })
                    .catch(() => { fallbackFetch(folderName, fileName); });
                } else {
                    fallbackFetch(folderName, fileName);
                }
                
            })
            .catch(() => { logLoadError(); });
    }

    function parseText(raw) {
        editor.innerHTML = '';
        textTimestamps = [];
        const lines = raw.split('\\n');
        let idx = 0;
        
        lines.forEach((line) => {
            const trimmed = line.trim();
            if (!trimmed) return;
            
            const div = document.createElement('div');
            div.className = 'line';
            div.innerText = trimmed;
            div.id = `line-${idx}`;
            
            let seconds = -1;
            if (trimmed.startsWith('[') && trimmed.includes(']')) {
                try {
                    const parts = trimmed.split(']');
                    const tStr = parts[0].replace('[', '');
                    const [m, s] = tStr.split(':').map(Number);
                    seconds = m * 60 + s;
                } catch(e) {}
            }
            textTimestamps.push(seconds);

            div.addEventListener('click', () => {
                if (!isEditing && seconds !== -1) {
                    audio.currentTime = seconds;
                    audio.play();
                }
            });
            editor.appendChild(div);
            idx++;
        });
    }

    function toggleEditMode() {
        const repo = (localStorage.getItem('git_repo') || "").trim();
        const token = (localStorage.getItem('git_token') || "").trim();
        
        if (!repo || !token) {
            alert("先に「設定」ボタンからGitHubの連携設定（リポジトリ名・トークン）を行ってください。");
            setupGitConfig();
            return;
        }

        const lines = document.querySelectorAll('.line');
        
        if (!isEditing) {
            isEditing = true;
            btnEdit.innerText = "保存";
            btnEdit.classList.add('editing');
            
            lines.forEach(div => {
                const currentText = div.innerText;
                const input = document.createElement('input');
                input.type = 'text';
                input.className = 'edit-input';
                input.value = currentText;
                div.innerHTML = '';
                div.appendChild(input);
            });
        } else {
            let updatedLines = [];
            lines.forEach(div => {
                const input = div.querySelector('.edit-input');
                if (input) updatedLines.push(input.value.trim());
            });
            
            const fullText = updatedLines.join('\\n');
            
            btnEdit.innerText = "通信中...";
            btnEdit.disabled = true;

            let fileName = currentLoadedFolder;
            if (currentLoadedFolder.includes('_')) {
                const parts = currentLoadedFolder.split('_');
                fileName = parts[parts.length - 1];
            }
            const path = `data/${currentLoadedFolder}/${fileName}.txt`;

            const u8array = new TextEncoder().encode(fullText);
            let binary = '';
            for (let i = 0; i < u8array.byteLength; i++) {
                binary += String.fromCharCode(u8array[i]);
            }
            const b64Content = btoa(binary);

            const apiDomain = ["https:", "", "://github.com", "repos", ""].join("/");

            fetch(apiDomain + repo + "/contents/" + path, {
                method: "PUT",
                headers: {
                    "Authorization": "Bearer " + token,
                    "Accept": "application/vnd.github+json",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: "Log updated via Souroku Web Editor [" + fileName + "]",
                    content: b64Content,
                    sha: currentFileSha
                })
            })
            .then(res => {
                if (!res.ok) {
                    return res.json().then(errData => {
                        throw new Error(errData.message || "API送信エラー");
                    });
                }
                return res.json();
            })
            .then(json => {
                alert("GitHubへの上書き保存が成功しました！\\n(※Pagesの反映には数分かかる場合があります)");
                currentFileSha = json.content.sha;
                
                isEditing = false;
                btnEdit.innerText = "編集";
                btnEdit.disabled = false;
                btnEdit.classList.remove('editing');
                
                parseText(fullText);
                drawTimeline(Math.floor(audio.currentTime));
            })
            .catch(err => {
                alert("GitHubへの保存に失敗しました。\\nエラー内容: " + err.message);
                btnEdit.innerText = "保存";
                btnEdit.disabled = false;
            });
        }
    }

    function syncEditorScroll(currentSec) {
        let targetIdx = -1;
        for (let i = 0; i < textTimestamps.length; i++) {
            if (textTimestamps[i] !== -1 && textTimestamps[i] <= currentSec) {
                targetIdx = i;
            } else { break; }
        }
        
        document.querySelectorAll('.line').forEach(el => el.classList.remove('highlight'));
        if (targetIdx !== -1) {
            const activeLine = document.getElementById(`line-${targetIdx}`);
            if (activeLine) {
                activeLine.classList.add('highlight');
                editor.scrollTo({
                    top: activeLine.offsetTop - editor.offsetTop - 20,
                    behavior: 'smooth'
                });
            }
        }
    }

    window.onload = () => { loadFolderList(); };
</script>
</body>
</html>
"""

# Streamlitの画面にコンポーネントとして埋め込み
components.html(html_content, height=1000, scrolling=False)
