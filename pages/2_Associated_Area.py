# =====================================
# 🕸️ ASSOCIATED AREA TRAFFIC ANALYSIS (AI ALL METRICS)
# =====================================
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os       
import requests 
from datetime import date 

# --- IMPORT MODULE AI ---
import sys
sys.path.append('.') 
import ai_utils 

# =========================
# ⚙️ CONFIG
# =========================

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
    try:
        df = pd.read_excel(ASSOCIATION_FILE)
    except FileNotFoundError:
        return f"File '{ASSOCIATION_FILE}' tidak ditemukan."
    except Exception as e:
        return f"Gagal membaca file '{ASSOCIATION_FILE}'. Error: {e}"

    df.columns = [c.strip().title() for c in df.columns]
    
    # Mapping nama kolom
    rename_map = {
        "Store Area": "Store area",       
        "Associated Area": "Associated area", 
        "Shared Traffic": "Shared traffic"    
    }
    existing_cols_to_rename = {k: v for k, v in rename_map.items() if k in df.columns}
    df.rename(columns=existing_cols_to_rename, inplace=True)

    if "Store area" not in df.columns or "Associated area" not in df.columns or "Shared traffic" not in df.columns:
        return None 

    df["Shared traffic"] = pd.to_numeric(df["Shared traffic"], errors="coerce").fillna(0)
    return df

def calculate_metrics(df_assoc):
    if df_assoc.empty: return pd.DataFrame()
    
    total_shared_traffic = df_assoc["Shared traffic"].sum()
    
    # Menghitung total traffic per toko asal (Store area)
    traffic_from_store = df_assoc.groupby("Store area")["Shared traffic"].sum()
    # Menghitung total traffic per toko tujuan (Associated area)
    traffic_to_associated = df_assoc.groupby("Associated area")["Shared traffic"].sum()
    
    # Hitung Probabilitas P(A) dan P(B)
    # P(A) = Peluang seseorang berada di Store Area A
    prob_store = traffic_from_store / total_shared_traffic
    # P(B) = Peluang seseorang berada di Associated Area B
    prob_associated = traffic_to_associated / total_shared_traffic
    
    df_metrics = df_assoc.copy()
    
    # Mapping nilai probabilitas ke dataframe
    df_metrics["P(A)"] = df_metrics["Store area"].map(prob_store)
    df_metrics["P(B)"] = df_metrics["Associated area"].map(prob_associated)
    
    # 1. Support = P(A ∩ B) = Seberapa sering A dan B dikunjungi bersamaan dibanding total traffic
    df_metrics["Support"] = df_metrics["Shared traffic"] / total_shared_traffic 
    
    # 2. Confidence = P(B|A) = Jika di A, berapa % lanjut ke B?
    # Rumus: Support / P(A)
    df_metrics["Confident"] = df_metrics["Support"] / df_metrics["P(A)"]
    
    # 3. Lift = P(B|A) / P(B) = Seberapa kuat hubungan dibanding kebetulan
    df_metrics["Lift"] = df_metrics["Confident"] / df_metrics["P(B)"]
    
    df_metrics.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_metrics.fillna(0, inplace=True)
    
    return df_metrics.sort_values("Lift", ascending=False)

# ==========================================
# 🧠 FUNGSI PERINGKAS DATA UNTUK AI (LENGKAP)
# ==========================================
def generate_association_summary(df):
    """
    Meringkas 4 metrik utama (Lift, Confidence, Support, Shared Traffic) untuk AI.
    """
    if df.empty: return "Data Asosiasi Kosong."

    # 1. Analisis LIFT (Kekuatan Hubungan Murni)
    top_lift = df.sort_values("Lift", ascending=False).head(5)
    
    # 2. Analisis CONFIDENCE (Peluang Arah Pergerakan)
    top_conf = df.sort_values("Confident", ascending=False).head(5)
    
    # 3. Analisis SUPPORT (Popularitas Kombinasi)
    top_support = df.sort_values("Support", ascending=False).head(5)

    # Buat teks narasi yang kaya konteks
    summary_text = """
    DATA ANALISIS ASOSIASI ANTAR AREA (MARKET BASKET ANALYSIS):
    
    1. HUBUNGAN TERKUAT (METRIK LIFT):
    (Lift > 1 berarti hubungan kuat & bukan kebetulan. Area ini saling melengkapi.)
    """
    for idx, row in top_lift.iterrows():
        summary_text += f"- {row['Store area']} -> {row['Associated area']} (Lift: {row['Lift']:.2f})\n"

    summary_text += "\n2. PELUANG PERPINDAHAN TERTINGGI (METRIK CONFIDENCE):\n"
    summary_text += "(Jika pengunjung ada di Area A, sekian % PASTI pergi ke Area B. Gunakan untuk signage/arahan.)\n"
    for idx, row in top_conf.iterrows():
        conf_pct = row['Confident'] * 100
        summary_text += f"- Jika di {row['Store area']}, {conf_pct:.1f}% lanjut ke {row['Associated area']}\n"

    summary_text += "\n3. KOMBINASI TERPOPULER (METRIK SUPPORT & TRAFFIC):\n"
    summary_text += "(Pasangan area ini paling banyak menyumbang keramaian di toko.)\n"
    for idx, row in top_support.iterrows():
        summary_text += f"- {row['Store area']} & {row['Associated area']} (Traffic Bersama: {row['Shared traffic']} orang)\n"

    return summary_text

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

        st.session_state.token = st.text_input("Authorization Token", value=st.session_state.token, type="password")
        st.session_state.start_date = st.date_input("Start Date", value=st.session_state.start_date)
        st.session_state.end_date = st.date_input("End Date", value=st.session_state.end_date)
        st.markdown("---")

        if st.button("🚀 Kumpulkan Data Asosiasi", type="primary", use_container_width=True):
            start_slash = st.session_state.start_date.strftime("%Y/%m/%d")
            end_slash = st.session_state.end_date.strftime("%Y/%m/%d")
            with st.spinner("Mengambil data..."):
                os.makedirs(DATA_FOLDER, exist_ok=True)
                res1 = fetch_association_data(st.session_state.token, DEFAULT_USER_ID, start_slash, end_slash, DEFAULT_SITE_CODE)
            if res1:
                st.success("Data berhasil diambil!")
                st.cache_data.clear()
                st.rerun()
        
        if st.button("🔄 Refresh Cache", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # --- 2. TAMPILKAN DASHBOARD ---
    st.markdown('<div style="text-align:center; font-size:2.6rem; font-weight:700; margin-bottom:1.2rem;">🕸️ Associated Area Analysis</div>', unsafe_allow_html=True)
    st.markdown("Analisis hubungan antar area: Ke mana pengunjung pergi setelah dari suatu tempat?")

    if not os.path.exists(ASSOCIATION_FILE):
        st.info("Data belum tersedia. Silakan 'Kumpulkan Data' di sidebar.")
        st.stop()
        
    df_assoc_raw = load_data() 
    if isinstance(df_assoc_raw, str): 
        st.error(df_assoc_raw)
        st.stop()
    if df_assoc_raw is None: 
        st.error("Validasi kolom gagal.")
        st.stop()

    # --- 3. HITUNG METRIK ---
    df_results_sorted = calculate_metrics(df_assoc_raw)
    
    if df_results_sorted.empty:
        st.warning("Data asosiasi kosong.")
        st.stop()

    # ==========================================
    # ✨ FITUR AI ANALYST (LENGKAP)
    # ==========================================
    st.markdown("---")
    with st.expander("✨ Tanya AI tentang Hubungan Antar Area", expanded=False):
        c_ai1, c_ai2 = st.columns([3, 1])
        with c_ai1:
            q_options = [
                "Area mana yang memiliki 'Confidence' tertinggi (paling pasti dikunjungi)?",
                "Jelaskan perbedaan antara pasangan dengan Lift tinggi vs Support tinggi.",
                "Rekomendasi penempatan produk berdasarkan data Confidence.",
                "Tulis pertanyaan sendiri..."
            ]
            selected_q = st.selectbox("Pilih Pertanyaan:", q_options)
            if selected_q == "Tulis pertanyaan sendiri...":
                user_q = st.text_input("Ketik pertanyaanmu:", "Adakah anomali dalam pola pergerakan pengunjung?")
            else:
                user_q = selected_q
        
        with c_ai2:
            st.write("") 
            st.write("") 
            tombol_tanya = st.button("Analisa Hubungan 🤖", type="primary", use_container_width=True)
            
        if tombol_tanya:
            with st.spinner("AI sedang menganalisis Lift, Confidence, dan Support..."):
                # 1. Ringkas data
                summary_text = generate_association_summary(df_results_sorted)
                # 2. Kirim ke AI
                jawaban_ai = ai_utils.analyze_with_gemini(summary_text, user_q)
                # 3. Tampilkan
                st.markdown("### 💡 Insight Asosiasi:")
                st.markdown(jawaban_ai)
    st.markdown("---")

    # --- 4. VISUALISASI TREEMAP ---
    with st.container(border=True):
        st.subheader("🌳 Treemap Metrik Asosiasi")
        
        col_metric, col_dummy = st.columns([1, 2])
        with col_metric:
            metric_choice = st.selectbox(
                "Pilih Metrik untuk Ukuran Treemap:",
                ['Lift', 'Confident', 'Support', 'Shared traffic'],
                format_func=lambda x: f"{x} ({'Kekuatan' if x=='Lift' else 'Peluang' if x=='Confident' else 'Popularitas' if x=='Support' else 'Volume'})"
            )
        
        df_treemap = df_results_sorted[df_results_sorted[metric_choice] > 0.00001].copy()
        
        if df_treemap.empty:
            st.warning(f"Tidak ada data untuk metrik '{metric_choice}' > 0.")
        else:
            df_treemap["Root"] = "Semua Relasi" 
            fig_tree = px.treemap(
                df_treemap,
                path=['Root', 'Store area', 'Associated area'],
                values=metric_choice, 
                color=metric_choice,
                color_continuous_scale='YlOrRd',
                title=f"Peta Hubungan Berdasarkan {metric_choice}"
            )
            fig_tree.update_traces(textinfo="label+value", root_color="rgba(0,0,0,0)")
            fig_tree.update_layout(height=650, margin=dict(t=30, l=10, r=10, b=10))
            st.plotly_chart(fig_tree, use_container_width=True)

    with st.expander("Lihat Data Mentah (Metrics)"):
        st.dataframe(df_results_sorted, use_container_width=True)

    st.caption("© 2025 Associated Area Analytics")

if __name__ == "__main__":
    main()
