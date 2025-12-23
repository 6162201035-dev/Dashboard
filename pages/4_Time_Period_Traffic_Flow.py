# ==========================================
# ⏳ TIME PERIOD TRAFFIC FLOW (AI INTEGRATED)
# ==========================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os       
import requests    
from datetime import date, datetime

# --- IMPORT MODULE AI ---
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
# 📥 FUNGSI PENGAMBIL DATA
# ==============================
def fetch_traffic_flow_data(token, user_id, start_date_slash, end_date_slash, site_code):
    st.write("Mengambil Data Time Traffic Flow...")
    # URL API (Disesuaikan dengan pola sebelumnya, pastikan endpoint ini benar/valid)
    data_api_url = 'https://winnertech.hk:8090/api/en-us/passengerFlow/PassengerFlowTimePeriodExportData'
    
    data_payload = {
        "userId": user_id, "lang": "en-us", "menuId": 3000103,
        "params": {
            "isClose": 0, "module": "BM00019S007", "dateType": "d",
            "beginDate": start_date_slash, "endDate": end_date_slash,
            "siteKey": site_code,
            "timePeriod": 60 # Default interval 60 menit
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
# 📂 LOAD DATA
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
    
    # Standarisasi nama kolom (sesuaikan dengan output Excel asli)
    # Biasanya: 'Time', 'Entering', 'Exiting', 'Passing', 'Return'
    rename_map = {
        "Time": "Jam",
        "Time Period": "Jam",
        "Enter": "Masuk",
        "Entering": "Masuk",
        "Exit": "Keluar",
        "Exiting": "Keluar",
        "Staff": "Staff"
    }
    existing_cols_to_rename = {k: v for k, v in rename_map.items() if k in df.columns}
    df.rename(columns=existing_cols_to_rename, inplace=True)
    
    if "Masuk" not in df.columns:
        return "Kolom 'Masuk' (Entering) tidak ditemukan di Excel."

    # Pastikan data numerik
    for col in ["Masuk", "Keluar"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

# ==========================================
# 🧠 FUNGSI PERINGKAS DATA UNTUK AI (TIME SERIES)
# ==========================================
def generate_traffic_summary(df):
    """
    Menganalisis pola waktu: Peak Hour, Low Hour, dan Tren.
    """
    if df.empty: return "Data Trafik Kosong."
    
    total_masuk = df["Masuk"].sum()
    total_keluar = df.get("Keluar", pd.Series([0]*len(df))).sum()
    
    # Cari Peak Hour (Jam Tersibuk)
    peak_row = df.loc[df["Masuk"].idxmax()]
    peak_time = peak_row.get("Jam", "N/A")
    peak_val = peak_row["Masuk"]
    
    # Cari Low Hour (Jam Tersepi - abaikan 0 jika toko tutup)
    df_active = df[df["Masuk"] > 0]
    if not df_active.empty:
        low_row = df_active.loc[df_active["Masuk"].idxmin()]
        low_time = low_row.get("Jam", "N/A")
        low_val = low_row["Masuk"]
    else:
        low_time = "N/A"
        low_val = 0
        
    # Hitung Rata-rata
    avg_traffic = df["Masuk"].mean()

    summary_text = f"""
    ANALISIS TRAFIK BERDASARKAN WAKTU (TIME FLOW):
    
    1. RINGKASAN TOTAL:
    - Total Pengunjung Masuk: {total_masuk}
    - Total Pengunjung Keluar: {total_keluar}
    - Rata-rata Pengunjung per Jam/Periode: {avg_traffic:.1f}
    
    2. JAM TERSIBUK (PEAK HOUR):
    - Pukul/Periode: {peak_time}
    - Jumlah Pengunjung: {peak_val} orang
    (Pada jam ini, toko mengalami beban tertinggi. Potensi antrean panjang.)
    
    3. JAM TERSEPI (LOW HOUR):
    - Pukul/Periode: {low_time}
    - Jumlah Pengunjung: {low_val} orang
    
    TUGAS AI:
    Analisis pola ini untuk efisiensi operasional. 
    Kapan staff harus siaga penuh (shift padat)? 
    Kapan waktu terbaik untuk melakukan restocking barang atau cleaning agar tidak mengganggu pengunjung?
    """
    return summary_text

# ==============================
# 🚀 MAIN DASHBOARD
# ==============================
def main():
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Filter Data")
        if 'token' not in st.session_state: st.session_state.token = "Bearer ey..."
        if 'start_date' not in st.session_state: st.session_state.start_date = date.today()
        
        st.session_state.token = st.text_input("Authorization Token", value=st.session_state.token, type="password")
        st.session_state.start_date = st.date_input("Tanggal Analisis", value=st.session_state.start_date)
        # Note: Time Flow biasanya harian, jadi start=end untuk melihat detail jam
        
        if st.button("🚀 Ambil Data Trafik", type="primary"):
            date_slash = st.session_state.start_date.strftime("%Y/%m/%d")
            with st.spinner("Loading Time Flow Data..."):
                os.makedirs(DATA_FOLDER, exist_ok=True)
                # Ambil data untuk 1 hari yang sama agar dapat detail per jam
                fetch_traffic_flow_data(st.session_state.token, DEFAULT_USER_ID, date_slash, date_slash, DEFAULT_SITE_CODE)
                st.rerun()

    st.markdown('<div style="text-align:center; font-size:2.6rem; font-weight:700; margin-bottom:1.2rem;">⏳ Time Period Traffic Flow</div>', unsafe_allow_html=True)
    st.caption(f"Analisis detail pergerakan pengunjung per jam pada tanggal: {st.session_state.start_date}")

    if not os.path.exists(TRAFFIC_FILE):
        st.info("Data belum tersedia. Klik tombol di sidebar.")
        st.stop()
        
    df = load_data()
    if isinstance(df, str):
        st.error(df)
        st.stop()

    # --- 1. METRIK UTAMA ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Masuk", f"{df['Masuk'].sum():,}")
    if "Keluar" in df.columns:
        col2.metric("Total Keluar", f"{df['Keluar'].sum():,}")
    col3.metric("Peak Hour Traffic", f"{df['Masuk'].max():,} org")

    # --- 2. FITUR AI ANALYST ---
    st.markdown("---")
    with st.expander("✨ Tanya AI tentang Jadwal & Pola Jam Sibuk", expanded=False):
        c_ai1, c_ai2 = st.columns([3, 1])
        with c_ai1:
            q_options = [
                "Berdasarkan data, kapan shift karyawan harus paling banyak?",
                "Apakah ada pola aneh (anomali) pada jam tertentu?",
                "Kapan waktu terbaik untuk maintenance/cleaning?",
                "Tulis pertanyaan sendiri..."
            ]
            selected_q = st.selectbox("Pilih Pertanyaan:", q_options)
            user_q = st.text_input("Ketik pertanyaanmu:", "Jelaskan tren trafik hari ini.") if selected_q == "Tulis pertanyaan sendiri..." else selected_q
        
        with c_ai2:
            st.write("") 
            st.write("")
            if st.button("Analisa Waktu 🤖", type="primary", use_container_width=True):
                with st.spinner("AI sedang membaca jam sibuk..."):
                    summary = generate_traffic_summary(df)
                    jawaban = ai_utils.analyze_with_gemini(summary, user_q)
                    st.markdown("### 💡 Insight Operasional:")
                    st.markdown(jawaban)
    st.markdown("---")

    # --- 3. VISUALISASI ---
    # A. Line Chart Trend
    st.subheader("📈 Tren Pengunjung per Jam")
    
    # Pastikan kolom jam string agar urutannya benar di chart
    df['Jam'] = df['Jam'].astype(str)
    
    fig_line = px.line(df, x='Jam', y=['Masuk', 'Keluar'] if 'Keluar' in df.columns else ['Masuk'],
                       markers=True, title="Fluktuasi Pengunjung Sepanjang Hari",
                       color_discrete_map={"Masuk": "#00CC96", "Keluar": "#EF553B"})
    fig_line.update_layout(xaxis_title="Jam / Periode", yaxis_title="Jumlah Orang", hovermode="x unified")
    
    # Highlight Peak Hour di Chart
    peak_val = df['Masuk'].max()
    peak_time = df.loc[df['Masuk'].idxmax(), 'Jam']
    fig_line.add_annotation(x=peak_time, y=peak_val, text="Peak Hour 🚩", showarrow=True, arrowhead=1)
    
    st.plotly_chart(fig_line, use_container_width=True)

    # B. Heatmap Intensity (Jika data mendukung, kita buat visualisasi bar warna-warni)
    st.subheader("🔥 Intensitas Trafik")
    fig_bar = px.bar(df, x='Jam', y='Masuk', color='Masuk', 
                     color_continuous_scale='Reds', title="Heatmap Intensitas Keramaian")
    st.plotly_chart(fig_bar, use_container_width=True)

    with st.expander("Lihat Data Tabel"):
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
