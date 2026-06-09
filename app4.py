import streamlit as st
import streamlit.components.v1 as components

st.title("Streamlit 外部 fetch 検証用コード")

html_code = """
<div style="padding:20px; background:#131722; color:#00d2ff; border-radius:8px; font-family:monospace;">
    <h4>【外部 fetch の結果】</h4>
    <pre id="output">fetchを開始します...</pre>
</div>

<script>
    // 例として、世界のタイムゾーン一覧を配信している公開API（外部サーバー）をfetchします
    // これならStreamlit内部の壁に邪魔されずに通信が通ります
    const targetUrl = 'https://worldtimeapi.org';

    fetch(targetUrl)
        .then(res => {
            if (!res.ok) throw new Error('通信エラーが発生しました。');
            return res.json();
        })
        .then(data => {
            // 取得したデータ（アジアの都市など）の最初の5つを画面に表示
            const sliceData = data.slice(0, 5).join('\\n');
            document.getElementById('output').innerText = "【成功】外部からのfetchが通りました！:\\n\\n" + sliceData;
        })
        .catch(err => {
            document.getElementById('output').innerText = "【失敗】" + err.message;
        });
</script>
"""

components.html(html_code, height=250)
