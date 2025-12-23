# ==========================================
# 🏬 AREA PERFORMANCE ANALYSIS (AI INTEGRATED - RAG)
# ==========================================
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
import os       
import requests    
from datetime import date 
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# --- IMPORT MODULE AI ---
import sys
sys.path.append('.') 
import ai_utils 

# ==============================
# ⚙️ CONFIG
# ==============================

st.set_page_config(
    page_title="Area Performance Analysis",
    page_icon="🏬",
    layout="wide"
)

DATA_FOLDER = "data"
PERFORMANCE_FILE = os.path.join(DATA_FOLDER, "area_performance_export.xlsx") 
DEFAULT_USER_ID = "4748ef52-ccb6-4dbe-acf4-1268d25123d8"
DEFAULT_SITE_CODE = "P00077"

# ==============================
# 📥 FUNGSI PENGAMBIL DATA
# ==============================
def fetch_area_performance_data(token, user_id, start_date_slash, end_date_slash, site_code):
    st.write("Mengambil Data Area Performance...")
    data_api_url = 'https://winnertech.hk:8090/api/en-us/ShopAreaHeat/ShopAreaAttentionDataExport'
    data_payload = {
        "userId": user_id, "lang": "en-us", "menuId": 3000201,
        "params": {
            "isClose": 0, "module": "BM00019S007", "dateType": "d",
            "beginDate": start_date_slash, "endDate": end_date_slash,
            "siteKey": site_code
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
            with open(PERFORMANCE_FILE, 'wb') as f:
                f.write(response.content)
            st.success(f"Sukses: File Area Performance ({PERFORMANCE_FILE}) disimpan.")
            return True
        else:
            st.error(f"Gagal: Server tidak mengembalikan file. Respons:\n{response.json()}")
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
        df = pd.read_excel(PERFORMANCE_FILE)
    except FileNotFoundError:
        return f"File '{PERFORMANCE_FILE}' tidak ditemukan."
    except Exception as e:
        return f"Gagal membaca file '{PERFORMANCE_FILE}'. Error: {e}"

    df.columns = [c.strip().title() for c in df.columns]
    
    rename_map = {
        "Store Area": "Store Area", 
        "Attendance": "Area Attendance",
        "Avg. Attention Time": "Avg. Attention Time (S)",
        "Dwell": "Dwell",
        "Interest": "Interest",
        "Tend To Buy": "Tend To Buy"
    }
    existing_cols_to_rename = {k: v for k, v in rename_map.items() if k in df.columns}
    df.rename(columns=existing_cols_to_rename, inplace=True)
    
    expected_cols = ["Store Area", "Area Attendance", "Avg. Attention Time (S)", "Dwell", "Interest", "Tend To Buy"]
    if not all(col in df.columns for col in expected_cols):
        return None

    return df

# ==========================================
# 🧠 FUNGSI PERINGKAS DATA UNTUK AI (ADVANCED)
# ==========================================
def generate_performance_summary(df, df_clusters_summary=None):
    """
    Meringkas performa area, tingkat konversi, dan karakteristik cluster.
    """
    if df.empty: return "Data Performance Kosong."

    # 1. Top Performers (Konversi Buying Rate Tertinggi)
    top_buying = df.sort_values("Buying Rate", ascending=False).head(3)
    # 2. Top Interest (Banyak yang minat tapi belum tentu beli)
    top_interest = df.sort_values("Interest Rate", ascending=False).head(3)
    
    # 3. Rata-rata Global
    avg_buying = df["Buying Rate"].mean()
    avg_interest = df["Interest Rate"].mean()
    avg_dwell_rate = df["Dwell Rate"].mean()

    # 4. Analisis Cluster (Jika ada)
    cluster_text = ""
    if df_clusters_summary is not None and not df_clusters_summary.empty:
        cluster_text = "\nKARAKTERISTIK CLUSTER (Berdasarkan Pola Data):\n"
        for idx, row in df_clusters_summary.iterrows():
            cluster_text += f"- {idx}: Dwell={row['Dwell']:.1f}, Interest={row['Interest']:.1f}, Buy={row['Tend To Buy']:.1f}\n"

    # Susun Teks Prompt
    summary_text = f"""
    ANALISIS PERFORMA AREA TOKO (PERFORMANCE & CLUSTERING):
    
    1. STATISTIK RATA-RATA TOKO:
    - Rata-rata Buying Rate (Konversi): {avg_buying:.1%}
    - Rata-rata Interest Rate (Minat): {avg_interest:.1%}
    - Rata-rata Dwell Rate: {avg_dwell_rate:.1%}
    
    2. AREA DENGAN KONVERSI PENJUALAN TERTINGGI (CHAMPIONS):
    (Area ini sangat efektif mengubah pengunjung menjadi pembeli)
    """
    for _, row in top_buying.iterrows():
        summary_text += f"- {row['Store Area']}: Buying Rate {row['Buying Rate']:.1%} (Total Visits: {row['Area Attendance']})\n"

    summary_text += """
    3. AREA DENGAN MINAT TERTINGGI (POTENTIAL):
    (Area ini menarik perhatian banyak orang)
    """
    for _, row in top_interest.iterrows():
        summary_text += f"- {row['Store Area']}: Interest Rate {row['Interest Rate']:.1%}\n"

    summary_text += cluster_text
    
    summary_text += """
    \nTUGAS AI:
    Berikan analisis mendalam tentang efektivitas layout toko. 
    Jika ada Cluster dengan Interest tinggi tapi Buying rendah, sarankan perbaikan.
    """
    
    return summary_text

# ===================================
# 🎁 FUNGSI UNTUK MEMBUNGKUS DASHBOARD
# ===================================
def build_dashboard(df):
    
    # ==============================
    # 🧮 DATA CLEANING
    # ==============================
    num_cols = ["Area Attendance", "Avg. Attention Time (S)", "Dwell", "Interest", "Tend To Buy"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=num_cols, inplace=True)
    
    if df.empty:
        st.error("Data kosong setelah dibersihkan.")
        st.stop()

    # ==============================
    # 🧠 FEATURE ENGINEERING
    # ==============================
    df["Dwell Rate"] = df["Dwell"] / df["Area Attendance"]
    df["Interest Rate"] = df["Interest"] / df["Area Attendance"]
    df["Buying Rate"] = df["Tend To Buy"] / df["Area Attendance"] 
    
    # ==============================
    # 📊 BAGIAN 1 — BEHAVIOR BREAKDOWN
    # ==============================
    st.subheader("📊 Komposisi Perilaku Pengunjung per Area")
    with st.container(border=True): 
        df_melted = df.melt(
            id_vars="Store Area", 
            value_vars=["Dwell Rate", "Interest Rate", "Buying Rate"], 
            var_name="Tipe Perilaku", 
            value_name="Proporsi"
        )
        sorted_areas = df.sort_values("Buying Rate", ascending=False)["Store Area"] 
        fig_stacked_bar = px.bar(
            df_melted, x="Store Area", y="Proporsi", color="Tipe Perilaku",
            title="Komposisi Perilaku Pengunjung di Setiap Area",
            color_discrete_map={
                'Dwell Rate': '#CCCCCC', 
                'Interest Rate': '#FFB703',
                'Buying Rate': '#02C39A' 
            },
            category_orders={"Store Area": sorted_areas}
        )
        fig_stacked_bar.update_layout(
            barmode='stack', yaxis_title="Proporsi Perilaku",
            yaxis_tickformat='.0%'
        )
        st.plotly_chart(fig_stacked_bar, use_container_width=True)

    st.markdown("---") 

    # ==============================
    # 🧩 BAGIAN 2 — CLUSTERING & AI
    # ==============================
    st.subheader("🧩 Cluster Area & Analisis AI")
    
    # --- PROSES CLUSTERING (Di luar container agar datanya bisa diambil AI) ---
    cluster_features = ["Dwell", "Interest", "Tend To Buy"]
    df_cluster_raw = df[["Store Area"] + cluster_features].dropna().reset_index(drop=True)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_cluster_raw[cluster_features])
    df_cluster = df_cluster_raw.copy()

    # Default settings untuk visualisasi
    reduction_method = "t-SNE" 
    optimal_k = 3

    # Logika Reduksi & K-Means (Otomatis jalan default k=3)
    perplexity_value = min(10, len(X_scaled) - 1)
    tsne = TSNE(n_components=2, perplexity=perplexity_value, random_state=42, learning_rate='auto')
    X_reduced = tsne.fit_transform(X_scaled)
    df_cluster["Dim1"], df_cluster["Dim2"] = X_reduced[:, 0], X_reduced[:, 1]
    
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    df_cluster["Cluster"] = kmeans.fit_predict(X_scaled)
    df_cluster.sort_values("Cluster", inplace=True)
    label_map = {i: f"Cluster {i+1}" for i in range(optimal_k)}
    df_cluster["Cluster Label"] = df_cluster["Cluster"].map(label_map)

    # Siapkan Data Summary Cluster untuk AI
    df_cluster_avg = df_cluster.groupby("Cluster Label")[cluster_features].mean().round(2)
    
    # --- UI UNTUK AI ANALYST ---
    with st.expander("✨ Tanya AI tentang Performa & Cluster Area Ini", expanded=False):
        c_ai1, c_ai2 = st.columns([3, 1])
        with c_ai1:
            q_options = [
                "Jelaskan karakteristik unik dari setiap Cluster.",
                "Area mana yang memiliki konversi penjualan terbaik dan kenapa?",
                "Strategi apa untuk meningkatkan 'Buying Rate' di area yang rendah?",
                "Tulis pertanyaan sendiri..."
            ]
            selected_q = st.selectbox("Pilih Pertanyaan:", q_options)
            if selected_q == "Tulis pertanyaan sendiri...":
                user_q = st.text_input("Ketik pertanyaanmu:", "Adakah anomali performa di area tertentu?")
            else:
                user_q = selected_q
        
        with c_ai2:
            st.write("") 
            st.write("") 
            tombol_tanya = st.button("Analisa Performa 🤖", type="primary", use_container_width=True)
            
        if tombol_tanya:
            with st.spinner("AI sedang membedah performa area & cluster..."):
                # 1. Ringkas data (Kirim DF utama & DF Cluster Summary)
                summary_text = generate_performance_summary(df, df_cluster_avg)
                # 2. Kirim ke AI
                jawaban_ai = ai_utils.analyze_with_gemini(summary_text, user_q)
                # 3. Tampilkan
                st.markdown("### 💡 Insight Performa:")
                st.markdown(jawaban_ai)
    
    st.markdown("---")

    # --- VISUALISASI CLUSTER ---
    with st.container(border=True): 
        palette = px.colors.qualitative.Bold
        unique_labels = sorted(df_cluster["Cluster Label"].unique())
        color_map_fixed = {label: palette[i % len(palette)] for i, label in enumerate(unique_labels)}

        df_viz = pd.merge(df_cluster, df[["Store Area", "Area Attendance"]], on="Store Area", how="left")
        
        # Radar Chart Prep
        df_radar = df_cluster.groupby("Cluster Label")[cluster_features].mean().reset_index()
        scaler_radar = MinMaxScaler(feature_range=(0.2, 1)) 
        df_radar_norm = df_radar.copy()
        if not df_radar.empty:
            df_radar_norm[cluster_features] = scaler_radar.fit_transform(df_radar[cluster_features])
        
        df_radar_melted = df_radar_norm.melt(id_vars="Cluster Label", var_name="Metrik", value_name="Nilai Skala")

        col_visual1, col_visual2 = st.columns([3, 2]) 

        with col_visual1:
            st.markdown(f"##### 🗺️ Peta Persebaran Area")
            fig_cluster_plot = px.scatter(
                df_viz, x="Dim1", y="Dim2", color="Cluster Label",
                size="Area Attendance", hover_name="Store Area",
                hover_data=cluster_features, color_discrete_map=color_map_fixed, height=500
            )
            fig_cluster_plot.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_cluster_plot, use_container_width=True)

        with col_visual2:
            st.markdown("##### 🕸️ Profil Cluster")
            fig_radar = px.line_polar(
                df_radar_melted, r="Nilai Skala", theta="Metrik", color="Cluster Label",
                line_close=True, color_discrete_map=color_map_fixed, height=450
            )
            fig_radar.update_traces(fill='toself', opacity=0.4) 
            fig_radar.update_layout(template="plotly_dark", polar=dict(bgcolor='rgba(0,0,0,0)'))
            st.plotly_chart(fig_radar, use_container_width=True)

        # Treemap
        st.markdown("##### 🏢 Detail Anggota Klaster")
        fig_treemap = px.treemap(
            df_viz, path=[px.Constant("Semua Area"), 'Cluster Label', 'Store Area'], 
            values='Area Attendance', color='Cluster Label', color_discrete_map=color_map_fixed
        )
        fig_treemap.update_layout(height=500)
        st.plotly_chart(fig_treemap, use_container_width=True)
        
        with st.expander("📂 Lihat Data Angka Rata-rata Cluster"):
            st.dataframe(df_cluster_avg.style.format("{:.2f}"), use_container_width=True)


# ==============================
# 🚀 MAIN (KONTROLER)
# ==============================
def main():
    with st.sidebar:
        st.header("⚙️ Kontrol Pengambilan Data")
        if 'token' not in st.session_state: st.session_state.token = "Bearer ey..."
        if 'start_date' not in st.session_state: st.session_state.start_date = date.today()
        if 'end_date' not in st.session_state: st.session_state.end_date = date.today()

        st.session_state.token = st.text_input("Authorization Token", value=st.session_state.token, type="password")
        st.session_state.start_date = st.date_input("Start Date", value=st.session_state.start_date)
        st.session_state.end_date = st.date_input("End Date", value=st.session_state.end_date)
        st.markdown("---")

        if st.button("🚀 Kumpulkan Data Performance", type="primary", use_container_width=True):
            start_slash = st.session_state.start_date.strftime("%Y/%m/%d")
            end_slash = st.session_state.end_date.strftime("%Y/%m/%d")
            with st.spinner("Mengambil data..."):
                os.makedirs(DATA_FOLDER, exist_ok=True)
                res1 = fetch_area_performance_data(st.session_state.token, DEFAULT_USER_ID, start_slash, end_slash, DEFAULT_SITE_CODE)
            if res1:
                st.success("Data berhasil diambil!")
                st.cache_data.clear()
                st.rerun()
        
        if st.button("🔄 Refresh Cache", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown('<div style="text-align:center; font-size:2.6rem; font-weight:700; margin-bottom:1.2rem;">🏬 Area Performance Analysis</div>', unsafe_allow_html=True)
    st.caption("Analisis perilaku pengunjung tiap area berdasarkan metrik engagement dan konversi.")

    if not os.path.exists(PERFORMANCE_FILE):
        st.info("Data belum tersedia. Silakan 'Kumpulkan Data' di sidebar.")
        st.stop()
        
    df_perf = load_data() 
    if isinstance(df_perf, str): 
        st.error(df_perf)
        st.stop()
    if df_perf is None or df_perf.empty: 
        st.error("Gagal memvalidasi data.")
        st.stop()

    build_dashboard(df_perf)

if __name__ == "__main__":
    main()
