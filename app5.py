import streamlit as st

st.title("M4A 音声再生アプリ")

# ローカルのm4aファイルパスまたはURLを指定
audio_file_path = "sample.m4a"

# 音声ファイルの読み込みと再生ウィジェットの表示
with open(audio_file_path, "rb") as audio_file:
    audio_bytes = audio_file.read()

st.audio(audio_bytes, format="audio/m4a")
