import streamlit as st
import google.generativeai as genai
import time
import os
import mimetypes

# 1. Gemini APIの設定（APIキーは環境変数から読み込むか、ここに直接記述）
GOOGLE_API_KEY = "AIzaSyDrpDwlWIjBGlWGhX-Pvp9159rQSg327HI"
genai.configure(api_key=GOOGLE_API_KEY)

st.title("楽団合奏 指揮者コメント抽出アプリ")
st.write("30分以上の合奏音源から、指揮者の発言だけをタイムスタンプ付きで抽出します。")

# 2. ファイルアップローダーの設置
uploaded_file = st.file_uploader("音声ファイルをアップロードしてください (mp3, wav, m4aなど)", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    st.info("音声を処理中...（大容量ファイルの場合、数分かかることがあります）")
    
    # 一時ファイルとして保存
    with open("temp_audio", "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    try:
        # 3. ファイル形式（MIMEタイプ）を拡張子から自動判別する
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        if not mime_type:
            # 判別できない場合のセーフティとして、一般的なオーディオ形式を指定
            mime_type = "audio/mpeg"

# mime_type引数を追加してアップロードを実行
audio_file = genai.upload_file(path="temp_audio", mime_type=mime_type)
        
        # アップロード完了を待つループ
        while audio_file.state.name == "PROCESSING":
            time.sleep(2)
            audio_file = genai.get_file(audio_file.name)
            
        # 4. 指揮者コメントを抽出するプロンプトを投げる
        model = genai.GenerativeModel(model_name="gemini-1.5-flash") # 精度重視なら gemini-1.5-pro
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
        
        # 5. 結果の表示
        st.success("抽出が完了しました！")
        st.text_area("抽出結果", response.text, height=400)
        
        # Googleサーバー上のファイルを削除してクリーンアップ
        genai.delete_file(audio_file.name)
        
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        
    finally:
        # 一時ファイルの削除
        if os.path.exists("temp_audio"):
            os.remove("temp_audio")
