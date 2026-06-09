import streamlit as st
import streamlit.components.v1 as components

st.title("Streamlit fetch 動作検証用（決定版）")

# HTML/JSを組み立ててコンポーネントとして実行
html_code = """
<div style="padding:20px; background:#131722; color:#00d2ff; border-radius:8px; font-family:monospace;">
    <h4>【JavaScript の fetch 結果】</h4>
    <pre id="output">fetchを開始します...</pre>
</div>

<script>
    // ドメインのズレを防ぐため、先頭に「 / 」をつけて絶対パスで指定します
    const targetUrl = '/app/static/test.txt?nocache=' + new Date().getTime();

    fetch(targetUrl)
        .then(res => {
            if (!res.ok) {
                // /app/static/ で失敗した場合は、もう一つの候補 /static/ でリトライ
                const fallbackUrl = '/static/test.txt?nocache=' + new Date().getTime();
                document.getElementById('output').innerText = '/app/static/ で失敗したため、/static/ でリトライ中...';
                return fetch(fallbackUrl);
            }
            return res;
        })
        .then(res => {
            if (!res.ok) throw new Error('どちらのパスでも 404 Not Found (またはHTML) になりました。');
            return res.text();
        })
        .then(textData => {
            // 成功したら中身をそのまま表示
            document.getElementById('output').innerText = "【成功】サーバーから受信したテキスト:\n\n" + textData;
        })
        .catch(err => {
            // 失敗したらエラー内容を表示
            document.getElementById('output').innerText = "【失敗】エラーが発生しました:\n" + err.message;
        });
</script>
"""

components.html(html_code, height=250)
