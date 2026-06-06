import streamlit as st
from google import genai
from google.genai import types
import time
import os
import mimetypes

st.title("楽団合奏 指揮者コメント抽出アプリ")
st.write("30分以上の合奏音源から、指揮者の発言だけをタイムスタンプ付きで抽出します。")

# 🔒 画面の左側に入力欄を作成（セキュリティ対策）
st.sidebar.header("🔑 セキュリティ設定")
password_input = st.sidebar.text_input("楽団の合言葉を入力してください", type="password")

# 💡 【重要】利用者が各自の画面から自分のAPIキーを入力する欄
api_key_input = st.sidebar.text_input("ご自身のGemini APIキーを入力してください", type="password")

# 1. まず合言葉のチェック
# ※「いつもの合言葉」の部分を、楽団のメンバーだけが知っている好きな言葉に変えてください
if password_input != "いつもの合言葉":
    st.warning("左側のメニューに正しい「楽団の合言葉」を入力してください。")
    st.stop()

# 2. 次に利用者自身のAPIキーのチェック
if not api_key_input:
    st.info("左側のメニューに「ご自身のGemini APIキー」を入力してください。")
    st.stop()
else:
    # 利用者が入力したキーを変数にセット
    api_key = api_key_input

# ----------------------------------------------------
# 音声処理（ここから下は変更なし）
# ----------------------------------------------------
uploaded_file = st.file_uploader("音声ファイルをアップロードしてください (mp3, wav, m4aなど)", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    st.info("音声を処理中...（大容量ファイルの場合、数分かかることがあります）")
    
    with open("temp_audio", "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    try:
        # MIMEタイプの判別
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        if not mime_type:
            mime_type = "audio/mpeg"

        # 利用者が入力したキーを使ってクライアントを起動（AQ.キーにも完全対応）
        client = genai.Client(api_key=api_key)

        st.write("ファイルをGoogleのサーバーへ転送中...")
        
        # mime_type を config の中に指定してアップロード
        audio_file = client.files.upload(
            file="temp_audio", 
            config=types.UploadFileConfig(mime_type=mime_type)
        )
        
        # アップロード完了を待つループ
        while audio_file.state.name == "PROCESSING":
            time.sleep(3)
            audio_file = client.files.get(name=audio_file.name)
            
        st.write("AIが音声の解析（文字起こし・抽出）を開始しました...")

        # プロンプトの準備
        prompt = """
        添付された音声は、楽団の合奏練習の録音です。
        演奏全体の音の中から「指揮者が発言しているコメント」だけを特定し、
        以下の条件で文字起こし・抽出をしてください。
        
        条件：
        ・楽器の演奏音やメトロノームの音などは無視してください。
        ・指揮者が演奏を止めて指示を出している部分を中心に抽出してください。
        ・おおよそのタイムスタンプ（開始時間）を必ず記載してください。
        """
        
        # コンテンツの生成を実行
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[audio_file, prompt]
        )
        
        st.success("抽出が完了しました！")
        st.text_area("抽出結果", response.text, height=400)
        
        # Googleサーバー上のファイルを削除してクリーンアップ
        client.files.delete(name=audio_file.name)
        
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        
    finally:
        if os.path.exists("temp_audio"):
            os.remove("temp_audio")
