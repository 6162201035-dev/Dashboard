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

# --- CSS Tambahan untuk Tampilan Lebih Interaktif ---
st.markdown("""
<style>
    /* Efek Hover pada Container Menu */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        transition: all 0.3s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #FF4B4B !important; /* Warna aksen saat hover */
        transform: translateY(-5px); /* Efek naik sedikit */
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- Judul Halaman Utama (Hero Section) ---
st.markdown('<div style="text-align:center; font-size:3rem; font-weight:800; margin-bottom:0.5rem;">AI Traffic Data Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; font-size:1.2rem; color:#888; margin-bottom:2rem;">Pusat kendali analisis data pengunjung, pola pergerakan, dan performa area secara real-time.</div>', unsafe_allow_html=True)

st.markdown("---")

# --- Konten Utama (Menu Navigasi 5 Kolom) ---
st.subheader("📂 Pilih Modul Analisis")

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
