import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# --- Path & Constants ---
DATA_FOLDER = "data"
AREA_TRAFFIC_FILE = os.path.join(DATA_FOLDER, "area_traffic.xlsx")
GATE_FLOW_FILE = os.path.join(DATA_FOLDER, "gate_flow.xlsx")

DEFAULT_USER_ID = "4748ef52-ccb6-4dbe-acf4-1268d25123d8"
DEFAULT_SITE_CODE = "P00077"

# ==============================
# 📥 DATA FETCHING FUNCTIONS
# ==============================

def fetch_area_traffic(token, user_id, start_date_slash, end_date_slash, site_code):
    """Fetch SelType 400 (Area Traffic)"""
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

def fetch_gate_flow(token, user_id, start_date_slash, end_date_slash, site_code):
    """Fetch SelType 700 (Gate Flow)"""
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
# 📂 DATA LOADING
# ==============================
@st.cache_data
def load_data():
    """Reads and processes the Excel files"""
    try:
        df_traffic = pd.read_excel(AREA_TRAFFIC_FILE, sheet_name="Datas", header=0)
    except FileNotFoundError:
        return f"File '{AREA_TRAFFIC_FILE}' not found.", None
    except Exception as e:
        return f"Error reading '{AREA_TRAFFIC_FILE}': {e}", None
        
    try:
        df_flow = pd.read_excel(GATE_FLOW_FILE, sheet_name="Datas", header=0)
    except FileNotFoundError:
        return None, f"File '{GATE_FLOW_FILE}' not found."
    except Exception as e:
        return None, f"Error reading '{GATE_FLOW_FILE}': {e}"

    # --- Rename Map ---
    rename_map_traffic = {
        "Site": "Area",
        "Customer": "Customer",  
        "Flow (in)": "Flow(in)",
        "Flow  (out)": "Flow(out)", 
        "Number of stores": "Number of stores"     
    }
    
    rename_map_flow = {
        "Site": "Gate",
        "Flow (in)": "Gate Flow(in)", 
        "Flow  (out)": "Gate Flow(out)", 
        "Customer": "Customer",
        "Number of stores": "Number of stores"
    }
    
    # Apply Rename
    df_traffic.rename(columns={k: v for k, v in rename_map_traffic.items() if k in df_traffic.columns}, inplace=True)
    df_flow.rename(columns={k: v for k, v in rename_map_flow.items() if k in df_flow.columns}, inplace=True)
    
    # Numeric Conversion
    cols_to_convert_traffic = ["Customer", "Flow(in)", "Flow(out)"]
    for col in cols_to_convert_traffic:
        if col in df_traffic.columns:
            df_traffic[col] = pd.to_numeric(df_traffic[col], errors='coerce').fillna(0)
            
    cols_to_convert_flow = ["Gate Flow(in)", "Gate Flow(out)", "Customer"]
    for col in cols_to_convert_flow:
        if col in df_flow.columns:
            df_flow[col] = pd.to_numeric(df_flow[col], errors='coerce').fillna(0)

    # Simple Validation
    if 'Area' not in df_traffic.columns:
        st.error("Column 'Area' missing. Check `rename_map_traffic`.")
    if 'Gate Flow(out)' not in df_flow.columns:
        st.error("Column 'Gate Flow(out)' missing. Check `rename_map_flow`.")

    return df_traffic, df_flow

# ===================================
# 🎁 DASHBOARD BUILDER (MODIFIED)
# ===================================
def build_dashboard(df_traffic, df_flow):
    """
    Fungsi ini menganalisis data RINGKASAN dalam satu halaman.
    """
    
    # --- 1. HOTSPOTS INSIGHTS ---
    # Hitung Gate tersibuk
    if not df_flow.empty:
        df_flow['Total_Gate_Vol'] = df_flow['Gate Flow(in)'] + df_flow['Gate Flow(out)']
        busiest_gate_row = df_flow.loc[df_flow['Total_Gate_Vol'].idxmax()]
        busiest_gate_name = busiest_gate_row['Gate']
        busiest_gate_val = busiest_gate_row['Total_Gate_Vol']
    else:
        busiest_gate_name, busiest_gate_val = "-", 0

    # Hitung Area tersibuk
    if not df_traffic.empty:
        busiest_area_row = df_traffic.loc[df_traffic['Customer'].idxmax()]
        busiest_area_name = busiest_area_row['Area']
        busiest_area_val = busiest_area_row['Customer']
    else:
        busiest_area_name, busiest_area_val = "-", 0
    
    st.info(f"""
    🔥 **Hotspots & Highlights:**
    - **Gate Tersibuk:** {busiest_gate_name} ({int(busiest_gate_val):,} lintasan)
    - **Area Teramai:** {busiest_area_name} ({int(busiest_area_val):,} customer)
    """)

    # --- 2. KPI METRICS ---
    st.subheader("🧭 Ringkasan KPI Total")
    total_customer = df_traffic['Customer'].sum()
    total_flow_in = df_flow['Gate Flow(in)'].sum()
    total_flow_out = df_flow['Gate Flow(out)'].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Area Traffic", f"{int(total_customer):,}")
    c2.metric("Total Gate Inflow", f"{int(total_flow_in):,}")
    c3.metric("Total Gate Outflow", f"{int(total_flow_out):,}")
    
    st.markdown("---")

    # --- 3. MAIN COLUMNS ---
    col1, col2 = st.columns(2)

    # =========================================
    # KOLOM KIRI: AREA ANALYSIS (Bar + Donut)
    # =========================================
    with col1:
        with st.container(border=True):
            st.subheader("📊 Analisis Area")
            
            # A. Bar Chart Area
            area_agg = df_traffic.groupby("Area")["Customer"].sum().reset_index().sort_values(by="Customer", ascending=False)
            area_agg = area_agg[area_agg['Customer'] > 0]
            
            if not area_agg.empty:
                fig_area = px.bar(
                    area_agg, x="Area", y="Customer",
                    color="Customer", color_continuous_scale="Blues",
                    title="Volume Customer per Area"
                )
                st.plotly_chart(fig_area, use_container_width=True)
                
                # B. Donut Chart
                st.markdown("---")
                top_n = 5
                df_pie = area_agg.copy()
                if len(df_pie) > top_n:
                    top_5 = df_pie.iloc[:top_n]
                    others = pd.DataFrame(data={
                        'Area': ['Others'], 
                        'Customer': [df_pie.iloc[top_n:]['Customer'].sum()]
                    })
                    df_pie_final = pd.concat([top_5, others])
                else:
                    df_pie_final = df_pie

                fig_pie = px.pie(
                    df_pie_final, values='Customer', names='Area', hole=0.4,
                    title=f"Market Share Traffic (Top {top_n})",
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            else:
                st.warning("Data Customer kosong.")

    # =========================================
    # KOLOM KANAN: GATE ANALYSIS (Bar + Scatter)
    # =========================================
    with col2:
        with st.container(border=True):
            st.subheader("🚪 Analisis Gate")
            
            # --- A. Grouped Bar Chart (Masuk vs Keluar) ---
            gate_agg = df_flow.groupby("Gate").agg({
                "Gate Flow(in)": "sum",
                "Gate Flow(out)": "sum"
            }).reset_index()
            
            if not gate_agg.empty and 'Gate Flow(in)' in gate_agg.columns:
                gate_melted = gate_agg.melt(id_vars="Gate", value_vars=["Gate Flow(in)", "Gate Flow(out)"], 
                                            var_name="Flow Type", value_name="Jumlah")
                
                fig_gate = px.bar(
                    gate_melted, x="Gate", y="Jumlah",
                    color="Flow Type", barmode="group",
                    title="Perbandingan Volume Masuk vs Keluar",
                    color_discrete_map={"Gate Flow(in)": "#2E86C1", "Gate Flow(out)": "#E74C3C"}
                )
                # Pindahkan legenda ke atas agar hemat tempat
                fig_gate.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig_gate, use_container_width=True)
                
                # --- B. Scatter Plot (Dipindahkan ke SINI) ---
                st.markdown("---")
                st.markdown("##### ⚖️ Peta Karakteristik (In vs Out)")
                
                gate_scatter = df_flow.groupby("Gate")[["Gate Flow(in)", "Gate Flow(out)"]].sum().reset_index()
                gate_scatter['Total Volume'] = gate_scatter['Gate Flow(in)'] + gate_scatter['Gate Flow(out)']
                
                fig_scatter = px.scatter(
                    gate_scatter, 
                    x="Gate Flow(in)", y="Gate Flow(out)", 
                    size="Total Volume", color="Gate",
                    hover_name="Gate", text="Gate",
                    # Judul dihapus/dipendekkan karena sudah ada header markdown
                    labels={"Gate Flow(in)": "Inflow", "Gate Flow(out)": "Outflow"}
                )
                
                # Garis Diagonal
                max_val = max(gate_scatter["Gate Flow(in)"].max(), gate_scatter["Gate Flow(out)"].max())
                fig_scatter.add_shape(type="line", line=dict(dash="dash", color="gray"),
                    x0=0, y0=0, x1=max_val, y1=max_val)
                
                fig_scatter.update_traces(textposition='top center')
                fig_scatter.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0)) # Hemat margin
                
                st.plotly_chart(fig_scatter, use_container_width=True)
                
                st.caption("""
                **Cara Baca:**
                Garis putus-putus = Seimbang. 
                Titik di **Bawah** garis = Dominan Masuk (Entrance). 
                Titik di **Atas** garis = Dominan Keluar (Exit).
                """)

            else:
                st.warning("Data Gate kosong.")

    # --- 4. RAW DATA (Di paling bawah) ---
    st.markdown("---")
    with st.expander("📂 Lihat Data Mentah"):
        st.markdown("#### Data Area Traffic")
        st.dataframe(df_traffic, use_container_width=True)
        st.markdown("#### Data Gate Flow")
        st.dataframe(df_flow, use_container_width=True)
        
# ==============================
# 🚀 MAIN CONTROLLER
# ==============================
def main():
    
    # --- Sidebar ---
    with st.sidebar:
        st.header("⚙️ Data Control")
        if 'token' not in st.session_state: st.session_state.token = "Bearer ey..."
        if 'start_date' not in st.session_state: st.session_state.start_date = date.today()
        if 'end_date' not in st.session_state: st.session_state.end_date = date.today()

        st.session_state.token = st.text_input("Token", value=st.session_state.token, type="password")
        st.session_state.start_date = st.date_input("Start Date", value=st.session_state.start_date)
        st.session_state.end_date = st.date_input("End Date", value=st.session_state.end_date)
        
        st.markdown("---")
        
        if st.button("🚀 Kumpulkan Data", type="primary", use_container_width=True):
            start_slash = st.session_state.start_date.strftime("%Y/%m/%d")
            end_slash = st.session_state.end_date.strftime("%Y/%m/%d")
            
            with st.spinner("Downloading..."):
                os.makedirs(DATA_FOLDER, exist_ok=True)
                r1 = fetch_area_traffic(st.session_state.token, DEFAULT_USER_ID, start_slash, end_slash, DEFAULT_SITE_CODE)
                r2 = fetch_gate_flow(st.session_state.token, DEFAULT_USER_ID, start_slash, end_slash, DEFAULT_SITE_CODE)
            
            if r1 and r2:
                st.success("Done! Refreshing...")
                st.cache_data.clear()
                st.rerun()
        
        if st.button("🔄 Refresh Cache", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # --- Main Page ---
    st.markdown('<div style="text-align:center; font-size:2.6rem; font-weight:700;">🚶‍♂️ Traffic & Flow Analytics</div>', unsafe_allow_html=True)
    st.caption("Dashboard Monitoring Pergerakan Pengunjung Area & Gate")
    
    # File Check
    files_exist = os.path.exists(AREA_TRAFFIC_FILE) and os.path.exists(GATE_FLOW_FILE)
    
    if not files_exist:
        st.info("Data belum tersedia. Silakan masukkan Token dan klik tombol 'Kumpulkan Data' di sidebar.")
        st.stop()
        
    df_traffic, df_flow = load_data()
    
    if isinstance(df_traffic, str) or isinstance(df_flow, str):
        st.error(f"Error Loading Data: {df_traffic} | {df_flow}")
        st.stop()
        
    if df_traffic is None or df_flow is None:
        st.error("Dataframes are None.")
        st.stop()
        
    build_dashboard(df_traffic, df_flow)

if __name__ == "__main__":
    main()

