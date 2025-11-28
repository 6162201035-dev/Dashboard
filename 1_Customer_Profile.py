import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
from datetime import date 

# -------------------------------------------------------------------
# KONFIGURASI UTAMA
# -------------------------------------------------------------------

# --- Konfigurasi Path Data ---
DATA_FOLDER = "data"
CUSTOMER_FILE = os.path.join(DATA_FOLDER, "customer_profile.csv")
WEATHER_FILE = os.path.join(DATA_FOLDER, "data_cuaca.csv")
DWELL_FILE = os.path.join(DATA_FOLDER, "dwell_time_export.xlsx")

# --- Konfigurasi API ---
VISUAL_CROSSING_API_KEY = "477QVYDNSEPM6BJ6YS7GG7THZ" # (Dari kode Anda)

# --- NILAI TETAP (HARD-CODED) ---
DEFAULT_USER_ID = "4748ef52-ccb6-4dbe-acf4-1268d25123d8"
DEFAULT_SITE_CODE = "P00077"
DEFAULT_LOKASI = "-6.931706738510438, 107.57600657226179"


# --- Konfigurasi Dashboard ---
st.set_page_config(page_title="Customer Profile Dashboard", page_icon="👥", layout="wide")

st.markdown("""
<style>
.block-space {margin-bottom: 40px;}
</style>
""", unsafe_allow_html=True)

ORDER_DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
AGE_GENDER_PAIRS = [
    ("Child(0~6 Age)", "one_Man", "one_Woman"),
    ("Young person(7~15 Age)", "two_Man", "two_Woman"),
    ("Teenager(16~35 Age)", "three_Man", "three_Woman"),
    ("Middle age(36~60 Age)", "four_Man", "four_Woman"),
    ("Senility(60< Age)", "five_Man", "five_Woman")
]
DWELL_COLS_RAW = ["Dwell_≤30s", "Dwell_31~60s", "Dwell_1~2min", "Dwell_2~5min", "Dwell_5~10min", "Dwell_>10min"]
BASE_COLOR_SEQ = px.colors.sequential.Blues
BASE_CONT_SCALE = "Blues"


# -------------------------------------------------------------------
# FUNGSI PENGAMBIL DATA (Tidak Berubah)
# -------------------------------------------------------------------
def fetch_customer_data(token, user_id, start_date_norm, end_date_norm, site_code):
    st.write("1/3: Mengambil Data Customer Profile...")
    data_api_url = 'https://winnertech.hk:8090/api/en-us/customerPortrait/getAgeAndSexDetail'
    data_payload = {
        "menuId": 3000401, "lang": "en-us",
        "params": {
            "isClose": 0, "module": "BM00019S002", "dateType": "d",
            "beginDate": start_date_norm, "endDate": end_date_norm,
            "SiteTreeSelects": [
                {"source": "0", "type": "0", "code": site_code, "operators": []}
            ],
            "childSite": "", "tabSiteType": 300, "page": 1, "pageSize": 500
        }, "userId": user_id
    }
    data_headers = {
        'Accept': 'application/json, text/plain, */*', 'Authorization': token,
        'Content-Type': 'application/json', 'Origin': 'https://winnertech.hk:8090',
        'Referer': 'https://winnertech.hk:8090/ReportsAnalysis/AccurateFlowS0600/customerPortrait/index.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0'
    }
    try:
        response = requests.post(data_api_url, headers=data_headers, json=data_payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        list_data_tabel = data.get('msg', {}).get('data', [])
        if list_data_tabel:
            df = pd.DataFrame(list_data_tabel)
            df.to_csv(CUSTOMER_FILE, index=False)
            st.success(f"Sukses (1/3): Customer Profile disimpan ({len(df)} baris).")
            return True
        else:
            st.error(f"Gagal (1/3): 'msg' atau 'data' tidak ditemukan di JSON Customer.\nRespons: {data}")
            return False
    except Exception as e:
        st.error(f"KRITIS (1/3): Error saat mengambil Customer Profile: {e}")
        return False

def fetch_dwell_data(token, user_id, start_date_slash, end_date_slash, site_code):
    st.write("2/3: Mengambil Data Dwell Time...")
    data_api_url = 'https://winnertech.hk:8090/api/en-us/SelfAccess/selfDataExport'
    data_payload = {
        "userId": user_id, "lang": "en-us", "menuId": "4000101",
        "params": {
            "isClose": 0, "Module": "BM00025,BM00001,BM00019S001,BM00019S002,BM00019",
            "accurateType": "1", "dateType": "d",
            "beginDate": start_date_slash, "endDate": end_date_slash,
            "SelType": 300, "siteChooseType": 0, "tabSiteType": "300",
            "indicator": "Accurate_Wander,Accurate_AvgWanderTime",
            "indicatorcolumnsData": [
                "Accurate_Wander|Distribution of customers'dwell time",
                "Accurate_AvgWanderTime|Avg. dwell time"
            ],
            "advancedOptionsData": [], "advancedOptions": "", "exportType": 1,
            "SiteTreeSelects": [
                {"source": "0", "type": "0", "code": site_code, "iscloseshop": "0", "operators": []}
            ]
        }
    }
    data_headers = {
        'Accept': 'application/json, text/plain, */*', 'Authorization': token,
        'Content-Type': 'application/json', 'Origin': 'https://winnertech.hk:8090',
        'Referer': 'https://winnertech.hk:8090/ReportsAnalysis/AccurateFlowS0600/selfAccess/index.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0'
    }
    try:
        response = requests.post(data_api_url, headers=data_headers, json=data_payload, timeout=30)
        response.raise_for_status()
        if response.content and response.headers.get('Content-Type') != 'application/json':
            with open(DWELL_FILE, 'wb') as f:
                f.write(response.content)
            st.success(f"Sukses (2/3): File Dwell Time (.xlsx) disimpan.")
            return True
        else:
            st.error(f"Gagal (2/3): Server tidak mengembalikan file Dwell Time.\nRespons: {response.json()}")
            return False
    except Exception as e:
        st.error(f"KRITIS (2/3): Error saat mengambil Dwell Time: {e}")
        return False

def fetch_weather_data(lokasi, start_date_norm, end_date_norm):
    st.write("3/3: Mengambil Data Cuaca...")
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{lokasi}/{start_date_norm}/{end_date_norm}"
        f"?key={VISUAL_CROSSING_API_KEY}&unitGroup=metric&include=days&contentType=json"
    )
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status() 
        data = response.json()
        if 'days' in data:
            df = pd.DataFrame(data['days'])
            df.to_csv(WEATHER_FILE, index=False)
            st.success(f"Sukses (3/3): Data Cuaca disimpan.")
            return True
        else:
            st.error(f"Gagal (3/3): 'days' tidak ditemukan di JSON Cuaca.\nRespons: {data}")
            return False
    except Exception as e:
        st.error(f"KRITIS (3/3): Error saat mengambil Data Cuaca: {e}")
        return False

# -------------------------------------------------------------------
# FUNGSI PEMUAT DATA (Tidak Berubah)
# -------------------------------------------------------------------

@st.cache_data
def load_customer_data():
    """Membaca customer_profile.csv dan data_cuaca.csv, lalu menggabungkannya."""
    try:
        df_cust = pd.read_csv(CUSTOMER_FILE)
    except FileNotFoundError:
        return f"File '{CUSTOMER_FILE}' tidak ditemukan."
    
    try:
        df_weather = pd.read_csv(WEATHER_FILE)
    except FileNotFoundError:
        return f"File '{WEATHER_FILE}' tidak ditemukan."

    df_cust.rename(columns={"countDate": "Date", "siteName": "Site"}, inplace=True)
    df_cust["Date"] = pd.to_datetime(df_cust["Date"], errors="coerce")
    man_cols = [col for pair in AGE_GENDER_PAIRS for col in [pair[1]] if col in df_cust.columns]
    woman_cols = [col for pair in AGE_GENDER_PAIRS for col in [pair[2]] if col in df_cust.columns]
    df_cust["Customer"] = df_cust[man_cols + woman_cols].sum(axis=1)
    for group, man_col, woman_col in AGE_GENDER_PAIRS:
        valid_cols = [c for c in [man_col, woman_col] if c in df_cust.columns]
        df_cust[group] = df_cust[valid_cols].sum(axis=1) if valid_cols else 0
    df_cust["Male_Total"] = df_cust[man_cols].sum(axis=1)
    df_cust["Female_Total"] = df_cust[woman_cols].sum(axis=1)
    df_weather.rename(columns={"datetime": "Date"}, inplace=True)
    df_weather["Date"] = pd.to_datetime(df_weather["Date"], errors="coerce")
    rename_map = {
        "conditions": "Weather", "temp": "Temperature", "tempmax": "Temp_Max",
        "tempmin": "Temp_Min", "humidity": "Humidity", "precip": "Precipitation"
    }
    df_weather.rename(columns=rename_map, inplace=True)
    weather_cols_to_merge = ["Date", "Weather", "Temperature", "Temp_Max", "Temp_Min", "Humidity", "Precipitation"]
    df_weather_subset = df_weather[[col for col in weather_cols_to_merge if col in df_weather.columns]]
    df_final = pd.merge(df_cust, df_weather_subset, on="Date", how="left")
    return df_final


@st.cache_data
def load_dwell_data():
    """Membaca dwell_time_export.xlsx."""
    try:
        df = pd.read_excel(DWELL_FILE, header=0)
    except FileNotFoundError:
        return f"File '{DWELL_FILE}' tidak ditemukan."
    except Exception as e:
        return f"Gagal membaca file Excel '{DWELL_FILE}'. Error: {e}"
        
    rename_map_dwell = {
        "Date": "Date", "Site": "Site",
        "Avg. dwell time": "Avg_dwell_time_sec",
        "≤30s": "Dwell_≤30s", "31~60s": "Dwell_31~60s",
        "1~2min": "Dwell_1~2min", "2~5min": "Dwell_2~5min",
        "5~10min": "Dwell_5~10min", ">10min": "Dwell_>10min"
    }
    existing_cols_to_rename = {k: v for k, v in rename_map_dwell.items() if k in df.columns}
    df.rename(columns=existing_cols_to_rename, inplace=True)
    if "Date" not in df.columns or "Site" not in df.columns:
        st.error(f"Gagal memproses '{DWELL_FILE}'. Kolom 'Date' atau 'Site' tidak ditemukan.")
        st.info("Cek nama kolom di file Excel dan perbarui 'rename_map_dwell' di kode.")
        st.dataframe(df.head())
        return None
    dwell = df.copy()
    dwell["Date"] = pd.to_datetime(dwell["Date"], errors="coerce")
    if "Avg_dwell_time_sec" in dwell.columns:
        dwell["Avg_dwell_time_sec"] = pd.to_numeric(dwell["Avg_dwell_time_sec"], errors="coerce")
        dwell["Avg_dwell_time_min"] = dwell["Avg_dwell_time_sec"] / 60
    dwell_cols = [c for c in DWELL_COLS_RAW if c in dwell.columns]
    for c in dwell_cols:
        dwell[c] = pd.to_numeric(dwell[c], errors="coerce").fillna(0)
    return dwell


# -------------------------------------------------------------------
# FUNGSI PROSES & PLOT (TIDAK BERUBAH)
# -------------------------------------------------------------------

def merge_data(df, dwell):
    if df is None or dwell is None: return None
    if "Date" in df.columns and "Site" in df.columns and "Date" in dwell.columns and "Site" in dwell.columns:
        return pd.merge(df, dwell, on=["Date", "Site"], how="left")
    st.error("Gagal menggabungkan data Customer & Dwell. Kolom 'Date'/'Site' mungkin tidak cocok.")
    return None

def feature_engineering(df):
    day_map = {0:"Senin",1:"Selasa",2:"Rabu",3:"Kamis",4:"Jumat",5:"Sabtu",6:"Minggu"}
    if "Date" in df.columns:
        df["DayOfWeek"] = df["Date"].dt.dayofweek.map(day_map)
        df["DayOfWeek"] = pd.Categorical(df["DayOfWeek"], categories=ORDER_DAYS, ordered=True)
    
    valid_dwell_cols = [c for c in DWELL_COLS_RAW if c in df.columns]
    if "Dwell_≤30s" in df.columns and "Dwell_>10min" in df.columns and len(valid_dwell_cols)>0:
        df["Total_Dwell_Counted"] = df[valid_dwell_cols].sum(axis=1)
        df["Bounce_Rate"] = 0.0
        df["Engagement_Rate"] = 0.0
        mask_total_gt_zero = df["Total_Dwell_Counted"] > 0
        df.loc[mask_total_gt_zero, "Bounce_Rate"] = (df["Dwell_≤30s"] / df["Total_Dwell_Counted"]) * 100
        df.loc[mask_total_gt_zero, "Engagement_Rate"] = (df["Dwell_>10min"] / df["Total_Dwell_Counted"]) * 100
        
    required_cols = ["Child(0~6 Age)", "Young person(7~15 Age)", "Teenager(16~35 Age)", "Middle age(36~60 Age)", "Customer"]
    if all(c in df.columns for c in required_cols):
        df["Family_Index"] = 0.0
        mask_cust_gt_zero = df["Customer"] > 0
        prop_child = (df["Child(0~6 Age)"] + df["Young person(7~15 Age)"]) / df["Customer"]
        prop_adult = (df["Teenager(16~35 Age)"] + df["Middle age(36~60 Age)"]) / df["Customer"]
        df.loc[mask_cust_gt_zero, "Family_Index"] = prop_child[mask_cust_gt_zero] * prop_adult[mask_cust_gt_zero]
        df["Family_Index"] = df["Family_Index"].fillna(0)
        max_idx = df["Family_Index"].max()
        if max_idx > 0:
            df["Family_Index"] = df["Family_Index"] / max_idx
    return df

def kpi_content(df):
    total_customer = int(df['Customer'].sum())
    total_site = df['Site'].nunique()
    actual_min_date = df['Date'].min()
    actual_max_date = df['Date'].max()
    min_str = actual_min_date.strftime("%d %b %y")
    max_str = actual_max_date.strftime("%d %b %y")
    date_range_str = min_str if min_str == max_str else f"{min_str} - {max_str}"
    return total_customer, total_site, date_range_str

def plot_age_gender(df):
    records=[]
    for day, group in df.groupby("DayOfWeek", observed=True):
        total_cust = group["Customer"].sum()
        if total_cust > 0:
            for age_label, man_col, woman_col in AGE_GENDER_PAIRS:
                if man_col in group.columns and woman_col in group.columns:
                    man_sum = group[man_col].sum()
                    woman_sum = group[woman_col].sum()
                    records.append({"DayOfWeek":day, "Age Group":age_label, "Gender":"Man", "Proportion":(man_sum/total_cust)*100})
                    records.append({"DayOfWeek":day, "Age Group":age_label, "Gender":"Woman", "Proportion":(woman_sum/total_cust)*100})
    ratio_df=pd.DataFrame(records)
    if not ratio_df.empty:
        ratio_df=ratio_df.sort_values("DayOfWeek")
        fig=px.bar(
            ratio_df, x="DayOfWeek", y="Proportion", color="Age Group",
            facet_col="Gender", barmode="stack", category_orders={"DayOfWeek":ORDER_DAYS},
            color_discrete_sequence=BASE_COLOR_SEQ,
            title="Proporsi (%) Pengunjung Berdasarkan Usia dan Gender per Hari"
        )
        fig.update_layout(yaxis_title="Proporsi (%)", title_x=0.05, paper_bgcolor='rgba(38, 41, 64, 0.99)', plot_bgcolor='rgba(38, 41, 64, 0.95)', font=dict(size=16, family="Arial"), margin=dict(l=18, r=18, t=48, b=18))
        fig.update_xaxes(title_text="Hari")
        return fig
    else: return None

def plot_family_index(df):
    if "Family_Index" in df.columns and "DayOfWeek" in df.columns:
        day_family = df.groupby("DayOfWeek", observed=True)["Family_Index"].mean().reset_index()
        fig = px.bar(day_family, x="DayOfWeek", y="Family_Index", text_auto=".2f", color="Family_Index", color_continuous_scale=BASE_CONT_SCALE, title="Rata-rata Family Index per Hari dalam Seminggu", category_orders={"DayOfWeek":ORDER_DAYS})
        fig.update_layout(yaxis_title="Rata-rata Family Index (0–1)", xaxis_title="Hari", paper_bgcolor='rgba(38, 41, 64, 0.99)', plot_bgcolor='rgba(38, 41, 64, 0.95)', font=dict(size=16, family="Arial"), margin=dict(l=18, r=18, t=48, b=18))
        return fig
    else: return None

# -------------------------------------------------------------------
# --- FUNGSI PLOT VS CUACA (INI YANG DIMODIFIKASI) ---
# -------------------------------------------------------------------

def plot_metric_vs_cuaca(df, metric_col, metric_label):
    """
    Fungsi BARU: Membuat plot bar chart dinamis
    antara metrik yang dipilih vs kondisi cuaca.
    """
    # Cek apakah kolom-kolom yang dibutuhkan ada
    if "Weather" in df.columns and metric_col in df.columns:
        df_weather_metric = df.dropna(subset=['Weather', metric_col])
        
        # Grup berdasarkan 'Weather' dan hitung rata-rata metrik yang dipilih
        # Kita gunakan 'mean' agar perbandingannya adil
        weather_metric_avg = df_weather_metric.groupby("Weather")[metric_col].mean().reset_index().sort_values(metric_col, ascending=False)
        
        # Buat title dinamis
        title = f"Rata-rata {metric_label} per Kondisi Cuaca"
        yaxis_title = f"Rata-rata {metric_label}"
        
        fig = px.bar(
            weather_metric_avg, 
            x="Weather", 
            y=metric_col,  # Gunakan kolom metrik
            color=metric_col, # Warnai berdasarkan kolom metrik
            color_continuous_scale=BASE_CONT_SCALE, 
            text_auto=".2f", 
            title=title # Title dinamis
        )
        fig.update_layout(
            yaxis_title=yaxis_title, # Y-axis dinamis
            paper_bgcolor='rgba(38, 41, 64, 0.99)', 
            plot_bgcolor='rgba(38, 41, 64, 0.95)',
            font=dict(size=16, family="Arial"),
            margin=dict(l=18, r=18, t=48, b=18),
        )
        return fig
    else:
        # Beri pesan jika kolom tidak ada (misal Family_Index belum dihitung)
        st.warning(f"Kolom '{metric_col}' tidak ditemukan untuk plot cuaca.")
        return None

# -------------------------------------------------------------------

def plot_family_index_vs_dwell(df):
    """
    Versi Ramah Orang Awam: Mengelompokkan Family Index menjadi kategori
    agar lebih mudah dibaca (Bar Chart, bukan Scatter).
    """
    if "Family_Index" in df.columns and "Avg_dwell_time_min" in df.columns:
        
        # 1. Buat salinan dataframe agar tidak mengganggu data utama
        df_chart = df.copy()

        # 2. Buat Kategori (Binning) untuk Family Index
        # Logika: 
        # 0.0 - 0.33 = Low (Sedikit Keluarga/Banyak Single)
        # 0.33 - 0.66 = Medium (Campuran)
        # 0.66 - 1.0 = High (Dominasi Keluarga)
        bins = [-0.1, 0.50, 0.75, 1.1] 
        labels = ["Low (Sedikit Keluarga)", "Medium (Campuran)", "High (Dominasi Keluarga)"]
        
        df_chart["Family_Category"] = pd.cut(df_chart["Family_Index"], bins=bins, labels=labels)

        # 3. Hitung Rata-rata Dwell Time per Kategori
        grouped = df_chart.groupby("Family_Category", observed=False)["Avg_dwell_time_min"].mean().reset_index()

        # 4. Visualisasi Bar Chart Sederhana
        fig = px.bar(
            grouped, 
            x="Family_Category", 
            y="Avg_dwell_time_min",
            color="Avg_dwell_time_min", # Warna makin gelap jika durasi makin lama
            color_continuous_scale="Blues",
            text_auto=".1f", # Tampilkan angka di batang
            title="Hubungan Kepadatan Keluarga vs Durasi Kunjungan"
        )

        fig.update_layout(
            yaxis_title="Rata-rata Durasi (Menit)",
            xaxis_title="Kategori Family Index",
            paper_bgcolor='rgba(38, 41, 64, 0.99)',
            plot_bgcolor='rgba(38, 41, 64, 0.95)',
            font=dict(size=16, family="Arial"),
            margin=dict(l=18, r=18, t=48, b=18),
            showlegend=False
        )
        
        # Hapus color bar di samping (agar lebih bersih untuk awam)
        fig.update_coloraxes(showscale=False) 

        return fig
    else: 
        return None


# -------------------------------------------------------------------
# FUNGSI UTAMA (MAIN) - DENGAN SIDEBAR INPUT
# -------------------------------------------------------------------
def main():
    
    # --- 1. BUAT SIDEBAR UNTUK INPUT (Tidak Berubah) ---
    with st.sidebar:
        st.header("⚙️ Kontrol Pengambilan Data")
        
        if 'token' not in st.session_state: st.session_state.token = "Bearer ey..."
        if 'start_date' not in st.session_state: st.session_state.start_date = date.today()
        if 'end_date' not in st.session_state: st.session_state.end_date = date.today()

        st.session_state.token = st.text_input("1. Authorization Token", value=st.session_state.token, type="password", help="Salin dari DevTools > Network > Request Headers")
        
        st.session_state.start_date = st.date_input("2. Tanggal Mulai", value=st.session_state.start_date)
        st.session_state.end_date = st.date_input("3. Tanggal Akhir", value=st.session_state.end_date)
        
        st.markdown("---")
        st.markdown(f"**UserID:** `{DEFAULT_USER_ID}`")
        st.markdown(f"**Site Code:** `{DEFAULT_SITE_CODE}`")
        st.markdown(f"**Lokasi:** `{DEFAULT_LOKASI[:20]}...`")
        st.markdown("*(Nilai di atas diatur di dalam kode)*")
        st.markdown("---")


        if st.button("🚀 Kumpulkan Data Baru", type="primary", use_container_width=True):
            
            start_date_norm = st.session_state.start_date.strftime("%Y-%m-%d")
            end_date_norm = st.session_state.end_date.strftime("%Y-%m-%d")
            start_date_slash = st.session_state.start_date.strftime("%Y/%m/%d")
            end_date_slash = st.session_state.end_date.strftime("%Y/%m/%d")

            with st.spinner("Mengambil data... Ini mungkin butuh beberapa saat..."):
                os.makedirs(DATA_FOLDER, exist_ok=True)
                
                res1 = fetch_customer_data(
                    st.session_state.token, DEFAULT_USER_ID, 
                    start_date_norm, end_date_norm, DEFAULT_SITE_CODE
                )
                res2 = fetch_dwell_data(
                    st.session_state.token, DEFAULT_USER_ID, 
                    start_date_slash, end_date_slash, DEFAULT_SITE_CODE
                )
                res3 = fetch_weather_data(
                    DEFAULT_LOKASI, start_date_norm, end_date_norm
                )
            
            if res1 and res2 and res3:
                st.success("Semua data berhasil diambil!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Satu atau lebih proses pengambilan data gagal. Cek pesan error di atas.")
        
        st.markdown("---")
        if st.button("🔄 Muat Ulang Data (Refresh)", use_container_width=True):
            st.cache_data.clear()
            st.rerun()


    # --- 2. TAMPILKAN DASHBOARD JIKA DATA SIAP ---
    
    st.markdown('<div style="text-align:center; font-size:2.6rem; font-weight:700; margin-bottom:1.2rem;">👤 Customer Profile Analysis</div>', unsafe_allow_html=True)

    file_check = [os.path.exists(CUSTOMER_FILE), os.path.exists(DWELL_FILE), os.path.exists(WEATHER_FILE)]
    
    if not all(file_check):
        st.info("👋 Selamat datang! Data mentah tidak ditemukan. Silakan isi parameter di sidebar kiri dan klik 'Kumpulkan Data Baru' untuk memulai.")
        
        warning_message = "File yang hilang: \n"
        if not file_check[0]:
            warning_message += "• customer_profile.csv\n"
        if not file_check[1]:
            warning_message += "• dwell_time_export.xlsx\n"
        if not file_check[2]:
            warning_message += "• data_cuaca.csv"
            
        st.warning(warning_message)
        
        st.stop()
        
    df_customer = load_customer_data()
    df_dwell = load_dwell_data()
    
    if isinstance(df_customer, str):
        st.error(df_customer)
        st.stop()
    if isinstance(df_dwell, str):
        st.error(df_dwell)
        st.stop()

    df_merged = merge_data(df_customer, df_dwell)
    
    if df_merged is None or df_merged.empty:
        st.error("Gagal memuat atau menggabungkan data. Pastikan semua file sumber ada dan benar.")
        st.info("Coba jalankan ulang 'Kumpulkan Data Baru' di sidebar.")
        st.stop()
        
    df = feature_engineering(df_merged)
    
    if df.empty:
        st.error("Data kosong setelah diproses. Tidak ada yang bisa ditampilkan.")
        st.stop()
        
    total_customer, total_site, date_range_str = kpi_content(df)
    
    k1, k2, k3 = st.columns([1,1,2])
    k1.metric("Total Customer", f"{total_customer:,}")
    k2.metric("Total Site", f"{total_site} lokasi")
    k3.metric("Rentang Tanggal (Data)", date_range_str)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👥 Proporsi Usia × Gender per Hari")
        
        # --- SOLUSI PADDING ---
        # Tambahkan 2 baris spasi kosong untuk 
        # menyeimbangkan 'selectbox' di col2.
        st.write("") 
        st.write("") 
        # --- AKHIR SOLUSI ---
        
        fig1 = plot_age_gender(df)
        if fig1: st.plotly_chart(fig1, use_container_width=True)
        st.markdown('<div class="block-space"></div>', unsafe_allow_html=True)
        
        st.subheader("📅 Family Index per Hari")
        fig2 = plot_family_index(df)
        if fig2: st.plotly_chart(fig2, use_container_width=True)
        st.markdown('<div class="block-space"></div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------
    # --- BLOK 'col2' (INI YANG DIMODIFIKASI) ---
    # -------------------------------------------------------------------
    with col2:
        # --- PERUBAHAN DIMULAI DI SINI ---
        
        # 1. Definisikan dulu opsi dropdown di luar subheader
        METRIC_OPTIONS = {
            # Label Pilihan : Nama Kolom di DataFrame
            "Family Index": "Family_Index",
            "Total Pengunjung": "Customer",
            "Total Pria": "Male_Total",
            "Total Wanita": "Female_Total",
            "Anak (0-6 thn)": "Child(0~6 Age)",
            "Remaja (7-15 thn)": "Young person(7~15 Age)",
            "Dewasa (16-35 thn)": "Teenager(16~35 Age)",
            "Paruh Baya (36-60 thn)": "Middle age(36~60 Age)",
            "Lansia (>60 thn)": "Senility(60< Age)"
        }
        available_options = {label: col for label, col in METRIC_OPTIONS.items() if col in df.columns}
        
        # 2. Buat kolom internal untuk menaruh subheader dan selectbox berdampingan
        sub_col1, sub_col2 = st.columns([2, 1]) # Ratio 2:1
        
        with sub_col1:
            st.subheader("🌦️ Analisis Metrik vs Cuaca")
        with sub_col2:
            selected_metric_label = st.selectbox(
                "Pilih Metrik:", # Label yang lebih singkat
                options=list(available_options.keys()),
                key="weather_metric_select"
            )
            
        # 3. Sekarang, panggil plotnya. Ini akan sejajar dengan plot di col1
        if selected_metric_label:
            selected_metric_col = available_options[selected_metric_label]
            fig3 = plot_metric_vs_cuaca(df, selected_metric_col, selected_metric_label)
            
            if fig3: 
                st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("Tidak ada metrik yang tersedia untuk diplot.")
        
        # --- AKHIR PERUBAHAN ---
        
        st.markdown('<div class="block-space"></div>', unsafe_allow_html=True)
        
        # Plot vs Dwell Time (tetap sama)
        st.subheader("🧭 Family Index vs Dwell Time")
        fig4 = plot_family_index_vs_dwell(df)
        if fig4: st.plotly_chart(fig4, use_container_width=True)
        st.markdown('<div class="block-space"></div>', unsafe_allow_html=True)
    # -------------------------------------------------------------------
    
    st.caption('<div style="font-size:0.97em;text-align:center">© 2025 Customer Profile + Dwell Time Analytics - Tema Senada</div>', unsafe_allow_html=True)

# --- Jalankan Fungsi Utama ---
if __name__ == "__main__":
    main()