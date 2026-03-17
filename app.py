import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI Image Creator v2.5", page_icon="🎨", layout="centered")

# --- 2. SETUP API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Di Versi 2.5 kita inisialisasi model secara fleksibel
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Konfigurasi Gagal. Pastikan GEMINI_API_KEY sudah benar di Secrets.")
    st.stop()

# --- 3. SESSION STATE ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 4. UI HEADER ---
st.title("🎨 AI Image Studio v2.5")
st.info("Versi Stabil: Fokus pada pembuatan gambar langsung di layar.")

# Tampilkan Riwayat
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.write(message["content"])
        else:
            st.image(message["content"], use_container_width=True)

# --- 5. LOGIKA GENERATE ---
if prompt := st.chat_input("Deskripsikan gambar (Contoh: Pemandangan Gunung Bromo pagi hari)"):
    
    # Tampilkan prompt user
    st.session_state.chat_history.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Sedang memproses gambar..."):
            try:
                # Perbaikan pemanggilan: Menggunakan cara terbaru yang kompatibel
                # Jika ImageGenerationModel tidak ditemukan, kita beri instruksi lewat multimodal
                
                # Coba inisialisasi model gambar secara dinamis
                try:
                    imagen = genai.ImageGenerationModel("imagen-3")
                    response = imagen.generate_images(prompt=prompt)
                    img_result = response.images[0]._pil_image
                except AttributeError:
                    # Jika versi library tidak mendukung attribute tadi, 
                    # kita tampilkan pesan edukatif atau gunakan fallback
                    st.error("Library di server perlu di-update melalui requirements.txt (Versi 0.8.3+)")
                    st.stop()
                
                # Tampilkan Hasil
                st.image(img_result, caption="Hasil Render v2.5", use_container_width=True)
                
                # Simpan ke history
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "type": "image", 
                    "content": img_result
                })

            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
                st.warning("Tips: Pastikan akun Google AI Studio Anda memiliki kuota untuk Imagen-3.")

# --- FOOTER ---
st.write("---")
st.caption("AI Studio 2026 | Versi 2.5 Stabil")
