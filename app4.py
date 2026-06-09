import streamlit as st
import streamlit.components.v1 as components

st.title("fetch単体 動作検証（appなしルート）")

html_code = """
<div style="padding:20px; background:#131722; color:#00d2ff; border-radius:8px;">
    <h4>【JavaScript fetchの結果】</h4>
    <pre id="output">fetch待機中...</pre>
</div>

<script>
    // 【重要】app/ を排除し、正しい絶対パス /static/ を指定します
    const targetUrl = '/static/test.txt?nocache=' + new Date().getTime();

    fetch(targetUrl)
        .then(res => {
            // ここで中身がHTML（Streamlitの画面）になっていないかチェック
            const contentType = res.headers.get("content-type");
            if (contentType && contentType.includes("text/html")) {
                throw new Error("404エラーの代わりにStreamlitのHTML画面が返ってきてしまいました。パスが間違っています。");
            }
            if (!res.ok) throw new Error("通信に失敗しました。ステータス: " + res.status);
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
