import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI Image Generator", page_icon="🎨", layout="centered")

# --- 2. SETUP API ---
try:
    # Mengambil key dari Secrets Streamlit
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Menggunakan model Imagen terbaru (Nano Banana 2 / Imagen 3)
    model_imagen = genai.ImageGenerationModel("imagen-3") 
except Exception as e:
    st.error(f"Konfigurasi Gagal: {e}")
    st.stop()

# --- 3. SESSION STATE (Penyimpanan Chat) ---
if "image_history" not in st.session_state:
    st.session_state.image_history = []

# --- 4. TAMPILAN UTAMA ---
st.title("🎨 AI Image Studio")
st.markdown("Ketik deskripsi gambar yang kamu inginkan, dan AI akan melukisnya untukmu.")

# Tampilkan history gambar yang sudah dibuat sebelumnya
for chat in st.session_state.image_history:
    with st.chat_message(chat["role"]):
        if chat["type"] == "text":
            st.write(chat["content"])
        else:
            st.image(chat["content"], use_container_width=True, caption="Hasil Kreasi AI")

# --- 5. LOGIKA GENERATE ---
if prompt := st.chat_input("Contoh: Lukisan kucing astronot di bulan..."):
    
    # Simpan prompt user ke layar
    st.session_state.image_history.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Proses Generate Gambar
    with st.chat_message("assistant"):
        with st.spinner("🚀 Sedang mengimajinasikan gambarmu..."):
            try:
                # Memanggil API Imagen
                response = model_imagen.generate_images(
                    prompt=prompt,
                    number_of_images=1,
                    safety_filter_level="block_some",
                    person_generation="allow_adult"
                )
                
                # Mengambil hasil gambar pertama
                generated_image = response.images[0]
                
                # Langsung tampilkan di aplikasi
                st.image(generated_image._pil_image, use_container_width=True)
                st.success("Berhasil dibuat!")

                # Simpan gambar ke history (agar tidak hilang saat halaman di-refresh)
                st.session_state.image_history.append({
                    "role": "assistant", 
                    "type": "image", 
                    "content": generated_image._pil_image
                })

            except Exception as e:
                st.error(f"Gagal membuat gambar: {e}")
                st.info("Catatan: Pastikan prompt tidak melanggar kebijakan konten Google.")

# --- FOOTER ---
st.write("---")
st.caption("Powered by Google Imagen-3 | 2026 Edition")
