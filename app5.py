import os
import streamlit as st

# アプリのタイトル
st.title("🎵 サーバ音声ファイルプレイヤー")

# 音声ファイルが保存されているフォルダのパス
AUDIO_DIR = "audio_files"

# フォルダが存在しない場合は自動作成
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)
    st.info(f"'{AUDIO_DIR}' フォルダを作成しました。音声を配置してください。")

# 対応する拡張子
SUPPORTED_EXTENSIONS = (".mp3", ".wav", ".m4a", ".ogg", ".flac")

# フォルダ内の音声ファイル一覧を取得
audio_files = [
    f for f in os.listdir(AUDIO_DIR) 
    if f.lower().endswith(SUPPORTED_EXTENSIONS)
]

if audio_files:
    # ユーザーが再生するファイルを選択するセレクトボックス
    selected_file = st.selectbox("再生する音声ファイルを選択してください", audio_files)
    
    # 選択されたファイルのフルパスを作成
    file_path = os.path.join(AUDIO_DIR, selected_file)
    
    # ファイル名と拡張子を表示
    st.write(f"選択中: `{selected_file}`")
    
    # 拡張子からマィムタイプ（MIME type）を自動判別するための準備
    ext = os.path.splitext(selected_file)[1].lower()
    mime_type = f"audio/{ext.replace('.', '')}"
    # m4aの場合は audio/mp4 もしくは audio/x-m4a として扱うとブラウザ互換性が高まります
    if ext == ".m4a":
        mime_type = "audio/mp4"

    # 音声プレイヤーの表示
    st.audio(file_path, format=mime_type)

else:
    st.warning(f"'{AUDIO_DIR}' フォルダの中に音声ファイルが見つかりません。")
