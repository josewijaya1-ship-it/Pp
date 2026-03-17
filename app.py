import streamlit as st
import google.generativeai as genai
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Gemini Multimodal Studio", 
    page_icon="🎬", 
    layout="wide"
)

# --- KONFIGURASI API (Versi Terbaru) ---
try:
    # Mengambil API Key dari Streamlit Secrets
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Konfigurasi API Gagal. Pastikan GEMINI_API_KEY sudah diset di Secrets.")
    st.stop()

# Inisialisasi Model
# Catatan: Nama model di bawah adalah placeholder untuk implementasi API Generative AI terbaru
model_text = genai.GenerativeModel("gemini-1.5-flash")

# --- SESSION STATE ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    mode = st.radio("Pilih Output:", ["Gambar (Image)", "Video (Veo)"])
    
    st.info(f"Mode saat ini: **{mode}**")
    st.write("---")
    if st.button("Hapus Riwayat"):
        st.session_state.history = []
        st.rerun()

# --- FUNGSI GENERATOR ---
def generate_creative_content(prompt, mode):
    """
    Fungsi simulasi pemanggilan API Nano Banana 2 (Image) dan Veo (Video).
    Pastikan library google-generativeai Anda sudah versi terbaru.
    """
    if mode == "Gambar (Image)":
        # Simulasi pemanggilan model Nano Banana 2
        # Di versi produksi: imagen = genai.ImageGenerationModel("nano-banana-2")
        with st.spinner("🎨 Sedang melukis gambar..."):
            time.sleep(3) # Simulasi proses
            # Logic: response = imagen.generate_images(prompt=prompt)
            st.success("Gambar berhasil dibuat!")
            return "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe" # Contoh output
            
    elif mode == "Video (Veo)":
        # Simulasi pemanggilan model Veo
        with st.spinner("🎬 Sedang me-render video..."):
            time.sleep(5) # Simulasi proses video lebih lama
            st.success("Video berhasil di-generate!")
            return "https://www.w3schools.com/html/mov_bbb.mp4" # Contoh output

# --- TAMPILAN UTAMA ---
st.title("🚀 Gemini AI Vision Studio")
st.subheader(f"Buat {mode} impianmu hanya dengan teks.")

# Input Prompt
user_prompt = st.chat_input(f"Deskripsikan {mode} yang ingin kamu buat...")

if user_prompt:
    # Tambahkan ke history
    st.session_state.history.append({"role": "user", "type": "text", "content": user_prompt})
    
    # Proses AI
    result_url = generate_creative_content(user_prompt, mode)
    
    # Simpan hasil AI
    res_type = "image" if mode == "Gambar (Image)" else "video"
    st.session_state.history.append({"role": "assistant", "type": res_type, "content": result_url})

# Tampilkan Chat & Hasil
for chat in st.session_state.history:
    if chat["role"] == "user":
        with st.chat_message("user"):
            st.write(chat["content"])
    else:
        with st.chat_message("assistant"):
            if chat["type"] == "image":
                st.image(chat["content"], caption="Hasil AI Image", use_column_width=True)
                st.button("Download Gambar", key=time.time())
            else:
                st.video(chat["content"])
                st.caption("Video di-generate oleh Veo Model")

# --- FOOTER ---
st.markdown("---")
st.caption("Powered by Gemini 3 Flash & Veo | 2026 AI Edition")
