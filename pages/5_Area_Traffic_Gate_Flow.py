# =====================================
# 🚶‍♂️ TRAFFIC ANALYSIS DASHBOARD
# =====================================
import streamlit as st
import pandas as pd
import plotly.express as px
import os       
import requests 
from datetime import date 


# ==============================
# ⚙️ CONFIG
# ==============================

st.set_page_config(
    page_title="Traffic Flow Analysis", 
    page_icon="🚶‍♂️", 
    layout="wide"
)

# --- Path & Nilai Tetap ---
DATA_FOLDER = "data"
AREA_TRAFFIC_FILE = os.path.join(DATA_FOLDER, "area_traffic.xlsx")
GATE_FLOW_FILE = os.path.join(DATA_FOLDER, "gate_flow.xlsx")

DEFAULT_USER_ID = "4748ef52-ccb6-4dbe-acf4-1268d25123d8"
DEFAULT_SITE_CODE = "P00077"

# ==============================
# 📥 FUNGSI PENGAMBIL DATA (Tidak Berubah)
# ==============================

# --- FUNGSI 1: MENGAMBIL DATA AREA TRAFFIC (SelType 400) ---
def fetch_area_traffic(token, user_id, start_date_slash, end_date_slash, site_code):
    st.write("1/2: Mengambil Data Area Traffic...")
    data_api_url = 'https://winnertech.hk:8090/api/en-us/PassengerRank/AccRankExportDetailsAPI'
    data_payload = {
        "menuId": "3000102", "lang": "en-us", "userId": user_id,
        "params": {
            "SelType": "400", "Type": "d", "SiteKeys": site_code,
            "BeginTime": start_date_slash, "EndTime": end_date_slash,
            "Module": "BM00019S002", "IsClose": 0, "orderbyName": "inSum", "sortDesc": "desc"
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
            with open(AREA_TRAFFIC_FILE, 'wb') as f: f.write(response.content)
            st.success(f"Sukses (1/2): File Area Traffic ({AREA_TRAFFIC_FILE}) disimpan.")
            return True
        else:
            st.error(f"Gagal (1/2): Server tidak mengembalikan file Area Traffic. Respons:\n{response.json()}")
            return False
    except Exception as e:
        st.error(f"KRITIS (1/2): Error saat mengambil Data Area Traffic: {e}")
        return False

# --- FUNGSI 2: MENGAMBIL DATA GATE FLOW (SelType 700) ---
def fetch_gate_flow(token, user_id, start_date_slash, end_date_slash, site_code):
    st.write("2/2: Mengambil Data Gate Flow...")
    data_api_url = 'https://winnertech.hk:8090/api/en-us/PassengerRank/AccRankExportDetailsAPI'
    data_payload = {
        "menuId": "3000102", "lang": "en-us", "userId": user_id,
        "params": {
            "SelType": "700", "Type": "d", "SiteKeys": site_code,
            "BeginTime": start_date_slash, "EndTime": end_date_slash,
            "Module": "BM00019S002", "IsClose": 0, "orderbyName": "inSum", "sortDesc": "desc"
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
            with open(GATE_FLOW_FILE, 'wb') as f: f.write(response.content)
            st.success(f"Sukses (2/2): File Gate Flow ({GATE_FLOW_FILE}) disimpan.")
            return True
        else:
            st.error(f"Gagal (2/2): Server tidak mengembalikan file Gate Flow. Respons:\n{response.json()}")
            return False
    except Exception as e:
        st.error(f"KRITIS (2/2): Error saat mengambil Data Gate Flow: {e}")
        return False

# ==============================
# 📂 LOAD DATA (DIMODIFIKASI DENGAN RENAME MAP ANDA)
# ==============================
@st.cache_data
def load_data():
    """Membaca DUA file Excel yang sudah di-download"""
    try:
        df_traffic = pd.read_excel(AREA_TRAFFIC_FILE, sheet_name="Datas", header=0)
    except FileNotFoundError:
        return f"File '{AREA_TRAFFIC_FILE}' tidak ditemukan.", None
    except Exception as e:
        return f"Gagal membaca file '{AREA_TRAFFIC_FILE}'. Error: {e}", None
        
    try:
        df_flow = pd.read_excel(GATE_FLOW_FILE, sheet_name="Datas", header=0)
    except FileNotFoundError:
        return None, f"File '{GATE_FLOW_FILE}' tidak ditemukan."
    except Exception as e:
        return None, f"Gagal membaca file '{GATE_FLOW_FILE}'. Error: {e}"

    # --- Rename Map (BERDASARKAN INPUT ANDA) ---
    
    # Ini `rename_map` Anda untuk file traffic
    rename_map_traffic = {
        "Site": "Area",
        "Customer": "Customer",  
        "Flow (in)": "Flow(in)",
        "Flow  (out)": "Flow(out)", # Spasi ganda di key
        "Number of stores": "Number of stores"    
    }
    
    # Ini `rename_map` Anda untuk file flow, SAYA MODIFIKASI value-nya
    rename_map_flow = {
        "Site": "Gate",
        "Flow (in)": "Gate Flow(in)",  # <-- DIPERBAIKI (value)
        "Flow  (out)": "Gate Flow(out)", # <-- DIPERBAIKI (value)
        "Customer": "Customer",
        "Number of stores": "Number of stores"
    }
    
    # Terapkan rename
    df_traffic.rename(columns={k: v for k, v in rename_map_traffic.items() if k in df_traffic.columns}, inplace=True)
    df_flow.rename(columns={k: v for k, v in rename_map_flow.items() if k in df_flow.columns}, inplace=True)
    
    # Konversi Tanggal (File Anda tidak punya 'Date', jadi kita lewati ini)
        
    # Konversi Kolom Numerik
    cols_to_convert_traffic = ["Customer", "Flow(in)", "Flow(out)"]
    for col in cols_to_convert_traffic:
        if col in df_traffic.columns:
            df_traffic[col] = pd.to_numeric(df_traffic[col], errors='coerce').fillna(0)
            
    cols_to_convert_flow = ["Gate Flow(in)", "Gate Flow(out)", "Customer"]
    for col in cols_to_convert_flow:
        if col in df_flow.columns:
            df_flow[col] = pd.to_numeric(df_flow[col], errors='coerce').fillna(0)

    # Validasi (untuk debug)
    if 'Area' not in df_traffic.columns:
        st.error("Kolom 'Area' GAGAL dibuat. Cek `rename_map_traffic`.")
        st.dataframe(pd.DataFrame({'Kolom Asli': pd.read_excel(AREA_TRAFFIC_FILE, sheet_name="Datas", header=0).columns}))
    if 'Gate Flow(out)' not in df_flow.columns:
        st.error("Kolom 'Gate Flow(out)' GAGAL dibuat. Cek `rename_map_flow`.")
        st.dataframe(pd.DataFrame({'Kolom Asli': pd.read_excel(GATE_FLOW_FILE, sheet_name="Datas", header=0).columns}))

    return df_traffic, df_flow

# ===================================
# 🎁 FUNGSI UNTUK MEMBUNGKUS DASHBOARD (DIMODIFIKASI: 2 KOLOM)
# ===================================
def build_dashboard(df_traffic, df_flow):
    """
    Fungsi ini menganalisis data RINGKASAN dalam satu halaman.
    - Area Traffic: Fokus di 'Customer'
    - Gate Flow: Fokus di 'Flow In / Out'
    """
    
    # --- 1. KPI TOTAL (Tetap) ---
    st.subheader("🧭 Ringkasan KPI Total")
    total_customer = df_traffic['Customer'].sum()
    total_flow_in = df_flow['Gate Flow(in)'].sum()
    total_flow_out = df_flow['Gate Flow(out)'].sum()

    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric("Total Area Traffic (Customer)", f"{int(total_customer):,}")
    col_kpi2.metric("Total Gate Flow In", f"{int(total_flow_in):,}")
    col_kpi3.metric("Total Gate Flow Out", f"{int(total_flow_out):,}")
    
    st.markdown("---")

    # --- BUAT 2 KOLOM UTAMA DI SINI ---
    col1, col2 = st.columns(2)

    # =======================
    # BAGIAN 1: ANALISIS PER AREA (KOLOM KIRI)
    # =======================
    with col1:
        with st.container(border=True): # Dibungkus container agar rapi
            st.subheader("📊 Analisis per Area (Customer)")
            
            # Agregat per Area (HANYA CUSTOMER)
            area_agg = df_traffic.groupby("Area")["Customer"].sum().reset_index().sort_values(by="Customer", ascending=False)
            
            # Filter area dengan customer > 0
            area_agg = area_agg[area_agg['Customer'] > 0]
            
            if area_agg.empty:
                st.warning("Tidak ada data 'Customer' (dari 'Customer' atau 'AccNum') yang ditemukan di file Area Traffic.")
            else:
                st.markdown("#### Total Customer per Area")
                fig_area_cust = px.bar(
                    area_agg, x="Area", y="Customer",
                    color="Customer", color_continuous_scale="Blues",
                    title="Total Customer (AccNum) Berdasarkan Area"
                )
                st.plotly_chart(fig_area_cust, use_container_width=True)

    # =======================
    # BAGIAN 2: ANALISIS PER GATE (KOLOM KANAN)
    # =======================
    with col2:
        with st.container(border=True): # Dibungkus container agar rapi
            st.subheader("🚪 Analisis per Gate (Flow In/Out)")
            
            # Agregat per Gate (Flow In/Out)
            gate_agg = df_flow.groupby("Gate").agg(
                **{
                    "Gate Flow(in)": pd.NamedAgg(column="Gate Flow(in)", aggfunc="sum"),
                    "Gate Flow(out)": pd.NamedAgg(column="Gate Flow(out)", aggfunc="sum")
                }
            ).reset_index()
            
            if gate_agg.empty or ('Gate Flow(in)' not in gate_agg.columns):
                 st.warning("Tidak ada data 'Gate Flow' (dari 'Flow (in)' atau 'Flow  (out)') yang ditemukan di file Gate Flow.")
            else:
                gate_melted = gate_agg.melt(id_vars="Gate", value_vars=["Gate Flow(in)", "Gate Flow(out)"], var_name="Flow Type", value_name="Jumlah")

                fig_gate_flow = px.bar(
                    gate_melted, x="Gate", y="Jumlah",
                    color="Flow Type", barmode="group",
                    title="Total Flow In vs Flow Out Berdasarkan Gate"
                )
                st.plotly_chart(fig_gate_flow, use_container_width=True)
            
    # =======================
    # BAGIAN 3: DATA MENTAH (DI BAWAH, FULL WIDTH)
    # =======================
    st.markdown("---")
    with st.expander("Lihat Data Mentah"):
        st.markdown("#### Data Mentah Area Traffic")
        st.dataframe(df_traffic)
        st.markdown("#### Data Mentah Gate Flow")
        st.dataframe(df_flow)

# ==============================
# 🚀 MAIN (KONTROLER)
# ==============================
def main():
    
    # --- 1. SIDEBAR INPUT ---
    with st.sidebar:
        st.header("⚙️ Kontrol Pengambilan Data")
        
        if 'token' not in st.session_state: st.session_state.token = "Bearer ey..."
        if 'start_date' not in st.session_state: st.session_state.start_date = date.today()
        if 'end_date' not in st.session_state: st.session_state.end_date = date.today()

        st.session_state.token = st.text_input("1. Authorization Token", value=st.session_state.token, type="password")
        st.session_state.start_date = st.date_input("2. Tanggal Mulai", value=st.session_state.start_date)
        st.session_state.end_date = st.date_input("3. Tanggal Akhir", value=st.session_state.end_date)
        
        st.markdown("---")
        st.markdown(f"**UserID:** `{DEFAULT_USER_ID}`")
        st.markdown(f"**Site Code:** `{DEFAULT_SITE_CODE}`")
        st.markdown("---")

        if st.button("🚀 Kumpulkan Data Traffic Analysis", type="primary", use_container_width=True):
            
            # Format tanggal (YYYY/MM/DD) sesuai payload
            start_date_slash = st.session_state.start_date.strftime("%Y/%m/%d")
            end_date_slash = st.session_state.end_date.strftime("%Y/%m/%d")
            
            with st.spinner("Mengambil data..."):
                os.makedirs(DATA_FOLDER, exist_ok=True)
                res1 = fetch_area_traffic(
                    st.session_state.token, DEFAULT_USER_ID, 
                    start_date_slash, end_date_slash, DEFAULT_SITE_CODE
                )
                res2 = fetch_gate_flow(
                    st.session_state.token, DEFAULT_USER_ID, 
                    start_date_slash, end_date_slash, DEFAULT_SITE_CODE
                )
            
            if res1 and res2:
                st.success("Semua data (Area Traffic & Gate Flow) berhasil diambil!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Satu atau lebih pengambilan data gagal.")
        
        st.markdown("---")
        if st.button("🔄 Muat Ulang Data (Refresh)", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # --- 2. TAMPILKAN DASHBOARD ---
    st.markdown('<div style="text-align:center; font-size:2.6rem; font-weight:700; margin-bottom:1.2rem;">🚶‍♂️ Area Traffic & Gate Flow</div>', unsafe_allow_html=True)
    st.caption("Dashboard ini menganalisis pola pergerakan pengunjung berdasarkan data Flow In, Flow Out, dan Total Traffic.")

    file_check = [os.path.exists(AREA_TRAFFIC_FILE), os.path.exists(GATE_FLOW_FILE)]
    
    if not all(file_check):
        st.info("👋 Selamat datang! Data Traffic Analysis tidak ditemukan. Silakan isi parameter di sidebar kiri dan klik 'Kumpulkan Data' untuk memulai.")
        
        warning_message = "File yang hilang: \n"
        if not file_check[0]:
            warning_message += "• area_traffic.xlsx\n"
        if not file_check[1]:
            warning_message += "• gate_flow.xlsx"
            
        st.warning(warning_message)
        st.stop()
        
    df_traffic, df_flow = load_data() 
    
    if isinstance(df_traffic, str) or isinstance(df_flow, str): 
        if isinstance(df_traffic, str): st.error(df_traffic)
        if isinstance(df_flow, str): st.error(df_flow)
        st.stop()
    if df_traffic is None or df_flow is None:
        st.error("Gagal memvalidasi data atau data kosong.")
        st.stop()

    # Jika data berhasil di-load, jalankan visualisasi
    build_dashboard(df_traffic, df_flow)

# --- Jalankan Fungsi Utama ---
if __name__ == "__main__":
    main()
