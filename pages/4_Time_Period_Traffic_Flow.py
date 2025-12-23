# ==========================================
# ⏳ TIME PERIOD TRAFFIC FLOW (AI INTEGRATED)
# ==========================================
import streamlit as st
import pandas as pd
import plotly.express as px
import os       
import requests    
from datetime import date

# --- 1. IMPORT MODULE AI (Baris ini yang baru) ---
import sys
sys.path.append('.') 
import ai_utils 

# ==============================
# ⚙️ CONFIG
# ==============================
st.set_page_config(
    page_title="Time Period Traffic Analysis",
    page_icon="⏳",
    layout="wide"
)

DATA_FOLDER = "data"
TRAFFIC_FILE = os.path.join(DATA_FOLDER, "time_traffic_flow.xlsx") 
DEFAULT_USER_ID = "4748ef52-ccb6-4dbe-acf4-1268d25123d8"
DEFAULT_SITE_CODE = "P00077"

# ==============================
# 📥 FUNGSI PENGAMBIL DATA (STANDAR)
# ==============================
def fetch_traffic_flow_data(token, user_id, start_date_slash, end_date_slash, site_code):
    st.write("Mengambil Data Time Traffic Flow...")
    # Endpoint API standar untuk Time Period
    data_api_url = 'https://winnertech.hk:8090/api/en-us/passengerFlow/PassengerFlowTimePeriodExportData'
    
    data_payload = {
        "userId": user_id, "lang": "en-us", "menuId": 3000103,
        "params": {
            "isClose": 0, "module": "BM00019S007", "dateType": "d",
            "beginDate": start_date_slash, "endDate": end_date_slash,
            "siteKey": site_code,
            "timePeriod": 60 # Default interval 60 menit (per jam)
        }
    }
    data_headers = {
        'Accept': 'application/json, text/plain, */*', 'Authorization': token,
        'Content-Type': 'application/json', 'Origin': 'https.winnertech.hk:8090',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
    }
    try:
        response = requests.post(data_api_url, headers=data_headers, json=data_payload, timeout=30)
        response.raise_for_status()
        if response.content and response.headers.get('Content-Type') != 'application/json':
            with open(TRAFFIC_FILE, 'wb') as f:
                f.write(response.content)
            st.success(f"Sukses: File Traffic Flow ({TRAFFIC_FILE}) disimpan.")
            return True
        else:
            st.error(f"Gagal: Server tidak mengembalikan file Excel. Respons:\n{response.json()}")
            return False
    except Exception as e:
        st.error(f"KRITIS: Error saat mengambil Data: {e}")
        return False

# ==============================
# 📂 LOAD DATA (STANDAR)
# ==============================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(TRAFFIC_FILE)
    except FileNotFoundError:
        return f"File '{TRAFFIC_FILE}' tidak ditemukan."
    except Exception as e:
        return f"Gagal membaca file. Error: {e}"

    # Bersihkan nama kolom
    df.columns = [c.strip() for c in df.columns]
    
    # Mapping nama kolom agar seragam
    # Menangani variasi nama kolom dari API (Entering/Enter/Masuk)
    rename_map = {
        "Time": "Jam", "Time Period": "Jam",
        "Enter": "Masuk", "Entering": "Masuk",
        "Exit": "Keluar", "Exiting": "Keluar",
        "Staff": "Staff"
    }
    existing_cols_to_rename = {k: v for k, v in rename_map.items() if k in df.columns}
    df.rename(columns=existing_cols_to_rename, inplace=True)
    
    # Pastikan data numerik
    for col in ["Masuk", "Keluar"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

# ==========================================
# 🧠 FUNGSI AI: PERINGKAS DATA (INI KODE BARU)
# ==========================================
def generate_traffic_summary(df):
    """
    Fungsi ini khusus untuk membaca DataFrame dan membuat teks ringkasan untuk AI.
    Tidak mengubah data asli.
    """
    if df.empty: return "Data Trafik Kosong."
    
    # Deteksi kolom 'Masuk' dan 'Jam' secara dinamis
    col_masuk = next((c for c in df.columns if c in ['Masuk', 'Enter', 'Entering']), None)
    col_jam = next((c for c in df.columns if c in ['Jam', 'Time', 'Time Period']), df.columns[0])
    
    if not col_masuk: return "Kolom data masuk tidak ditemukan."

    total_masuk = df[col_masuk].sum()
    avg_traffic = df[col_masuk].mean()
    
    # Cari Peak Hour (Jam Paling Ramai)
    peak_idx = df[col_masuk].idxmax()
    peak_time = df.loc[peak_idx, col_jam]
    peak_val = df.loc[peak_idx, col_masuk]

    # Cari Low Hour (Jam Sepi selain 0)
    df_active = df[df[col_masuk] > 0]
    if not df_active.empty:
        low_idx = df_active[col_masuk].idxmin()
        low_time = df_active.loc[low_idx, col_jam]
        low_val = df_active.loc[low_idx, col_masuk]
    else:
        low_time = "N/A"
        low_val = 0

    # Teks prompt untuk AI
    summary = f"""
    DATA TRAFIK BERDASARKAN WAKTU (HOURLY TRAFFIC):
    
    STATISTIK UTAMA:
    - Total Pengunjung Hari Ini: {total_masuk}
    - Rata-rata Pengunjung per Jam: {avg_traffic:.1f}
    
    JAM SIBUK (PEAK HOUR):
    - Waktu: {peak_time}
    - Jumlah: {peak_val} orang
    (Ini adalah beban tertinggi toko hari ini).
    
    JAM SEPI (LOW HOUR):
    - Waktu: {low_time}
    - Jumlah: {low_val} orang
    
    TUGAS AI:
    Berikan analisis operasional. 
    1. Kapan staff harus siaga penuh (Full Shift)?
    2. Kapan waktu terbaik untuk istirahat bergantian atau cleaning/restocking?
    3. Jika ada lonjakan drastis, apa penyebab potensialnya?
    """
    return summary

# ==============================
# 🚀 MAIN DASHBOARD
# ==============================
def main():
    
    # --- 1. SIDEBAR INPUT (Standar seperti Page 2) ---
    with st.sidebar:
        st.header("⚙️ Kontrol Pengambilan Data")
        if 'token' not in st.session_state: st.session_state.token = "Bearer ey..."
        if 'start_date' not in st.session_state: st.session_state.start_date = date.today()
        if 'end_date' not in st.session_state: st.session_state.end_date = date.today() # Ditambahkan biar aman
        
        st.session_state.token = st.text_input("Authorization Token", value=st.session_state.token, type="password")
        # Time Period Flow biasanya per hari, tapi kita kasih range biar fleksibel
        st.session_state.start_date = st.date_input("Start Date", value=st.session_state.start_date)
        st.session_state.end_date = st.date_input("End Date", value=st.session_state.end_date)
        st.markdown("---")

        if st.button("🚀 Kumpulkan Data Trafik", type="primary", use_container_width=True):
            start_slash = st.session_state.start_date.strftime("%Y/%m/%d")
            end_slash = st.session_state.end_date.strftime("%Y/%m/%d")
            with st.spinner("Loading Time Flow Data..."):
                os.makedirs(DATA_FOLDER, exist_ok=True)
                res = fetch_traffic_flow_data(st.session_state.token, DEFAULT_USER_ID, start_slash, end_slash, DEFAULT_SITE_CODE)
            if res:
                st.success("Data berhasil diambil!")
                st.cache_data.clear()
                st.rerun()

    st.markdown('<div style="text-align:center; font-size:2.6rem; font-weight:700; margin-bottom:1.2rem;">⏳ Time Period Traffic Flow</div>', unsafe_allow_html=True)
    st.caption(f"Analisis detail pergerakan pengunjung berdasarkan waktu.")

    if not os.path.exists(TRAFFIC_FILE):
        st.info("Data belum tersedia. Silakan 'Kumpulkan Data Trafik' di sidebar.")
        st.stop()
        
    df = load_data()
    if isinstance(df, str):
        st.error(df)
        st.stop()
    
    if df.empty:
        st.warning("Data kosong. Cek rentang tanggal.")
        st.stop()

    # --- 2. TAMPILAN GRAFIK (STANDAR) ---
    
    # Metrik Atas
    col1, col2, col3 = st.columns(3)
    masuk_col = next((c for c in df.columns if c in ['Masuk', 'Entering']), None)
    
    if masuk_col:
        col1.metric("Total Masuk", f"{df[masuk_col].sum():,}")
        col2.metric("Peak Hour", f"{df[masuk_col].max():,} org")
        col3.metric("Rata-rata/Jam", f"{df[masuk_col].mean():.0f} org")
        
        # Grafik Garis
        st.subheader("📈 Tren Pengunjung")
        jam_col = next((c for c in df.columns if c in ['Jam', 'Time']), df.columns[0])
        df[jam_col] = df[jam_col].astype(str) # Agar urutan jam tidak berantakan
        
        fig_line = px.line(df, x=jam_col, y=masuk_col, markers=True, title="Traffic Flow per Jam")
        st.plotly_chart(fig_line, use_container_width=True)
    
    with st.expander("Lihat Data Tabel"):
        st.dataframe(df, use_container_width=True)

    # ==========================================
    # ✨ 3. IMPLEMENTASI AI (DITAMBAHKAN DI BAWAH)
    # ==========================================
    st.markdown("---")
    with st.expander("✨ Tanya AI tentang Pola Jam Sibuk", expanded=False):
        c_ai1, c_ai2 = st.columns([3, 1])
        with c_ai1:
            q_options = [
                "Analisis jam sibuk dan berikan saran penjadwalan shift staff.",
                "Kapan waktu terbaik untuk melakukan restocking/cleaning?",
                "Apakah ada pola anomali yang mencurigakan?",
                "Tulis pertanyaan sendiri..."
            ]
            selected_q = st.selectbox("Pilih Pertanyaan:", q_options)
            if selected_q == "Tulis pertanyaan sendiri...":
                user_q = st.text_input("Ketik pertanyaanmu:", "Jelaskan tren trafik hari ini.")
            else:
                user_q = selected_q
        
        with c_ai2:
            st.write("") 
            st.write("")
            if st.button("Analisa Waktu 🤖", type="primary", use_container_width=True):
                if 'df' in locals() and not df.empty:
                    with st.spinner("AI sedang menganalisis pola waktu..."):
                        # Panggil fungsi ringkas data
                        summary_text = generate_traffic_summary(df)
                        # Kirim ke Gemini
                        jawaban = ai_utils.analyze_with_gemini(summary_text, user_q)
                        
                        st.markdown("### 💡 Insight Operasional:")
                        st.markdown(jawaban)
                else:
                    st.error("Dataframe tidak ditemukan.")

if __name__ == "__main__":
    main()
