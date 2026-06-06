import streamlit as st
import google.generativeai as genai
import time
import os
import mimetypes

# 🔒 Streamlitの秘密の環境（Secrets）から安全にAPIキーを読み込む
# ※コードの中にはAPIキーを1文字も書きません！
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Streamlitの管理画面（Secrets）にAPIキーが設定されていません。")
    st.stop()

st.title("楽団合奏 指揮者コメント抽出アプリ")
st.write("30分以上の合奏音源から、指揮者の発言だけをタイムスタンプ付きで抽出します。")

# 🔒 身内用の簡易パスワード設定
password_input = st.sidebar.text_input("楽団の合言葉を入力してください", type="password")

if password_input != "いつもの合言葉":
    st.warning("左側のメニューに正しい「楽団の合言葉」を入力してください。")
    st.stop()

# ----------------------------------------------------
# 音声処理
# ----------------------------------------------------
uploaded_file = st.file_uploader("音声ファイルをアップロードしてください (mp3, wav, m4aなど)", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    st.info("音声を処理中...（大容量ファイルの場合、数分かかることがあります）")
    
    with open("temp_audio", "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    try:
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        if not mime_type:
            mime_type = "audio/mpeg"

        audio_file = genai.upload_file(path="temp_audio", mime_type=mime_type)
        
        while audio_file.state.name == "PROCESSING":
            time.sleep(2)
            audio_file = genai.get_file(audio_file.name)
            
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        prompt = """
        添付された音声は、楽団の合奏練習の録音です。
        演奏全体の音の中から「指揮者が発言しているコメント」だけを特定し、
        以下の条件で文字起こし・抽出をしてください。
        
        条件：
        ・楽器の演奏音やメトロノームの音などは無視してください。
        ・指揮者が演奏を止めて指示を出している部分を中心に抽出してください。
        ・おおよそのタイムスタンプ（開始時間）を必ず記載してください。
        """
        
        response = model.generate_content([audio_file, prompt])
        
        st.success("抽出が完了しました！")
        st.text_area("抽出結果", response.text, height=400)
        
        genai.delete_file(audio_file.name)
        
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        
    finally:
        if os.path.exists("temp_audio"):
            os.remove("temp_audio")
