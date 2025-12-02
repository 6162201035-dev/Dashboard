# =====================================
# 🕸️ ASSOCIATED AREA TRAFFIC ANALYSIS (TREEMAP ONLY)
# =====================================
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os       
import requests 
from datetime import date 

# =========================
# ⚙️ CONFIG
# =========================

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Associated Area Analysis",
    page_icon="🕸️",
    layout="wide"
)

# --- Path & Nilai Tetap ---
DATA_FOLDER = "data"
ASSOCIATION_FILE = os.path.join(DATA_FOLDER, "area_association_export.xlsx") 

DEFAULT_USER_ID = "4748ef52-ccb6-4dbe-acf4-1268d25123d8"
DEFAULT_SITE_CODE = "P00077"

# =========================
#  FUNGSI PENGAMBIL DATA
# =========================
def fetch_association_data(token, user_id, start_date_slash, end_date_slash, site_code):
    """Mengambil data Area Association (File Excel)"""
    st.write("Mengambil Data Area Association...")
    
    data_api_url = 'https://winnertech.hk:8090/api/en-us/shopRelationController/ShopAreaRelationExportData'
    
    data_payload = {
        "lang": "en-us", "menuId": 3000202,
        "params": {
            "isClose": 0, "module": "BM00019S007", "dateType": "d",
            "beginDate": start_date_slash, "endDate": end_date_slash,
            "SiteTreeSelects": [
                {"source": "0", "type": "0", "code": site_code, "operators": []}
            ]
        }, "userId": user_id
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
            with open(ASSOCIATION_FILE, 'wb') as f:
                f.write(response.content)
            st.success(f"Sukses: File Asosiasi ({ASSOCIATION_FILE}) disimpan.")
            return True
        else:
            st.error(f"Gagal: Server tidak mengembalikan file. Respons:\n{response.json()}")
            return False
    except Exception as e:
        st.error(f"KRITIS: Error saat mengambil Data Asosiasi: {e}")
        return False

# =========================
# 📂 FUNGSI PEMUAT DATA
# =========================
@st.cache_data
def load_data():
    """Membaca file Excel yang sudah di-download"""
    try:
        df = pd.read_excel(ASSOCIATION_FILE)
    except FileNotFoundError:
        return f"File '{ASSOCIATION_FILE}' tidak ditemukan."
    except Exception as e:
        return f"Gagal membaca file '{ASSOCIATION_FILE}'. Error: {e}"

    df.columns = [c.strip().title() for c in df.columns]
    
    # !! PENTING: Ganti nama 'NamaAsliDiExcel' dengan nama kolom
    # yang benar dari file Excel Anda
    rename_map = {
        "Store Area": "Store area",       # Ganti "NamaAsliDiExcel"
        "Associated Area": "Associated area", # Ganti "NamaAsliDiExcel"
        "Shared Traffic": "Shared traffic"    # Ganti "NamaAsliDiExcel"
    }
    existing_cols_to_rename = {k: v for k, v in rename_map.items() if k in df.columns}
    df.rename(columns=existing_cols_to_rename, inplace=True)

    if "Store area" not in df.columns or "Associated area" not in df.columns or "Shared traffic" not in df.columns:
        st.error("Gagal memproses file Excel. Nama kolom tidak sesuai.")
        st.info("Nama kolom yang diharapkan: 'Store area', 'Associated area', 'Shared traffic'")
        st.dataframe(df.head()) 
        return None 

    df["Shared traffic"] = pd.to_numeric(df["Shared traffic"], errors="coerce").fillna(0)
    return df

# =========================
# 🚀 FUNGSI UTAMA (MAIN)
# =========================
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

        if st.button("🚀 Kumpulkan Data Asosiasi", type="primary", use_container_width=True):
            start_date_slash = st.session_state.start_date.strftime("%Y/%m/%d")
            end_date_slash = st.session_state.end_date.strftime("%Y/%m/%d")
            
            with st.spinner("Mengambil data..."):
                os.makedirs(DATA_FOLDER, exist_ok=True)
                res1 = fetch_association_data(
                    st.session_state.token, DEFAULT_USER_ID, 
                    start_date_slash, end_date_slash, DEFAULT_SITE_CODE
                )
            
            if res1:
                st.success("Data asosiasi berhasil diambil!")
                st.cache_data.clear() # Hapus cache agar data baru dibaca
                st.rerun()
            else:
                st.error("Pengambilan data asosiasi gagal.")
        
        st.markdown("---")
        if st.button("🔄 Muat Ulang Data (Refresh)", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # --- 2. TAMPILKAN DASHBOARD ---
    
    # --- PERUBAHAN JUDUL DI SINI ---
    st.markdown('<div style="text-align:center; font-size:2.6rem; font-weight:700; margin-bottom:1.2rem;">🕸️ Associated Area Traffic Analysis</div>', unsafe_allow_html=True)
    st.markdown("Analisis hubungan antar area berdasarkan shared traffic pengunjung.")

    if not os.path.exists(ASSOCIATION_FILE):
        st.info("👋 Selamat datang! Data asosiasi tidak ditemukan. Silakan isi parameter di sidebar kiri dan klik 'Kumpulkan Data' untuk memulai.")
        st.stop()
        
    df_assoc = load_data() 
    
    if isinstance(df_assoc, str): 
        st.error(df_assoc)
        st.stop()
    if df_assoc is None: 
        st.error("Validasi kolom gagal. Cek nama kolom di file Excel dan 'rename_map' di kode.")
        st.stop()

    # --- 3. KALKULASI METRIK (DATA UNTUK TREEMAP) ---
    
    if not df_assoc.empty:
        total_shared_traffic = df_assoc["Shared traffic"].sum()
        traffic_from_store = df_assoc.groupby("Store area")["Shared traffic"].sum()
        prob_store = traffic_from_store / total_shared_traffic
        traffic_to_associated = df_assoc.groupby("Associated area")["Shared traffic"].sum()
        prob_associated = traffic_to_associated / total_shared_traffic
        
        df_metrics = df_assoc.copy()
        df_metrics["P(A)"] = df_metrics["Store area"].map(prob_store)
        df_metrics["P(B)"] = df_metrics["Associated area"].map(prob_associated)
        df_metrics["Support"] = df_metrics["Shared traffic"] / total_shared_traffic 
        df_metrics["Confident"] = df_metrics["Support"] / df_metrics["P(A)"]
        df_metrics["Lift"] = df_metrics["Confident"] / df_metrics["P(B)"]
        df_metrics.replace([np.inf, -np.inf], np.nan, inplace=True)
        df_metrics.fillna(0, inplace=True)
        
        # DataFrame final untuk Treemap
        df_results = df_metrics[[
            "Store area", "Associated area", "Shared traffic", 
            "Support", "Confident", "Lift"
        ]].copy()
        df_results_sorted = df_results.sort_values("Lift", ascending=False)
    
    else:
        st.warning("Data asosiasi kosong. Tidak ada yang bisa ditampilkan.")
        st.stop()


    # --- 4. TAMPILKAN TREEMAP (SATU-SATUNYA VISUALISASI) ---
    with st.container(border=True):
        st.subheader("🌳 Treemap Metrik Asosiasi")
        
        # Dropdown untuk memilih metrik
        metric_choice = st.selectbox(
            "Pilih Metrik untuk Ukuran Treemap:",
            ['Shared traffic', 'Lift', 'Confident', 'Support']
        )
        
        # Filter data (treemap tidak suka nilai 0 atau negatif)
        df_treemap = df_results_sorted[df_results_sorted[metric_choice] > 0.00001].copy()
        
        if df_treemap.empty:
            st.warning(f"Tidak ada data untuk ditampilkan dengan metrik '{metric_choice}' > 0.")
        else:
            df_treemap["Root"] = "Semua Relasi" 
            
            fig_tree = px.treemap(
                df_treemap,
                path=['Root', 'Store area', 'Associated area'],
                values=metric_choice, # Ukuran kotak
                color=metric_choice,  # Warna kotak
                color_continuous_scale='YlOrRd',
                title=f"Treemap Hubungan Area Berdasarkan '{metric_choice}'"
            )
            # Menampilkan nilai metrik di dalam kotak
            fig_tree.update_traces(
                textinfo="label+value",
                root_color="rgba(0,0,0,0)"
            )
            fig_tree.update_layout(height=700)
            st.plotly_chart(fig_tree, use_container_width=True)

    # Menampilkan data mentah di bawah (opsional, tapi berguna)
    with st.expander("Lihat Data Mentah yang Telah Diproses (Metrics)"):
        st.dataframe(df_results_sorted, use_container_width=True)

    st.caption("© 2025 Associated Area Analytics")


# --- Jalankan Fungsi Utama ---
if __name__ == "__main__":
    main()

