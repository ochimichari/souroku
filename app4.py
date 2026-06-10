import streamlit as st
import streamlit.components.v1 as components

st.title("fetch単体 動作検証コード")

html_code = """
<div style="padding:20px; background:#131722; color:#00d2ff; border-radius:8px;">
    <h4>【JavaScript fetchの結果】</h4>
    <pre id="output">fetch待機中...</pre>
</div>

<script>
    // 現在のページURL（ドメイン）を自動で取得して絶対パスを組み立てる
    const domain = window.location.origin;
    const targetUrl = domain + '/app/static/test.txt?nocache=' + new Date().getTime();

    // ログ出力してfetch開始
    console.log("リクエスト先:", targetUrl);

    fetch(targetUrl)
        .then(res => {
            console.log("ステータス:", res.status);
            if (!res.ok) throw new Error("通信に失敗しました。ステータスコード: " + res.status);
            return res.text();
        })
        .then(textData => {
            document.getElementById('output').innerText = "【成功】ファイルの中身:\n\n" + textData;
        })
        .catch(err => {
            document.getElementById('output').innerText = "【失敗】" + err.message;
        });
</script>
"""

components.html(html_code, height=250)
