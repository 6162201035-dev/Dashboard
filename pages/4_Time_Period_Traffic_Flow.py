# ==========================================
# ⏰ TIME PERIOD & RETAIL TRAFFIC ANALYSIS (LAYOUT FIXED)
# ==========================================
import streamlit as st
import pandas as pd
import plotly.express as px
import os       
import requests 
from datetime import date 

# --- IMPORT MODULE AI ---
import sys
sys.path.append('.') 
import ai_utils 

# ==============================
# ⚙️ CONFIG
# ==============================

st.set_page_config(
    page_title="Time Period & Flow Analysis",
    page_icon="⏰",
    layout="wide"
)

# --- Path & Nilai Tetap ---
DATA_FOLDER = "data"
TRAFFIC_FILE = os.path.join(DATA_FOLDER, "time_period_traffic.xlsx")
FLOW_IN_FILE = os.path.join(DATA_FOLDER, "time_period_flow_in.xlsx")
FLOW_OUT_FILE = os.path.join(DATA_FOLDER, "time_period_flow_out.xlsx")

DEFAULT_USER_ID = "4748ef52-ccb6-4dbe-acf4-1268d25123d8"
DEFAULT_SITE_CODE = "P00077"

# ==============================
# 📥 FUNGSI PENGAMBIL DATA (KODE ASLI)
# ==============================

def fetch_time_period_traffic(token, user_id, start_date_norm, end_date_norm, site_code):
    st.write("1/3: Mengambil Data Time Period TRAFFIC...")
    data_api_url = 'https://winnertech.hk:8090/api/en-us/TimePeriodFlowAcc/CustomerFlowSumDetailExportData'
    data_payload = {
        "menuId": 3000103, "lang": "en-us",
        "params": {
            "beginDate": start_date_norm, "endDate": end_date_norm,
            "dateType": "d", "module": "BM00019S002", "isClose": 0,
            "siteTreeSelects": [
                {"code": site_code, "type": 0, "source": 0, "operators": []}
            ],
            "startHourTime": "00:00", "endHourTime": "23:00"
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
            with open(TRAFFIC_FILE, 'wb') as f: f.write(response.content)
            st.success(f"Sukses (1/3): File Traffic ({TRAFFIC_FILE}) disimpan.")
            return True
        else:
            st.error(f"Gagal (1/3): Server tidak mengembalikan file Traffic. Respons:\n{response.json()}")
            return False
    except Exception as e:
        st.error(f"KRITIS (1/3): Error saat mengambil Data Traffic: {e}")
        return False

def fetch_time_period_flow_in(token, user_id, start_date_norm, end_date_norm, site_code):
    st.write("2/3: Mengambil Data Time Period FLOW IN...")
    data_api_url = 'https://winnertech.hk:8090/api/en-us/TimePeriodFlow/CustomerFlowSumDetailExportData'
    data_payload = {
        "menuId": 2000103, "lang": "en-us",
        "params": {
            "beginDate": start_date_norm, "endDate": end_date_norm,
            "dateType": "d", "module": "BM00001", "isClose": 0,
            "siteTreeSelects": [
                {"code": site_code, "type": 0, "source": 0, "operators": []}
            ],
            "passFlowType": "inSum", 
            "startHourTime": "00:00", "endHourTime": "23:00"
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
            with open(FLOW_IN_FILE, 'wb') as f: f.write(response.content)
            st.success(f"Sukses (2/3): File Flow In ({FLOW_IN_FILE}) disimpan.")
            return True
        else:
            st.error(f"Gagal (2/3): Server tidak mengembalikan file Flow In. Respons:\n{response.json()}")
            return False
    except Exception as e:
        st.error(f"KRITIS (2/3): Error saat mengambil Data Flow In: {e}")
        return False

def fetch_time_period_flow_out(token, user_id, start_date_norm, end_date_norm, site_code):
    st.write("3/3: Mengambil Data Time Period FLOW OUT...")
    data_api_url = 'https://winnertech.hk:8090/api/en-us/TimePeriodFlow/CustomerFlowSumDetailExportData'
    data_payload = {
        "menuId": 2000103, "lang": "en-us",
        "params": {
            "beginDate": start_date_norm, "endDate": end_date_norm,
            "dateType": "d", "module": "BM00001", "isClose": 0,
            "siteTreeSelects": [
                {"code": site_code, "type": 0, "source": 0, "operators": []}
            ],
            "passFlowType": "outSum", 
            "startHourTime": "00:00", "endHourTime": "23:00"
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
            with open(FLOW_OUT_FILE, 'wb') as f: f.write(response.content)
            st.success(f"Sukses (3/3): File Flow Out ({FLOW_OUT_FILE}) disimpan.")
            return True
        else:
            st.error(f"Gagal (3/3): Server tidak mengembalikan file Flow Out. Respons:\n{response.json()}")
            return False
    except Exception as e:
        st.error(f"KRITIS (3/3): Error saat mengambil Data Flow Out: {e}")
        return False

# ==============================
# 📂 LOAD DATA
# ==============================
@st.cache_data
def load_data():
    try:
        df_traffic = pd.read_excel(TRAFFIC_FILE, header=0) 
    except FileNotFoundError:
        return f"File '{TRAFFIC_FILE}' tidak ditemukan.", None, None
    except Exception as e:
        return f"Gagal membaca file '{TRAFFIC_FILE}'. Error: {e}", None, None
        
    try:
        df_flow_in = pd.read_excel(FLOW_IN_FILE, header=0)
    except FileNotFoundError:
        return None, f"File '{FLOW_IN_FILE}' tidak ditemukan.", None
    except Exception as e:
        return None, f"Gagal membaca file '{FLOW_IN_FILE}'. Error: {e}", None
            
    try:
        df_flow_out = pd.read_excel(FLOW_OUT_FILE, header=0)
    except FileNotFoundError:
        return None, None, f"File '{FLOW_OUT_FILE}' tidak ditemukan."
    except Exception as e:
        return None, None, f"Gagal membaca file '{FLOW_OUT_FILE}'. Error: {e}"

    df_traffic.columns = [c.strip() for c in df_traffic.columns]
    df_flow_in.columns = [c.strip() for c in df_flow_in.columns]
    df_flow_out.columns = [c.strip() for c in df_flow_out.columns]

    return df_traffic, df_flow_in, df_flow_out

# ==========================================
# 🧠 FUNGSI AI SUMMARY
# ==========================================
def generate_traffic_ai_summary(df):
    if df.empty: return "Data Kosong."
    
    total_visit = df['Total'].sum()
    busiest_day_idx = df['Total'].idxmax()
    busiest_day = df.loc[busiest_day_idx, 'Weekly']
    busiest_val = df.loc[busiest_day_idx, 'Total']
    
    hour_cols = [c for c in df.columns if "~" in c]
    if hour_cols:
        hourly_means = df[hour_cols].mean()
        peak_hour = hourly_means.idxmax()
        peak_val = hourly_means.max()
        
        summary = f"""
        DATA TIME PERIOD TRAFFIC:
        - Total Pengunjung dalam periode ini: {total_visit:,.0f} orang.
        - Hari Tersibuk: {busiest_day} dengan total {busiest_val:,.0f} pengunjung.
        - Jam Tersibuk (Peak Hour): {peak_hour} (Rata-rata {peak_val:.1f} orang/jam).
        
        Tugas AI: Berikan analisis tentang pola jam sibuk ini. Kapan staff harus siaga penuh? Kapan waktu istirahat yang aman?
        """
    else:
        summary = f"Data total: {total_visit}. Data jam tidak ditemukan."
        
    return summary

# ===================================
# 🎁 VISUALISASI DASHBOARD
# ===================================
def build_dashboard(df_traffic, df_flow_in, df_flow_out):
    
    COLOR_PRIMARY = "#00B4D8"
    COLOR_SECONDARY = "#F72585"
    COLOR_WARNING = "#FFB703"
    BAR_COLOR_MAP = {
        "Traffic (Customer)": COLOR_PRIMARY,
        "Flow In": "#3A0CA3",
        "Flow Out": COLOR_SECONDARY
    }

    st.subheader("🧭 Ringkasan Data Total")
    total_traffic = df_traffic["Total"].sum()
    total_flow_in = df_flow_in["Total"].sum()
    total_flow_out = df_flow_out["Total"].sum()
    
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric("Total Traffic (Customer)", f"{int(total_traffic):,}")
    col_kpi2.metric("Total Flow In", f"{int(total_flow_in):,}")
    col_kpi3.metric("Total Flow Out", f"{int(total_flow_out):,}")
    
    st.markdown("---")
    
    hour_cols = [col for col in df_traffic.columns if "~" in col]
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 Heatmap Traffic per Hari dan Jam")
        if hour_cols:
            heatmap_df = df_traffic.melt(id_vars=["Weekly"], value_vars=hour_cols, var_name="Hour", value_name="Visitors")
            heatmap_df['Weekly'] = pd.Categorical(heatmap_df['Weekly'], categories=day_order, ordered=True)
            
            fig_heat = px.density_heatmap(
                heatmap_df, x="Hour", y="Weekly", z="Visitors",
                color_continuous_scale="Plasma", title="Distribusi Kepadatan Pengunjung", height=500 
            )
            fig_heat.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.warning("Kolom jam tidak ditemukan.")

    with col2:
        st.subheader("📈 Rata-rata Traffic per Jam")
        if hour_cols:
            if 'heatmap_df' not in locals():
                 heatmap_df = df_traffic.melt(id_vars=["Weekly"], value_vars=hour_cols, var_name="Hour", value_name="Visitors")
            
            hourly_avg = heatmap_df.groupby("Hour")["Visitors"].mean().reset_index()
            fig_hourly = px.line(
                hourly_avg, x="Hour", y="Visitors", markers=True,
                title="Rata-rata Pengunjung per Jam", color_discrete_sequence=[COLOR_PRIMARY], height=500 
            )
            fig_hourly.update_traces(fill='tozeroy')
            fig_hourly.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_hourly, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("📅 Total per Hari (Traffic vs Flow)")
        df_total_day = pd.DataFrame({
            "Weekly": df_traffic["Weekly"],
            "Traffic (Customer)": df_traffic["Total"],
            "Flow In": df_flow_in["Total"],
            "Flow Out": df_flow_out["Total"]
        })
        df_total_melted = df_total_day.melt(id_vars="Weekly", var_name="Tipe Metrik", value_name="Jumlah")
        df_total_melted['Weekly'] = pd.Categorical(df_total_melted['Weekly'], categories=day_order, ordered=True)
        df_total_melted.sort_values(by='Weekly', inplace=True)

        fig_total = px.bar(
            df_total_melted, x="Weekly", y="Jumlah", color="Tipe Metrik", barmode="group",
            title="Total Kunjungan per Hari", color_discrete_map=BAR_COLOR_MAP, height=500 
        )
        fig_total.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_total, use_container_width=True)

    with col4:
        st.subheader("🧭 Pola Weekday vs Weekend")
        if hour_cols:
            weekday_df = df_traffic[df_traffic["Weekly"].isin(["Monday","Tuesday","Wednesday","Thursday","Friday"])]
            weekend_df = df_traffic[df_traffic["Weekly"].isin(["Saturday","Sunday"])]
            
            if not weekday_df.empty and not weekend_df.empty:
                compare_df = pd.DataFrame({
                    "Hour": hour_cols,
                    "Weekday": weekday_df[hour_cols].mean().values,
                    "Weekend": weekend_df[hour_cols].mean().values
                }).melt(id_vars="Hour", var_name="Period", value_name="Visitors")

                fig_compare = px.line(
                    compare_df, x="Hour", y="Visitors", color="Period", markers=True,
                    title="Pola Kunjungan: Weekday vs Weekend", color_discrete_sequence=[COLOR_PRIMARY, COLOR_WARNING], height=500 
                )
                fig_compare.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_compare, use_container_width=True)
            else:
                st.info("Data Weekday atau Weekend tidak lengkap.")

# ==============================
# 🚀 MAIN (KONTROLER)
# ==============================
def main():
    
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

        if st.button("🚀 Kumpulkan Data Time Period", type="primary", use_container_width=True):
            start_date_norm = st.session_state.start_date.strftime("%Y-%m-%d")
            end_date_norm = st.session_state.end_date.strftime("%Y-%m-%d")
            
            with st.spinner("Mengambil data..."):
                os.makedirs(DATA_FOLDER, exist_ok=True)
                res1 = fetch_time_period_traffic(st.session_state.token, DEFAULT_USER_ID, start_date_norm, end_date_norm, DEFAULT_SITE_CODE)
                res2 = fetch_time_period_flow_in(st.session_state.token, DEFAULT_USER_ID, start_date_norm, end_date_norm, DEFAULT_SITE_CODE)
                res3 = fetch_time_period_flow_out(st.session_state.token, DEFAULT_USER_ID, start_date_norm, end_date_norm, DEFAULT_SITE_CODE)
            
            if res1 and res2 and res3:
                st.success("Semua 3 file data berhasil diambil!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Satu atau lebih pengambilan data gagal.")
        
        st.markdown("---")
        if st.button("🔄 Muat Ulang Data (Refresh)", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown('<div style="text-align:center; font-size:2.6rem; font-weight:700; margin-bottom:1.2rem;">⏰ Time Period Traffic & Flow</div>', unsafe_allow_html=True)
    st.caption("Analisis intensitas kunjungan pengunjung berdasarkan hari dan jam.")

    file_check = [os.path.exists(TRAFFIC_FILE), os.path.exists(FLOW_IN_FILE), os.path.exists(FLOW_OUT_FILE)]
    
    if not all(file_check):
        st.info("👋 Selamat datang! Data Time Period tidak ditemukan. Silakan klik 'Kumpulkan Data' di sidebar.")
        st.stop()
        
    df_traffic, df_flow_in, df_flow_out = load_data() 
    
    if isinstance(df_traffic, str) or isinstance(df_flow_in, str) or isinstance(df_flow_out, str): 
        st.error("Gagal load data.")
        st.stop()

    if df_traffic is not None:
        build_dashboard(df_traffic, df_flow_in, df_flow_out)

        # ==========================================
        # ✨ FITUR AI (UI DIPERBAIKI - FULL WIDTH)
        # ==========================================
        st.markdown("---")
        with st.expander("✨ Tanya AI tentang Pola Kunjungan", expanded=False):
            # Input dan Tombol tetap di kolom agar rapi
            c_ai1, c_ai2 = st.columns([3, 1])
            with c_ai1:
                q_options = [
                    "Kapan jam tersibuk dan apa saran shift karyawan?",
                    "Jelaskan perbedaan pola Weekday vs Weekend.",
                    "Apakah ada pola anomali di jam tertentu?",
                    "Tulis pertanyaan sendiri..."
                ]
                selected_q = st.selectbox("Pilih Pertanyaan:", q_options)
                user_q = st.text_input("Ketik pertanyaanmu:", "Jelaskan tren trafik hari ini.") if selected_q == "Tulis pertanyaan sendiri..." else selected_q
            
            with c_ai2:
                st.write("") 
                st.write("")
                # Simpan status klik tombol
                tombol_analisa = st.button("Analisa Waktu 🤖", type="primary", use_container_width=True)

            # JAWABAN DI LUAR KOLOM (FULL WIDTH)
            if tombol_analisa:
                with st.spinner("AI sedang menganalisis pola waktu..."):
                    summary_text = generate_traffic_ai_summary(df_traffic)
                    jawaban = ai_utils.analyze_with_gemini(summary_text, user_q)
                    
                    st.markdown("### 💡 Insight Operasional:")
                    st.info(jawaban) # Menggunakan st.info agar ada background biru/kotak yang rapi

if __name__ == "__main__":
    main()
