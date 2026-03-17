import streamlit as st
import requests
import google.generativeai as genai

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI Photo Studio", page_icon="🖼️", layout="wide")

# --- KONFIGURASI API (Secrets) ---
# Di Streamlit Cloud, konfigurasi ini diisi di bagian Settings > Secrets
try:
    # Key untuk Stability AI (Generasi Gambar)
    STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]
    
    # Key untuk Google Gemini (Fitur Pembantu: Judul & Deskripsi Otomatis)
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"]) 
except Exception:
    st.error("API Keys (Stability AI & Gemini) belum terpasang di Secrets! Aplikasi tidak bisa berjalan.")
    st.stop()

# Inisialisasi model Gemini (pilih yang cepat/flash)
model_gemini = genai.GenerativeModel("gemini-2.5-flash")

# --- SISTEM PENYIMPANAN SESSION (RIWAYAT) ---
# Menggunakan st.session_state agar data tidak hilang saat re-run halaman
if "all_photos" not in st.session_state:
    st.session_state.all_photos = {} 

if "current_photo_id" not in st.session_state:
    st.session_state.current_photo_id = None

# --- FUNGSI PEMBANTU (Helper Functions) ---

# Fungsi untuk membuat judul singkat menggunakan AI Gemini
def generate_photo_title(prompt):
    try:
        if not prompt: return "Foto Tanpa Prompt"
        # Meminta Gemini meringkas prompt menjadi 3 kata
        response = model_gemini.generate_content(f"Buat judul singkat (max 3 kata) dalam Bahasa Indonesia untuk hasil foto dari deskripsi ini: {prompt}")
        return response.text.strip()
    except:
        return "Foto Baru"

# Fungsi inti untuk memanggil API Stability AI (Versi Ultra 2026)
def generate_image_ultra(prompt, ratio, model_ai="ultra"):
    """
    Memanggil API Stability AI versi terbaru (v2beta ultra).
    Returns: Bytes data gambar jika sukses, None jika gagal.
    """
    # Endpoint terbaru untuk generasi kualitas tertinggi
    url = f"https://api.stability.ai/v2beta/stable-image/generate/{model_ai}"
    
    headers = {
        "authorization": f"Bearer {STABILITY_API_KEY}",
        "accept": "image/*" # Kita ingin hasil dalam bentuk binary gambar
    }
    
    # Data dikirim sebagai multipart/form-data
    data = {
        "prompt": prompt,
        "output_format": "webp", # webp memberikan kompresi bagus dengan kualitas tinggi
        "aspect_ratio": ratio    # Rasio aspek yang dipilih user
    }
    
    # Files kosong diperlukan karena API membutuhkan multipart request
    files = {"none": ''}
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        if response.status_code == 200:
            return response.content # Mengembalikan bytes gambar
        else:
            # Mengembalikan pesan error dari API
            error_data = response.json()
            st.error(f"Error API: {error_data.get('errors', 'Kesalahan tidak diketahui')}")
            return None
    except Exception as e:
        st.error(f"Gagal terhubung ke API: {e}")
        return None

# --- SIDEBAR: DAFTAR RIWAYAT FOTO ---
with st.sidebar:
    st.title("🖼️ Galeri Saya")
    st.caption("Fokus: Generasi Foto Ultra High-Def")
    
    # Tombol untuk mereset input dan membuat foto baru
    if st.button("+ Buat Foto Baru", use_container_width=True):
        st.session_state.current_photo_id = None
        st.rerun()

    st.write("---")
    # Menampilkan riwayat foto yang sudah dibuat dalam session ini
    st.subheader("Riwayat Sesi Ini")
    for photo_id in list(st.session_state.all_photos.keys()):
        # Gunakan tombol berikon untuk memilih foto dari riwayat
        if st.button(f"📷 {photo_id}", key=photo_id, use_container_width=True):
            st.session_state.current_photo_id = photo_id
            st.rerun()

# --- TAMPILAN UTAMA ---
st.title("🎨 AI Photo Studio: Ultra Generation")
st.markdown("Hasilkan foto dan gambar digital dengan detail luar biasa menggunakan teknologi **Stability AI Ultra** terbaru.")

# Menggunakan expander untuk menyembunyikan form input agar tampilan bersih
with st.expander("📝 Masukkan Deskripsi Foto (Prompt)", expanded=True):
    with st.form("photo_form"):
        # Input deskripsi utama
        img_prompt = st.text_area(
            "Deskripsikan foto yang kamu inginkan:", 
            placeholder="Contoh: Portrait seekor kucing cybernetic di pasar masa depan, pencahayaan neon, gaya cyberpunk, detail tinggi, f/1.8..."
        )
        
        # Opsi pengaturan rasio aspek
        col1, col2 = st.columns(2)
        with col1:
            ratio = st.selectbox("Aspek Rasio (Ukuran)", ["1:1 (Kotak)", "16:9 (Cinematic)", "9:16 (Phone Story)", "3:2 (Fotografi)", "21:9 (Ultrawide)"])
        with col2:
            # Membersihkan pilihan rasio untuk dikirim ke API (mengambil angkanya saja)
            clean_ratio = ratio.split(" ")[0]
            st.caption(f"Akan diproses dengan rasio: {clean_ratio}")
            
        # Tombol submit form
        submitted = st.form_submit_button("Generate Ultra Photo")

# --- LOGIKA GENERASI FOTO ---
if submitted:
    if not img_prompt:
        st.warning("Silakan masukkan deskripsi foto terlebih dahulu!")
    else:
        # 1. Buat judul otomatis dengan Gemini (agar rapi di sidebar)
        with st.spinner("AI sedang merencanakan judul..."):
            project_name = generate_photo_title(img_prompt)
        
        # Set project ini sebagai yang aktif saat ini
        st.session_state.current_photo_id = project_name
        
        # 2. Panggil API untuk generate gambar
        # Menggunakan status untuk memberikan feedback proses
        with st.status("Sedang melukis foto ultra high-def...", expanded=True) as status:
            st.write("Menghubungi Stability AI...")
            img_data = generate_image_ultra(img_prompt, clean_ratio)
            
            if img_data:
                status.update(label="Generasi foto selesai!", state="complete", expanded=False)
                
                # Tampilkan hasilnya langsung
                st.write("---")
                st.subheader(f"Hasil: {project_name}")
                st.image(img_data, caption=img_prompt, use_container_width=True)
                
                # Sediakan tombol download
                st.download_button(
                    label="💾 Download Foto (WEBP)",
                    data=img_data,
                    file_name=f"{project_name.replace(' ', '_').lower()}.webp",
                    mime="image/webp"
                )
                
                # 3. Simpan hasil ke session state (riwayat)
                st.session_state.all_photos[project_name] = {
                    "content": img_data, 
                    "prompt": img_prompt,
                    "ratio": ratio
                }
            else:
                status.update(label="Generasi foto gagal.", state="error", expanded=True)

# --- TAMPILAN JIKA MEMILIH DARI RIWAYAT ---
# Jika user mengeklik judul di sidebar, tampilkan detail yang disimpan
if st.session_state.current_photo_id and not submitted:
    # Mengambil data dari storage berdasarkan ID yang dipilih
    data = st.session_state.all_photos.get(st.session_state.current_photo_id)
    
    if data:
        st.write("---")
        st.subheader(f"Viewing: {st.session_state.current_photo_id}")
        
        # Layout kolom untuk detail
        col_img, col_txt = st.columns([3, 1])
        
        with col_img:
            # Tampilkan foto
            st.image(data['content'], use_container_width=True)
            
        with col_txt:
            # Tampilkan info dan tombol
            st.info(f"**Prompt:**\n{data['prompt']}")
            st.caption(f"**Aspek Rasio:** {data['ratio']}")
            
            # Tombol download untuk foto di riwayat
            st.download_button(
                label="💾 Download Again",
                data=data['content'],
                file_name=f"{st.session_state.current_photo_id.replace(' ', '_').lower()}.webp",
                mime="image/webp",
                use_container_width=True
            )
