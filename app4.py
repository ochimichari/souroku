import os
import streamlit as st
import streamlit.components.v1 as components

st.title("Streamlit 静的ファイル表示テスト")

# ① Python側で直接ファイルを開く（これが一番確実でエラーになりません）
file_content = "ファイルが見つかりません"
if os.path.exists("test.txt"):
    with open("test.txt", "r", encoding="utf-8") as f:
        file_content = f.read()

# ② HTML/JSを組み立てて、__TEXT__ の部分に中身を直接流し込む
html_code = f"""
<div style="padding:20px; background:#131722; color:#00d2ff; border-radius:8px; font-family:monospace;">
    <h4>【JavaScript側で受け取った中身】</h4>
    <pre id="output">読み込み中...</pre>
</div>

<script>
    // Pythonから直接テキストデータがここに注入されます（CORS制限を完全回避）
    const textData = `{file_content}`;
    
    // 画面に表示する
    document.getElementById('output').innerText = textData;
</script>
"""

# 画面に埋め込み表示
components.html(html_code, height=200)
