import streamlit as st
import google.generativeai as genai
import time
import os
import mimetypes

st.title("楽団合奏 指揮者コメント抽出アプリ")
st.write("30分以上の合奏音源から、指揮者の発言だけをタイムスタンプ付きで抽出します。")

# 🔒 画面の左側にAPIキーと合言葉の入力欄を作る（セキュリティ対策）
st.sidebar.header("🔑 セキュリティ設定")
api_key_input = st.sidebar.text_input("Gemini APIキーを入力してください", type="password")
password_input = st.sidebar.text_input("楽団の合言葉を入力してください", type="password")

# 合言葉のチェック（身内以外に勝手に使われないようにする設定）
# 「いつもの合言葉」の部分を、楽団のメンバーだけが知っている好きな言葉に変えてください
if password_input != "いつもの合言葉":
    st.warning("左側のメニューに正しい「楽団の合言葉」を入力してください。")
    st.stop()

# APIキーのチェック
if not api_key_input:
    st.info("左側のメニューに「Gemini APIキー」を入力してください。")
    st.stop()
else:
    # 入力されたキーをシステムに適用
    genai.configure(api_key=api_key_input)

# ----------------------------------------------------
# ここから下は通常の処理（APIキーが正しく入力されたら動く）
# ----------------------------------------------------

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
