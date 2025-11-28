# ==========================================
# 🏬 AREA PERFORMANCE ANALYSIS (FOKUS CLUSTERING & BREAKDOWN)
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
# 📥 FUNGSI PENGAMBIL DATA (Tidak Berubah)
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
# 📂 LOAD DATA (Tidak Berubah)
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
    
    # !! PENTING: PERBARUI RENAME MAP SESUAI EXCEL ANDA !!
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
        st.error("Gagal memproses file Excel. Nama kolom tidak sesuai.")
        st.info(f"Nama kolom yang diharapkan (setelah di-rename): {expected_cols}")
        st.warning("Silakan perbarui 'rename_map' di dalam kode 'load_data()' agar sesuai dengan file Excel.")
        st.dataframe(df.head()) 
        return None

    return df

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
        st.error("Data kosong setelah dibersihkan. Tidak ada yang bisa ditampilkan.")
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

    st.markdown("---") # Pemisah

    # ==============================
    # 🧩 BAGIAN 2 — CLUSTERING (CONSISTENT COLOR FIX)
    # ==============================
    st.subheader("🧩 Cluster Area Berdasarkan Perilaku Pengunjung")
    
    with st.container(border=True): 
        # --- Fitur & Skala Data ---
        cluster_features = ["Dwell", "Interest", "Tend To Buy"]
        df_cluster_raw = df[["Store Area"] + cluster_features].dropna().reset_index(drop=True)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_cluster_raw[cluster_features])
        df_cluster = df_cluster_raw.copy()

        # --- 1. Kontrol di Expander ---
        with st.expander("Pengaturan Klasterisasi & Visualisasi", expanded=False):
            control_col1, control_col2 = st.columns(2)
            with control_col1:
                reduction_method = st.radio(
                    "Pilih metode reduksi dimensi:",
                    ["PCA (Stabil)", "t-SNE (Non-linier)"],
                    index=1, horizontal=True,
                    key="cluster_reduction_method"
                )
            with control_col2:
                optimal_k = st.slider("Pilih jumlah cluster (k):", 2, 8, 3, key="cluster_k_slider")

        # --- 2. Logika Reduksi Dimensi ---
        if reduction_method.startswith("PCA"):
            pca = PCA(n_components=2, random_state=42)
            X_reduced = pca.fit_transform(X_scaled)
            df_cluster["Dim1"], df_cluster["Dim2"] = X_reduced[:, 0], X_reduced[:, 1]
            method_used = "PCA"
        else:
            perplexity_value = min(10, len(X_scaled) - 1)
            tsne = TSNE(n_components=2, perplexity=perplexity_value, random_state=42, learning_rate='auto')
            X_reduced = tsne.fit_transform(X_scaled)
            df_cluster["Dim1"], df_cluster["Dim2"] = X_reduced[:, 0], X_reduced[:, 1]
            method_used = "t-SNE"
            
        # --- 3. Logika Klasterisasi ---
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        df_cluster["Cluster"] = kmeans.fit_predict(X_scaled)
        # Sorting agar label selalu urut (Cluster 1, Cluster 2, ...)
        df_cluster.sort_values("Cluster", inplace=True)
        label_map = {i: f"Cluster {i+1}" for i in range(optimal_k)}
        df_cluster["Cluster Label"] = df_cluster["Cluster"].map(label_map)

        # --- 4. MEMBUAT KONSISTENSI WARNA (COLOR MAPPING) ---
        # Ini bagian penting agar Cluster 1 selalu Merah, Cluster 2 Selalu Biru, dst.
        # Kita ambil palet warna 'Bold' dari Plotly
        palette = px.colors.qualitative.Bold
        unique_labels = sorted(df_cluster["Cluster Label"].unique())
        
        # Buat kamus: {'Cluster 1': '#Warna1', 'Cluster 2': '#Warna2'}
        color_map_fixed = {
            label: palette[i % len(palette)] 
            for i, label in enumerate(unique_labels)
        }

        # --- 5. VISUALISASI (DENGAN WARNA KONSISTEN) ---
        
        # --- PERSIAPAN DATA ---
        df_viz = pd.merge(df_cluster, df[["Store Area", "Area Attendance"]], on="Store Area", how="left")
        
        # Data Radar Chart
        df_radar = df_cluster.groupby("Cluster Label")[cluster_features].mean().reset_index()
        scaler_radar = MinMaxScaler(feature_range=(0.2, 1)) 
        df_radar_norm = df_radar.copy()
        if not df_radar.empty:
            df_radar_norm[cluster_features] = scaler_radar.fit_transform(df_radar[cluster_features])
        
        df_radar_melted = df_radar_norm.melt(
            id_vars="Cluster Label", 
            var_name="Metrik", 
            value_name="Nilai Skala"
        )

        # --- LAYOUT VISUALISASI ---
        st.markdown("### 🔍 Analisis Detail Klaster")
        col_visual1, col_visual2 = st.columns([3, 2]) 

        # --- VISUAL 1: BUBBLE CHART (PETA) ---
        with col_visual1:
            st.markdown(f"##### 🗺️ Peta Persebaran Area ({method_used} 2D)")
            st.caption("Posisi berdekatan = Karakter mirip. Besar lingkaran = Jumlah Pengunjung.")
            
            fig_cluster = px.scatter(
                df_viz, 
                x="Dim1", 
                y="Dim2", 
                color="Cluster Label",
                size="Area Attendance", 
                hover_name="Store Area",
                hover_data=cluster_features,
                color_discrete_map=color_map_fixed, # <--- PAKAI COLOR MAP
                height=500
            )
            fig_cluster.update_layout(
                template="plotly_dark", 
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""), 
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=""),
                legend=dict(orientation="h", y=1.1) 
            )
            st.plotly_chart(fig_cluster, use_container_width=True)

        # --- VISUAL 2: RADAR CHART (PROFIL) ---
        with col_visual2:
            st.markdown("##### 🕸️ Profil Karakteristik")
            st.caption("Pola metrik rata-rata (Bentuk Segitiga = Karakter).")
            
            fig_radar = px.line_polar(
                df_radar_melted, 
                r="Nilai Skala", 
                theta="Metrik", 
                color="Cluster Label",
                line_close=True,
                color_discrete_map=color_map_fixed, # <--- PAKAI COLOR MAP SAMA
                height=450,
            )
            fig_radar.update_traces(fill='toself', opacity=0.4) 
            fig_radar.update_layout(
                template="plotly_dark",
                polar=dict(
                    radialaxis=dict(visible=True, showticklabels=False, range=[0, 1]), 
                    bgcolor='rgba(0,0,0,0)'
                ),
                legend=dict(orientation="h", y=-0.1),
                margin=dict(t=20, b=20)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        # --- VISUAL 3: TREEMAP (HIERARKI) ---
        st.markdown("---")
        st.markdown("##### 🏢 Detail Anggota Klaster (Treemap)")
        
        fig_treemap = px.treemap(
            df_viz, 
            path=[px.Constant("Semua Area"), 'Cluster Label', 'Store Area'], 
            values='Area Attendance',
            color='Cluster Label',
            color_discrete_map=color_map_fixed, # <--- PAKAI COLOR MAP SAMA
        )
        fig_treemap.update_layout(height=500, margin=dict(t=20, l=10, r=10, b=10))
        st.plotly_chart(fig_treemap, use_container_width=True)

        # --- TABEL DATA RAW ---
        with st.expander("📂 Lihat Rata-rata Angka Asli"):
            df_cluster_avg = df_cluster.groupby("Cluster Label")[cluster_features].mean().round(2)
            st.dataframe(df_cluster_avg.style.format("{:.2f}"), use_container_width=True)


# ==============================
# 🚀 MAIN (KONTROLER) (Tidak Berubah)
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

        if st.button("🚀 Kumpulkan Data Area Performance", type="primary", use_container_width=True):
            
            start_date_slash = st.session_state.start_date.strftime("%Y/%m/%d")
            end_date_slash = st.session_state.end_date.strftime("%Y/%m/%d")
            
            with st.spinner("Mengambil data..."):
                os.makedirs(DATA_FOLDER, exist_ok=True)
                res1 = fetch_area_performance_data(
                    st.session_state.token, DEFAULT_USER_ID, 
                    start_date_slash, end_date_slash, DEFAULT_SITE_CODE
                )
            
            if res1:
                st.success("Data Area Performance berhasil diambil!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Pengambilan data Area Performance gagal.")
        
        st.markdown("---")
        if st.button("🔄 Muat Ulang Data (Refresh)", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # --- 2. TAMPILKAN DASHBOARD ---
    
    st.markdown('<div style="text-align:center; font-size:2.6rem; font-weight:700; margin-bottom:1.2rem;">🏬 Area Performance Analysis</div>', unsafe_allow_html=True)
    st.caption("Analisis perilaku pengunjung tiap area berdasarkan metrik engagement dan konversi.")

    if not os.path.exists(PERFORMANCE_FILE):
        st.info("👋 Selamat datang! Data Area Performance tidak ditemukan. Silakan isi parameter di sidebar kiri dan klik 'Kumpulkan Data' untuk memulai.")
        st.stop()
        
    df_perf = load_data() 
    
    if isinstance(df_perf, str): 
        st.error(df_perf)
        st.stop()
    if df_perf is None or df_perf.empty: 
        st.error("Gagal memvalidasi data atau data kosong.")
        st.stop()

    # Jika data berhasil di-load, jalankan semua visualisasi
    build_dashboard(df_perf)


# --- Jalankan Fungsi Utama ---
if __name__ == "__main__":
    main()
