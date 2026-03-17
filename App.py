import streamlit as st
import requests
import time
import google.generativeai as genai

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI Creative Studio", page_icon="🎬", layout="wide")

# --- KONFIGURASI API (Secrets) ---
try:
    # Simpan key ini di Streamlit Cloud Secrets atau .streamlit/secrets.toml
    STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]
    LUMA_API_KEY = st.secrets["LUMA_API_KEY"]
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"]) # Untuk auto-title & deskripsi
except Exception:
    st.error("API Keys (Stability, Luma, Gemini) belum terpasang di Secrets!")
    st.stop()

model_gemini = genai.GenerativeModel("gemini-2.5-flash")

# --- SISTEM PENYIMPANAN SESSION ---
if "all_projects" not in st.session_state:
    st.session_state.all_projects = {} 

if "current_project_id" not in st.session_state:
    st.session_state.current_project_id = None

# --- FUNGSI PEMBANTU ---
def generate_project_title(prompt):
    try:
        response = model_gemini.generate_content(f"Buat judul singkat (max 3 kata) untuk project visual ini: {prompt}")
        return response.text.strip()
    except:
        return "Project Baru"

# --- SIDEBAR: RIWAYAT GENERASI ---
with st.sidebar:
    st.title("🎨 My Creations")
    if st.button("+ Project Baru", use_container_width=True):
        st.session_state.current_project_id = None
        st.rerun()

    st.write("---")
    for proj_id in list(st.session_state.all_projects.keys()):
        if st.button(f"🚀 {proj_id}", key=proj_id, use_container_width=True):
            st.session_state.current_project_id = proj_id
            st.rerun()

# --- TAMPILAN UTAMA ---
st.title("🎬 AI Image & Video Studio")
st.markdown("Hasilkan konten visual berkualitas tinggi menggunakan **Stability AI Ultra** & **Luma Dream Machine**.")

# Tab Selection
tab1, tab2 = st.tabs(["🖼️ Image Generator", "🎥 Video Generator"])

# --- LOGIKA GENERATE GAMBAR ---
with tab1:
    with st.form("img_form"):
        img_prompt = st.text_area("Deskripsikan Gambar:", placeholder="Contoh: Astronot menunggang kuda di bulan, gaya digital art...")
        ratio = st.selectbox("Aspek Rasio", ["1:1", "16:9", "9:16", "21:9"])
        submitted_img = st.form_submit_button("Generate Image")

    if submitted_img and img_prompt:
        project_name = generate_project_title(img_prompt)
        st.session_state.current_project_id = project_name
        
        with st.spinner("Sedang melukis..."):
            url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
            headers = {"authorization": f"Bearer {STABILITY_API_KEY}", "accept": "image/*"}
            files = {"none": ''}
            data = {"prompt": img_prompt, "output_format": "webp", "aspect_ratio": ratio}
            
            response = requests.post(url, headers=headers, files=files, data=data)
            
            if response.status_code == 200:
                img_data = response.content
                st.image(img_data, caption=project_name)
                # Simpan ke riwayat
                st.session_state.all_projects[project_name] = {"type": "image", "content": img_data, "prompt": img_prompt}
            else:
                st.error(f"Gagal: {response.json().get('errors')}")

# --- LOGIKA GENERATE VIDEO ---
with tab2:
    with st.form("vid_form"):
        vid_prompt = st.text_area("Deskripsikan Video:", placeholder="Contoh: Kamera bergerak cinematic mengikuti mobil sport di Tokyo...")
        submitted_vid = st.form_submit_button("Generate Video")

    if submitted_vid and vid_prompt:
        project_name = generate_project_title(vid_prompt)
        st.session_state.current_project_id = project_name
        
        with st.spinner("Luma sedang merender (1-2 menit)..."):
            # Request ke Luma AI API
            luma_url = "https://api.lumalabs.ai/dream-machine/v1/generations"
            headers = {"Authorization": f"Bearer {LUMA_API_KEY}", "Content-Type": "application/json"}
            payload = {"prompt": vid_prompt}
            
            res = requests.post(luma_url, headers=headers, json=payload)
            if res.status_code == 201:
                gen_id = res.json()['id']
                # Polling Status
                while True:
                    check = requests.get(f"{luma_url}/{gen_id}", headers=headers).json()
                    if check['state'] == "completed":
                        video_url = check['assets']['video']
                        st.video(video_url)
                        st.session_state.all_projects[project_name] = {"type": "video", "content": video_url, "prompt": vid_prompt}
                        break
                    elif check['state'] == "failed":
                        st.error("Generasi video gagal.")
                        break
                    time.sleep(10)
            else:
                st.error("API Video bermasalah.")

# --- TAMPILKAN PROJECT DARI RIWAYAT ---
if st.session_state.current_project_id in st.session_state.all_projects:
    data = st.session_state.all_projects[st.session_state.current_project_id]
    st.write("---")
    st.subheader(f"Detail Project: {st.session_state.current_project_id}")
    st.info(f"Prompt: {data['prompt']}")
    if data['type'] == "image":
        st.image(data['content'])
    else:
        st.video(data['content'])
