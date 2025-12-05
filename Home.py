# ================================
# 🏠 HOME PAGE (MAIN DASHBOARD)
# ================================
import streamlit as st
import pandas as pd
import os
import numpy as np

# --- Konfigurasi dasar halaman ---
st.set_page_config(
    page_title="Data Analysis Dashboard",
    page_icon="🏠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Tambahan ---
st.markdown("""
<style>
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        transition: all 0.3s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #FF4B4B !important;
        transform: translateY(-5px);
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI MENGHITUNG KPI DARI DATA LOKAL ---
def calculate_kpis():
    # Default Values (Jika data belum ditarik)
    kpi_data = {
        "total_visitors": "-",
        "busiest_area": "-",
        "peak_hour": "-",
        "avg_dwell": "-"
    }

    # Path File (Sesuai dengan modul-modul lain)
    DATA_FOLDER = "data"
    TRAFFIC_FILE = os.path.join(DATA_FOLDER, "time_period_traffic.xlsx")
    AREA_FILE = os.path.join(DATA_FOLDER, "area_traffic.xlsx")
    DWELL_FILE = os.path.join(DATA_FOLDER, "dwell_time_export.xlsx")

    # 1. Hitung Total Visitors & Peak Hour (Dari Time Period Traffic)
    if os.path.exists(TRAFFIC_FILE):
        try:
            df_t = pd.read_excel(TRAFFIC_FILE, header=0)
            df_t.columns = [c.strip() for c in df_t.columns] # Bersihkan spasi
            
            # Total Visitor
            if "Total" in df_t.columns:
                total_vis = df_t["Total"].sum()
                kpi_data["total_visitors"] = f"{int(total_vis):,}"
            
            # Peak Hour
            hour_cols = [c for c in df_t.columns if "~" in c] # Kolom jam misal 12:00~12:59
            if hour_cols:
                # Jumlahkan semua baris per kolom jam, cari yang max
                peak_col = df_t[hour_cols].sum().idxmax()
                kpi_data["peak_hour"] = peak_col.split("~")[0] # Ambil jam awal saja (misal 18:00)
        except:
            pass

    # 2. Hitung Busiest Area (Dari Area Traffic)
    if os.path.exists(AREA_FILE):
        try:
            df_a = pd.read_excel(AREA_FILE, sheet_name="Datas", header=0)
            # Pastikan nama kolom sesuai (kadang Excel header beda baris)
            # Kita cari kolom yang mengandung "Customer" atau "Site"
            col_map = {c: c.strip() for c in df_a.columns}
            df_a.rename(columns=col_map, inplace=True)
            
            # Cari kolom customer dan site
            cust_col = next((c for c in df_a.columns if "Customer" in c), None)
            site_col = next((c for c in df_a.columns if "Site" in c), None)

            if cust_col and site_col:
                df_a[cust_col] = pd.to_numeric(df_a[cust_col], errors='coerce').fillna(0)
                busiest = df_a.loc[df_a[cust_col].idxmax()]
                kpi_data["busiest_area"] = busiest[site_col]
        except:
            pass

    # 3. Hitung Avg Dwell Time (Dari Dwell Time Export)
    if os.path.exists(DWELL_FILE):
        try:
            df_d = pd.read_excel(DWELL_FILE, header=0)
            # Cari kolom Avg Dwell Time
            dwell_col = next((c for c in df_d.columns if "Avg" in c and "dwell" in c), None)
            
            if dwell_col:
                df_d[dwell_col] = pd.to_numeric(df_d[dwell_col], errors='coerce')
                avg_sec = df_d[dwell_col].mean()
                # Konversi detik ke menit
                avg_min = avg_sec / 60
                kpi_data["avg_dwell"] = f"{avg_min:.1f} Min"
        except:
            pass
            
    return kpi_data

# --- Load KPI ---
metrics = calculate_kpis()

# --- Judul halaman utama (Hero Section) ---
st.markdown('<div style="text-align:center; font-size:3rem; font-weight:800; margin-bottom:0.5rem;">AI Traffic Data Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; font-size:1.2rem; color:#888; margin-bottom:2rem;">Pusat kendali analisis data pengunjung, pola pergerakan, dan performa area secara real-time.</div>', unsafe_allow_html=True)

# --- 🚀 Executive Summary (KPI REAL) ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Total Visitors", value=metrics["total_visitors"], delta="Data Terkini")
with kpi2:
    st.metric(label="Busiest Area", value=metrics["busiest_area"], delta="High Traffic")
with kpi3:
    st.metric(label="Peak Hour", value=metrics["peak_hour"], delta="Jam Sibuk")
with kpi4:
    st.metric(label="Avg. Dwell Time", value=metrics["avg_dwell"], delta="Durasi")

st.markdown("---")

# --- Konten utama halaman Home (Menu Navigasi) ---
st.subheader("📂 Pilih Modul Analisis")

# Layout 5 Kolom
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    with st.container(border=True, height=380): 
        st.markdown("### 👥 Customer")
        st.markdown("Siapa yang datang? Analisis demografi, gender, usia, dan *dwell time*.")
        st.divider()
        st.page_link("pages/1_Customer_Profile.py", label="Buka Modul ➔", use_container_width=True)

with col2:
    with st.container(border=True, height=380):
        st.markdown("### 🔗 Relation")
        st.markdown("Bagaimana pergerakannya? Analisis korelasi antar area.")
        st.divider()
        st.page_link("pages/2_Associated_Area.py", label="Buka Modul ➔", use_container_width=True) 

with col3:
    with st.container(border=True, height=380):
        st.markdown("### 🏬 Potency")
        st.markdown("Area mana yang potensial? Analisis konversi pengunjung.")
        st.divider()
        st.page_link("pages/3_Area_Performance.py", label="Buka Modul ➔", use_container_width=True) 

with col4:
    with st.container(border=True, height=380):
        st.markdown("### ⏳ Period")
        st.markdown("Kapan waktu tersibuk? Tren trafik per jam & hari.")
        st.divider()
        st.page_link("pages/4_Time_Period_Traffic_Flow.py", label="Buka Modul ➔", use_container_width=True)
        
with col5:
    with st.container(border=True, height=380):
        st.markdown("### 🚦 Traffic")
        st.markdown("Berapa banyak yang lewat? Flow gabungan Gerbang & Area.")
        st.divider()
        st.page_link("pages/5_Area_Traffic_Gate_Flow.py", label="Buka Modul ➔", use_container_width=True)

st.markdown("---") 

# --- Footer ---
st.markdown("""
<div style="text-align:center; color:#666;">
    <small>© 2025 Data Analysis Dashboard | Dibentuk oleh N. | v1.0 Stable</small>
</div>
""", unsafe_allow_html=True)
