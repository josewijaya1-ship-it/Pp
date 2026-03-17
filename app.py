import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- CONFIG ---
st.set_page_config(page_title="AI Studio 3.0", page_icon="🎨")

# --- API SETUP ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key tidak ditemukan di Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TAMPILAN ---
st.title("🎨 AI Image Studio v3.0")
st.caption("Versi Kompatibilitas Tinggi (Anti-Error)")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["type"] == "text":
            st.write(msg["content"])
        else:
            st.image(msg["content"], use_container_width=True)

# --- LOGIKA GENERATE ---
if prompt := st.chat_input("Ketik deskripsi gambar..."):
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Proses pembuatan gambar..."):
            try:
                # Menggunakan inisialisasi model yang paling dasar (paling stabil)
                # Kita panggil Imagen 3 secara eksplisit sebagai string model
                model = genai.GenerativeModel("imagen-3")
                
                # Metode panggil gambar versi alternatif
                response = model.generate_content(prompt)
                
                # Mengambil gambar dari kandidat response
                # Jika response mengandung data gambar (blob)
                img = response.candidates[0].content.parts[0].inline_data.data
                
                st.image(img, use_container_width=True)
                st.session_state.messages.append({"role": "assistant", "type": "image", "content": img})
                
            except Exception as e:
                # Jika masih gagal, kita gunakan fallback ke model flash dengan instruksi gambar
                try:
                    model_flash = genai.GenerativeModel("gemini-1.5-flash")
                    res = model_flash.generate_content(f"Generate an image of: {prompt}")
                    st.write(res.text)
                    st.info("Catatan: Jika gambar tidak muncul, pastikan 'Imagen' sudah aktif di Google AI Studio kamu.")
                except:
                    st.error(f"Sistem gagal: {e}")
