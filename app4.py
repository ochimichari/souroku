import os
import streamlit as st
import streamlit.components.v1 as components

st.title("Streamlit fetch 動作検証用")

# HTML/JSを組み立ててコンポーネントとして実行
html_code = """
<div style="padding:20px; background:#131722; color:#00d2ff; border-radius:8px; font-family:monospace;">
    <h4>【JavaScript の fetch 結果】</h4>
    <pre id="output">fetchを開始します...</pre>
</div>

<script>
    // Streamlitの静的ファイル配信の標準ルール「app/static/ファイル名」を叩きます
    const targetUrl = 'app/static/test.txt?nocache=' + new Date().getTime();

    fetch(targetUrl)
        .then(res => {
            if (!res.ok) {
                // 404などのエラーが返ってきたら、予備のパス「static/ファイル名」でもう一度試す
                const fallbackUrl = 'static/test.txt?nocache=' + new Date().getTime();
                document.getElementById('output').innerText = 'app/static/ で失敗したため、static/ でリトライ中...';
                return fetch(fallbackUrl);
            }
            return res;
        })
        .then(res => {
            if (!res.ok) throw new Error('どちらのパスでも 404 Not Found になりました。');
            return res.text();
        })
        .then(textData => {
            // 成功したら中身をそのまま表示
            document.getElementById('output').innerText = "【成功】サーバーから受信したテキスト:\n\n" + textData;
        })
        .catch(err => {
            // 失敗したらエラー内容を表示（ここに例のHTMLソースが映るかどうかが分かります）
            document.getElementById('output').innerText = "【失敗】エラーが発生しました:\n" + err.message;
        });
</script>
"""

components.html(html_code, height=250)
