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

# --- CSS Tambahan ---
st.markdown("""
<style>
    /* Efek Hover pada Container */
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

# --- Konten Utama (Menu Navigasi) ---
st.subheader("📂 Pilih Modul Analisis")

# --- PERBAIKAN UTAMA DI SINI ---
def card_desc(text):
    # Height 140px: Cukup untuk 5-6 baris teks.
    # Font-size 0.9rem: Sedikit lebih kecil agar muat banyak.
    return st.markdown(f"""
    <div style="
        height: 140px; 
        overflow: hidden; 
        display: flex; 
        align-items: flex-start; 
        font-size: 0.9rem;
        line-height: 1.5; 
        margin-bottom: 5px;">
        {text}
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

# --- MODUL 1 ---
with col1:
    with st.container(border=True, height=400): # Height container sedikit dinaikkan ke 400 biar aman
        st.markdown("### 👥 Customer")
        card_desc("Siapa yang datang? Analisis demografi, gender, usia, dan dwell time secara mendalam.")
        st.divider()
        st.page_link("pages/1_Customer_Profile.py", label="Buka Modul ➔", use_container_width=True)

# --- MODUL 2 ---
with col2:
    with st.container(border=True, height=400):
        st.markdown("### 🔗 Relation")
        card_desc("Bagaimana pergerakannya? Analisis korelasi dan hubungan antar area yang saling berasosiasi.")
        st.divider()
        st.page_link("pages/2_Associated_Area.py", label="Buka Modul ➔", use_container_width=True) 

# --- MODUL 3 ---
with col3:
    with st.container(border=True, height=400):
        st.markdown("### 🏬 Potency")
        card_desc("Area mana yang potensial? Analisis tingkat konversi dan perilaku belanja pengunjung.")
        st.divider()
        st.page_link("pages/3_Area_Performance.py", label="Buka Modul ➔", use_container_width=True) 

# --- MODUL 4 ---
with col4:
    with st.container(border=True, height=400):
        st.markdown("### ⏳ Period")
        card_desc("Kapan waktu tersibuk? Tren trafik pengunjung per jam & hari dalam seminggu.")
        st.divider()
        st.page_link("pages/4_Time_Period_Traffic_Flow.py", label="Buka Modul ➔", use_container_width=True)
        
# --- MODUL 5 ---
with col5:
    with st.container(border=True, height=400):
        st.markdown("### 🚦 Traffic")
        card_desc("Berapa banyak yang lewat? Flow gabungan Gerbang & Area (In vs Out).")
        st.divider()
        st.page_link("pages/5_Area_Traffic_Gate_Flow.py", label="Buka Modul ➔", use_container_width=True)

st.markdown("---") 

# --- Footer ---
st.markdown("""
<div style="text-align:center; color:#666;">
    <small>© 2025 Data Analysis Dashboard | Dibentuk oleh N. | v1.0 Stable</small>
</div>
""", unsafe_allow_html=True)

