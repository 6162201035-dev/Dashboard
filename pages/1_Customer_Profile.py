import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
from datetime import date 

# --- IMPORT MODULE AI (Pastikan ai_utils.py ada di folder root/utama) ---
import sys
sys.path.append('.') # Memastikan python bisa membaca file di folder root
import ai_utils 

# -------------------------------------------------------------------
# KONFIGURASI UTAMA
# -------------------------------------------------------------------

# --- Konfigurasi Path Data ---
DATA_FOLDER = "data"
CUSTOMER_FILE = os.path.join(DATA_FOLDER, "customer_profile.csv")
WEATHER_FILE = os.path.join(DATA_FOLDER, "data_cuaca.csv")
DWELL_FILE = os.path.join(DATA_FOLDER, "dwell_time_export.xlsx")

# --- Konfigurasi API ---
VISUAL_CROSSING_API_KEY = "477QVYDNSEPM6BJ6YS7GG7THZ" 

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
# FUNGSI PENGAMBIL DATA
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
# FUNGSI PEMUAT DATA
# -------------------------------------------------------------------

@st.cache_data
def load_customer_data():
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
# FUNGSI PROSES & PLOT
# -------------------------------------------------------------------

def merge_data(df, dwell):
    if df is None or dwell is None: return None
    if "Date" in df.columns and "Site" in df.columns and "Date" in dwell.columns and "Site" in dwell.columns:
        return pd.merge(df, dwell, on=["Date", "Site"], how="left")
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

# --- Fungsi Peringkas Data untuk AI (BARU) ---
def generate_data_summary(df):
    """
    Meringkas data dari 4 Chart utama agar AI bisa menganalisis visualisasi dashboard.
    """
    if df.empty: return "Data Kosong."
    
    # --- BAGIAN 1: DEMOGRAFI (Chart Kiri Atas) ---
    total_visit = df['Customer'].sum()
    total_male = df['Male_Total'].sum()
    total_female = df['Female_Total'].sum()
    
    # Cari hari tersibuk
    if 'DayOfWeek' in df.columns:
        busy_day = df.groupby('DayOfWeek', observed=True)['Customer'].sum().idxmax()
    else:
        busy_day = "N/A"

    # Kelompok usia dominan
    age_cols = ["Child(0~6 Age)", "Young person(7~15 Age)", "Teenager(16~35 Age)", "Middle age(36~60 Age)", "Senility(60< Age)"]
    top_age_group = df[age_cols].sum().idxmax()
    
    demog_summary = f"""
    - Total Pengunjung: {total_visit}
    - Gender: Pria {total_male} vs Wanita {total_female}
    - Usia Dominan: {top_age_group}
    - Hari Tersibuk: {busy_day}
    """

    # --- BAGIAN 2: FAMILY INDEX PER HARI (Chart Kiri Bawah) ---
    family_trend = "Data Family Index N/A"
    if 'Family_Index' in df.columns and 'DayOfWeek' in df.columns:
        # Cari hari dengan Family Index tertinggi
        day_family = df.groupby("DayOfWeek", observed=True)["Family_Index"].mean()
        highest_family_day = day_family.idxmax()
        highest_val = day_family.max()
        family_trend = f"Rata-rata Family Index tertinggi jatuh pada hari {highest_family_day} (Skor: {highest_val:.2f})"

    # --- BAGIAN 3: METRIK VS CUACA (Chart Kanan Atas) ---
    weather_insight = "Data Cuaca N/A"
    if 'Weather' in df.columns:
        # Kita ambil rata-rata Total Customer per Cuaca sebagai default insight
        weather_grp = df.groupby('Weather')['Customer'].mean().sort_values(ascending=False).head(3)
        weather_dict = {k: round(v, 1) for k, v in weather_grp.items()}
        weather_insight = f"Rata-rata Kunjungan Tertinggi saat Cuaca: {weather_dict}"

    # --- BAGIAN 4: FAMILY INDEX VS DWELL TIME (Chart Kanan Bawah) ---
    relation_summary = "Data Hubungan N/A"
    if "Family_Index" in df.columns and "Avg_dwell_time_min" in df.columns:
        df_temp = df.copy()
        bins = [-0.1, 0.50, 0.75, 1.1] 
        labels = ["Low", "Medium", "High"]
        df_temp["Family_Category"] = pd.cut(df_temp["Family_Index"], bins=bins, labels=labels)
        
        grouped = df_temp.groupby("Family_Category", observed=False)["Avg_dwell_time_min"].mean()
        relation_summary = (
            f"Low Family Index (Single/Sedikit) Dwell Time: {grouped.get('Low', 0):.1f} menit; "
            f"High Family Index (Keluarga Besar) Dwell Time: {grouped.get('High', 0):.1f} menit"
        )

    # --- GABUNGKAN SEMUA ---
    final_text = f"""
    ANALISIS DASHBOARD (4 CHART):
    
    1. CHART DEMOGRAFI:
    {demog_summary}
    
    2. CHART FAMILY INDEX (TREN HARIAN):
    {family_trend}
    
    3. CHART CUACA (DAMPAK KE KUNJUNGAN):
    {weather_insight}
    
    4. CHART HUBUNGAN (FAMILY INDEX VS LAMA KUNJUNGAN):
    {relation_summary}
    """
    return final_text
# --- Fungsi Plotting ---

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
            title="Proporsi (%) Pengunjung Berdasarkan Usia dan Gender"
        )
        fig.update_layout(yaxis_title="Proporsi (%)", title_x=0.05, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=14))
        return fig
    else: return None

def plot_family_index(df):
    if "Family_Index" in df.columns and "DayOfWeek" in df.columns:
        day_family = df.groupby("DayOfWeek", observed=True)["Family_Index"].mean().reset_index()
        fig = px.bar(day_family, x="DayOfWeek", y="Family_Index", text_auto=".2f", color="Family_Index", color_continuous_scale=BASE_CONT_SCALE, title="Rata-rata Family Index per Hari", category_orders={"DayOfWeek":ORDER_DAYS})
        fig.update_layout(yaxis_title="Family Index (0-1)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig
    else: return None

def plot_metric_vs_cuaca(df, metric_col, metric_label):
    if "Weather" in df.columns and metric_col in df.columns:
        df_weather_metric = df.dropna(subset=['Weather', metric_col])
        weather_metric_avg = df_weather_metric.groupby("Weather")[metric_col].mean().reset_index().sort_values(metric_col, ascending=False)
        fig = px.bar(
            weather_metric_avg, x="Weather", y=metric_col, color=metric_col, 
            color_continuous_scale=BASE_CONT_SCALE, text_auto=".2f", 
            title=f"Rata-rata {metric_label} vs Cuaca"
        )
        fig.update_layout(yaxis_title=metric_label, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig
    return None

def plot_family_index_vs_dwell(df):
    if "Family_Index" in df.columns and "Avg_dwell_time_min" in df.columns:
        df_chart = df.copy()
        bins = [-0.1, 0.50, 0.75, 1.1] 
        labels = ["Low", "Medium", "High"]
        df_chart["Family_Category"] = pd.cut(df_chart["Family_Index"], bins=bins, labels=labels)
        grouped = df_chart.groupby("Family_Category", observed=False)["Avg_dwell_time_min"].mean().reset_index()
        fig = px.bar(
            grouped, x="Family_Category", y="Avg_dwell_time_min",
            color="Avg_dwell_time_min", color_continuous_scale="Blues", text_auto=".1f",
            title="Family Index vs Durasi Kunjungan (Menit)"
        )
        fig.update_layout(yaxis_title="Menit", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        return fig
    return None


# -------------------------------------------------------------------
# FUNGSI UTAMA (MAIN)
# -------------------------------------------------------------------
def main():
    
    with st.sidebar:
        st.header("⚙️ Data Control")
        if 'token' not in st.session_state: st.session_state.token = "Bearer ey..."
        if 'start_date' not in st.session_state: st.session_state.start_date = date.today()
        if 'end_date' not in st.session_state: st.session_state.end_date = date.today()

        st.session_state.token = st.text_input("Authorization Token", value=st.session_state.token, type="password")
        st.session_state.start_date = st.date_input("Start Date", value=st.session_state.start_date)
        st.session_state.end_date = st.date_input("End Date", value=st.session_state.end_date)
        st.markdown("---")
        
        if st.button("🚀 Kumpulkan Data Baru", type="primary", use_container_width=True):
            start_norm = st.session_state.start_date.strftime("%Y-%m-%d")
            end_norm = st.session_state.end_date.strftime("%Y-%m-%d")
            start_slash = st.session_state.start_date.strftime("%Y/%m/%d")
            end_slash = st.session_state.end_date.strftime("%Y/%m/%d")

            with st.spinner("Downloading..."):
                os.makedirs(DATA_FOLDER, exist_ok=True)
                r1 = fetch_customer_data(st.session_state.token, DEFAULT_USER_ID, start_norm, end_norm, DEFAULT_SITE_CODE)
                r2 = fetch_dwell_data(st.session_state.token, DEFAULT_USER_ID, start_slash, end_slash, DEFAULT_SITE_CODE)
                r3 = fetch_weather_data(DEFAULT_LOKASI, start_norm, end_norm)
            
            if r1 and r2 and r3:
                st.success("Done! Refreshing...")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Failed to download some data.")
        
        if st.button("🔄 Refresh Cache", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # --- MAIN PAGE CONTENT ---
    st.markdown('<div style="text-align:center; font-size:2.6rem; font-weight:700; margin-bottom:1.2rem;">👤 Customer Profile Analysis</div>', unsafe_allow_html=True)

    if not (os.path.exists(CUSTOMER_FILE) and os.path.exists(DWELL_FILE) and os.path.exists(WEATHER_FILE)):
        st.info("Data belum tersedia. Silakan masukkan Token dan klik 'Kumpulkan Data Baru'.")
        st.stop()
        
    df_customer = load_customer_data()
    df_dwell = load_dwell_data()
    
    if isinstance(df_customer, str) or isinstance(df_dwell, str):
        st.error(f"Error loading data: {df_customer} | {df_dwell}")
        st.stop()

    df_merged = merge_data(df_customer, df_dwell)
    if df_merged is None: st.stop()
    df = feature_engineering(df_merged)
    
    # --- KPI METRICS ---
    total_customer, total_site, date_range_str = kpi_content(df)
    k1, k2, k3 = st.columns([1,1,2])
    k1.metric("Total Customer", f"{total_customer:,}")
    k2.metric("Total Site", f"{total_site} lokasi")
    k3.metric("Data Range", date_range_str)
    
    st.markdown("---")
    
    # ==========================================
    # ✨ FITUR AI ANALYST (MODUL 1)
    # ==========================================
    with st.expander("✨ Tanya AI tentang Profil Pengunjung Ini", expanded=False):
        c_ai1, c_ai2 = st.columns([3, 1])
        
        with c_ai1:
            q_options = [
                "Jelaskan profil demografi utama (usia & gender).",
                "Bagaimana cuaca mempengaruhi jumlah pengunjung?",
                "Apakah ada hubungan antara tipe keluarga (Family Index) dan lama kunjungan?",
                "Tulis pertanyaan sendiri..."
            ]
            selected_q = st.selectbox("Pilih Pertanyaan:", q_options)
            
            if selected_q == "Tulis pertanyaan sendiri...":
                user_q = st.text_input("Ketik pertanyaanmu:", "Berikan rekomendasi strategi marketing berdasarkan data ini.")
            else:
                user_q = selected_q
        
        with c_ai2:
            st.write("") 
            st.write("") 
            tombol_tanya = st.button("Analisa Sekarang 🤖", type="primary", use_container_width=True)
            
        if tombol_tanya:
            with st.spinner("AI sedang berpikir..."):
                # 1. Generate ringkasan data
                summary_text = generate_data_summary(df)
                
                # 2. Kirim ke Gemini (lewat ai_utils)
                jawaban_ai = ai_utils.analyze_with_gemini(summary_text, user_q)
                
                # 3. Tampilkan
                st.markdown("### 💡 Insight AI:")
                st.markdown(jawaban_ai)
    
    st.markdown("---") 

    # --- CHARTS ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👥 Demografi")
        fig1 = plot_age_gender(df)
        if fig1: st.plotly_chart(fig1, use_container_width=True)
        st.markdown('<div class="block-space"></div>', unsafe_allow_html=True)
        
        st.subheader("📅 Family Index")
        fig2 = plot_family_index(df)
        if fig2: st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Metrik vs Cuaca
        METRIC_OPTIONS = {
            "Family Index": "Family_Index", "Total Pengunjung": "Customer",
            "Total Pria": "Male_Total", "Total Wanita": "Female_Total"
        }
        sub_col1, sub_col2 = st.columns([2, 1])
        with sub_col1: st.subheader("🌦️ Metrik vs Cuaca")
        with sub_col2: 
            sel_met = st.selectbox("Pilih Metrik:", list(METRIC_OPTIONS.keys()))
        
        if sel_met:
            fig3 = plot_metric_vs_cuaca(df, METRIC_OPTIONS[sel_met], sel_met)
            if fig3: st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown('<div class="block-space"></div>', unsafe_allow_html=True)
        
        st.subheader("🧭 Family Index vs Dwell Time")
        fig4 = plot_family_index_vs_dwell(df)
        if fig4: st.plotly_chart(fig4, use_container_width=True)

if __name__ == "__main__":
    main()


