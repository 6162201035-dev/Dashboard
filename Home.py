# ================================
# 🏠 HOME PAGE (MAIN DASHBOARD)
# ================================
import streamlit as st

# --- Konfigurasi dasar halaman ---
st.set_page_config(
    page_title="Data Analysis Dashboard",
    page_icon="🏠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Tambahan (Hover Effect) ---
st.markdown("""
<style>
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #FF4B4B !important;
        transform: translateY(-5px);
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# --- Judul Halaman ---
st.markdown('<div style="text-align:center; font-size:3rem; font-weight:800; margin-bottom:0.5rem;">AI Traffic Data Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; font-size:1.2rem; color:#888; margin-bottom:2rem;">Pusat kendali analisis data pengunjung, pola pergerakan, dan performa area secara real-time.</div>', unsafe_allow_html=True)
st.markdown("---")

# --- Konten Utama ---
st.subheader("📂 Pilih Modul Analisis")

# 🛠️ FUNGSI PEMBUAT KARTU (V3 - PIXEL PERFECT)
def make_card(title_emoji, title_text, desc_text, link_path):
    # Container Utama
    with st.container(border=True, height=400):
        
        # 1. BLOK KONTEN (Judul + Deskripsi digabung)
        # Kita kunci total tingginya di 220px.
        # Judul dikunci min-height 50px (muat 2 baris).
        # Deskripsi mengisi sisa ruang tapi dikunci layout-nya.
        st.markdown(f"""
        <div style="height: 220px; display: flex; flex-direction: column;">
            <div style="
                min-height: 60px; 
                display: flex; 
                align-items: center; 
                font-weight: 700; 
                font-size: 1.3rem; 
                margin-bottom: 10px;
                line-height: 1.2;
            ">
                <span style="margin-right: 8px;">{title_emoji}</span> {title_text}
            </div>
            
            <div style="
                flex-grow: 1; 
                font-size: 0.9rem; 
                color: #dcdcdc; 
                overflow: hidden; 
                text-overflow: ellipsis;
                line-height: 1.5;
            ">
                {desc_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. DIVIDER (Pasti sejajar karena HTML di atas tingginya dikunci 220px)
        st.divider()

        # 3. TOMBOL
        st.page_link(link_path, label="Buka Modul ➔", use_container_width=True)


# --- PENERAPAN LAYOUT ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    make_card(
        "👥", "Customer", 
        "Siapa yang datang? Analisis demografi, gender, usia, dan <i>dwell time</i> secara mendalam.",
        "pages/1_Customer_Profile.py"
    )

with col2:
    make_card(
        "🔗", "Relation", 
        "Bagaimana pergerakannya? Analisis korelasi dan hubungan antar area yang saling berasosiasi.",
        "pages/2_Associated_Area.py"
    )

with col3:
    make_card(
        "🏬", "Potency", 
        "Area mana yang potensial? Analisis tingkat konversi dan perilaku belanja pengunjung.",
        "pages/3_Area_Performance.py"
    )

with col4:
    make_card(
        "⏳", "Period", 
        "Kapan waktu tersibuk? Tren trafik pengunjung per jam & hari dalam seminggu.",
        "pages/4_Time_Period_Traffic_Flow.py"
    )

with col5:
    make_card(
        "🚦", "Traffic", 
        "Berapa banyak yang lewat? Flow gabungan Gerbang & Area (In vs Out).",
        "pages/5_Area_Traffic_Gate_Flow.py"
    )

st.markdown("---") 

# --- Footer ---
st.markdown("""
<div style="text-align:center; color:#666;">
    <small>© 2025 Data Analysis Dashboard | Dibentuk oleh N. | v1.0 Stable</small>
</div>
""", unsafe_allow_html=True)
