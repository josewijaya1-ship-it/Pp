import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- KONFIGURASI ---
st.set_page_config(page_title="AI Image & Video Studio", page_icon="🎨")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("API Key gagal dimuat. Cek Secrets di Streamlit Cloud!")
    st.stop()

# Menggunakan model terbaru untuk generate gambar
# Catatan: Pastikan akun Google AI Studio kamu memiliki akses ke Imagen
model_image = genai.GenerativeModel('gemini-1.5-flash') 

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TAMPILAN ---
st.title("🎬 AI Creative Studio")
st.caption("Buat gambar dan video secara instan.")

# Tampilkan history chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["type"] == "text":
            st.write(msg["content"])
        elif msg["type"] == "image":
            st.image(msg["content"], caption="Hasil Generate AI")

# --- PROSES GENERATE ---
if prompt := st.chat_input("Deskripsikan gambar/video..."):
    # Simpan pesan user
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Sedang memproses..."):
            try:
                # MENGGUNAKAN IMAGEN (API Image Generation)
                # Jika akunmu sudah mendukung, gunakan fungsi ini:
                imagen = genai.ImageGenerationModel("imagen-3") # Model terbaru 2026
                response = imagen.generate_images(prompt=prompt, number_of_images=1)
                
                # Ambil gambar pertama
                generated_img = response.images[0]
                
                # Tampilkan langsung
                st.image(generated_img._pil_image)
                
                # Simpan ke history agar tidak hilang saat refresh
                st.session_state.messages.append({
                    "role": "assistant", 
                    "type": "image", 
                    "content": generated_img._pil_image
                })
                
            except Exception as e:
                st.error(f"Maaf, terjadi kesalahan teknis: {e}")
                st.info("Tips: Pastikan kuota API Google Cloud kamu mencukupi untuk Imagen-3.")
