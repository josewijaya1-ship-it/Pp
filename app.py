import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI Studio v2.5", page_icon="🎨", layout="centered")

# --- KONFIGURASI API ---
try:
    # Membaca API Key dari Secrets Streamlit
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Menggunakan model Generative paling stabil
    # Kami tidak memanggil 'imagen-3' secara langsung untuk menghindari error 404
    model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    st.error(f"API Key bermasalah: {e}")
    st.stop()

# --- SISTEM PENYIMPANAN SESSION ---
if "image_chats" not in st.session_state:
    st.session_state.image_chats = []

# --- TAMPILAN UTAMA ---
st.title("🎨 AI Image Studio v2.5")
st.markdown("Buat gambar apa pun yang ada di imajinasimu secara instan.")

# Menampilkan Riwayat Chat & Gambar
for chat in st.session_state.image_history if "image_history" in st.session_state else []:
    with st.chat_message(chat["role"]):
        if chat["type"] == "text":
            st.markdown(chat["content"])
        else:
            st.image(chat["content"], use_container_width=True)

# --- INPUT USER & LOGIKA AI ---
if prompt := st.chat_input("Deskripsikan gambar (contoh: Pemandangan sawah di Bali)..."):
    
    # Simpan dan tampilkan pesan user
    if "image_history" not in st.session_state:
        st.session_state.image_history = []
    
    st.session_state.image_history.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respon AI
    with st.chat_message("assistant"):
        with st.spinner("Sedang melukis..."):
            try:
                # Perintah khusus agar model memicu pembuatan gambar (Imagen)
                response = model.generate_content(f"Generate an image of: {prompt}")
                
                # Cek apakah ada data gambar di dalam response
                found_img = False
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data'): # Ini adalah data gambar mentah
                        img_data = part.inline_data.data
                        st.image(img_data, use_container_width=True)
                        st.session_state.image_history.append({"role": "assistant", "type": "image", "content": img_data})
                        found_img = True
                        break
                
                if not found_img:
                    # Jika AI hanya menjawab teks
                    st.write(response.text)
                    st.info("Catatan: Google sedang membatasi fitur gambar di beberapa region.")
                    st.session_state.image_history.append({"role": "assistant", "type": "text", "content": response.text})
                
            except Exception as e:
                st.error(f"Gagal memproses gambar: {e}")
