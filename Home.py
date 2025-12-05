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

# 🛠️ FUNGSI PEMBUAT KARTU (Solusi agar Rata)
def make_card(title_emoji, title_text, desc_text, link_path):
    # Gunakan container dengan tinggi TETAP (Fixed Height)
    with st.container(border=True, height=420):
        
        # 1. JUDUL (Header)
        # Kita beri sedikit margin bawah agar rapi
        st.markdown(f"### {title_emoji} {title_text}")

        # 2. DESKRIPSI (Fixed Height Box)
        # Kita PAKSA area ini tingginya 130px.
        # Jika teks pendek, sisa ruang kosong akan mengisi ke bawah.
        # Jika teks panjang, akan terpotong rapi (atau bisa di-scroll jika overflow auto).
        st.markdown(f"""
        <div style="
            height: 130px; 
            min-height: 130px;
            overflow: hidden; 
            font-size: 0.9rem; 
            color: #e0e0e0;
            margin-bottom: 10px;
        ">
            {desc_text}
        </div>
        """, unsafe_allow_html=True)

        # 3. DIVIDER (Garis Pemisah)
        # Karena elemen di atasnya tingginya dikunci, garis ini pasti sejajar.
        st.divider()

        # 4. TOMBOL
        st.page_link(link_path, label="Buka Modul ➔", use_container_width=True)


# --- PENERAPAN LAYOUT (Lebih Bersih & Rapi) ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    make_card(
        "👥", "Customer", 
        "Siapa yang datang? Analisis demografi, gender, usia, dan *dwell time* secara mendalam.",
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

