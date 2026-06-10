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
        canvas { width: 100%; height: 100%; background: #131722; border-radius: 6px; display: block; border: 1px solid #1e2433; }
        .log-header-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .log-header-title { font-size: 14px; font-weight: bold; color: #00d2ff; padding-left: 4px; border-left: 3px solid #00d2ff; }
        .btn-group { display: flex; gap: 6px; }
        .btn { padding: 4px 10px; font-size: 11px; font-weight: bold; border-radius: 4px; border: none; outline: none; color: #8892b0; background: #1e2433; }
        .editor-container { border: 1px solid #1e2433; border-radius: 8px; flex: 1; overflow-y: auto; background: #131722; padding: 4px; }
    </style>
</head>
<body>

<!-- Python(app3.py)からの置換用プレースホルダーを設置 -->
<div id="raw-json-list" style="display:none;">__JSON_LIST__</div>

<div class="container">
    <div class="fixed-header-panel">
        <h3>奏録 / SOUROKU</h3>
        <div class="selector-panel">
            <div class="panel-title">Select session</div>
            <!-- ロード検証用に一度シンプルにします -->
            <select id="folder-selector"></select>
        </div>
        <div class="player-panel">
            <audio id="audio" controls></audio>
            <div class="time-display">00:00 / 00:00</div>
        </div>
        <div class="timeline-container">
            <canvas id="timeline-canvas"></canvas>
        </div>
        <div class="log-header-container">
            <div class="log-header-title">Session Logs</div>
            <div class="btn-group">
                <button class="btn">編集</button>
            </div>
        </div>
    </div>
    <div class="editor-container" id="editor">
        <div id="status-message" style="color: #64748b; text-align: center; padding-top: 60px; font-size:13px;">リスト読み込み検証中...</div>
    </div>
</div>

<script>
    document.addEventListener('DOMContentLoaded', () => {
        const selector = document.getElementById('folder-selector');
        const statusMsg = document.getElementById('status-message');
        const listEl = document.getElementById('raw-json-list');

        try {
            // 1. 埋め込まれたJSON文字列を取得してパース
            const sessionList = JSON.parse(listEl.textContent);
            console.log("読み込んだリスト:", sessionList);

            // 2. ドロップダウン（select）の選択肢を生成
            selector.innerHTML = '';

            if (!sessionList || sessionList.length === 0) {
                selector.innerHTML = '<option>セッションが見つかりません</option>';
                statusMsg.textContent = "list.txt が空か、読み込めていません。";
                return;
            }

            sessionList.forEach(folder => {
                const opt = document.createElement('option');
                opt.value = folder;
                opt.textContent = folder;
                selector.appendChild(opt);
            });

            statusMsg.textContent = "リストの読み込みに成功しました。次の実装ステップに進めます。";

        } catch (error) {
            console.error("パースエラー:", error);
            statusMsg.innerHTML = `<span style="color:#ef5350;">JSONパース失敗: ${error.message}</span>`;
        }
    });
</script>
</body>
</html>