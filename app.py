import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIG ---
st.set_page_config(page_title="AI Studio v2.5", page_icon="🎨")

# --- 2. API SETUP ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Key belum diset di Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- 3. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. TAMPILAN ---
st.title("🎨 AI Image Studio v2.5")
st.caption("Mode Kompatibilitas Maksimal")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["type"] == "text":
            st.write(msg["content"])
        else:
            st.image(msg["content"], use_container_width=True)

# --- 5. LOGIKA GENERATE ---
if prompt := st.chat_input("Contoh: Lukisan cat air bunga mawar..."):
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Sedang membuat gambar..."):
            try:
                # MENGGUNAKAN MODEL FLASH UNTUK MENGHASILKAN GAMBAR
                # Ini adalah cara paling stabil jika model 'imagen' spesifik ditolak
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                # Kita kirim instruksi spesifik agar dia memberikan output gambar
                response = model.generate_content(
                    f"Generate a high quality image based on this description: {prompt}. "
                    "Return ONLY the image data."
                )
                
                # Cek apakah ada data gambar dalam response
                found_image = False
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data'):
                        img_data = part.inline_data.data
                        st.image(img_data, use_container_width=True)
                        st.session_state.messages.append({"role": "assistant", "type": "image", "content": img_data})
                        found_image = True
                        break
                
                if not found_image:
                    # Jika response hanya teks, tampilkan teksnya
                    st.write(response.text)
                    st.warning("AI memberikan respon teks. Pastikan akun Anda mendukung fitur Image Generation.")
                
            except Exception as e:
                st.error(f"Kesalahan sistem: {e}")
