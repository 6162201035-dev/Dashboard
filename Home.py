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

# --- Judul halaman utama ---
st.markdown('<div style="text-align:center; font-size:2.6rem; font-weight:700; margin-bottom:1.2rem;">AI Traffic Data Dashboard</div>', unsafe_allow_html=True)
st.markdown("---")

# --- Konten utama halaman Home ---
st.subheader("Daftar Modul Analisis Data")

# --- PERBAIKAN: Layout 5 Kolom ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    with st.container(border=True, height=350): # Buat lebih tinggi
        st.markdown("### 1. 👥 Customer")
        st.markdown("Analisis demografi pelanggan, cuaca, dan *dwell time*.")
        st.page_link("Dahsboard/pages/1_Customer_Profile.py", label="Buka ➔", use_container_width=True)

with col2:
    with st.container(border=True, height=350):
        st.markdown("### 2. 🔗 Relation")
        st.markdown("Analisis hubungan antara area yang saling berasosiasi.")
        st.page_link("Dahsboard/pages/2_Associated_Area.py", label="Buka ➔", use_container_width=True) 

with col3:
    with st.container(border=True, height=350):
        st.markdown("### 3. 🏬 Potency")
        st.markdown("Analisis potensi perilaku pelanggan di setiap area.")
        st.page_link("Dahsboard/pages/3_Area_Performance.py", label="Buka ➔", use_container_width=True) 

with col4:
    with st.container(border=True, height=350):
        st.markdown("### 4. ⏳ Period")
        st.markdown("Analisis pola pelanggan terhadap waktu per jam dan hari.")
        st.page_link("Dahsboard/pages/4_Time_Period_Traffic_Flow.py", label="Buka ➔", use_container_width=True)
        
with col5:
    with st.container(border=True, height=350):
        st.markdown("### 5. 🚦 Traffic")
        st.markdown("Analisis traffic dan flow gabungan untuk Area dan Gerbang.")
        st.page_link("Dahsboard/pages/5_Area_Traffic_Gate_Flow.py", label="Buka ➔", use_container_width=True)

st.markdown("---") 

# --- Catatan kecil di bawah ---
st.markdown("""
<small>© 2025 Data Analysis Dashboard | Dibentuk oleh N .</small>

""", unsafe_allow_html=True)

