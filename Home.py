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

# --- CSS Styling untuk Kartu ---
# Kita buat class CSS khusus '.card-box' agar tampilan mirip container Streamlit
st.markdown("""
<style>
    /* Styling dasar kartu HTML */
    .card-box {
        border: 1px solid rgba(250, 250, 250, 0.2); /* Border halus */
        border-radius: 8px;
        padding: 20px;
        height: 250px; /* Tinggi Tetap */
        background-color: transparent;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    /* Efek Hover: Border menyala & naik sedikit */
    .card-box:hover {
        border-color: #FF4B4B;
        background-color: rgba(255, 75, 75, 0.05); /* Sedikit tint merah */
        transform: translateY(-5px);
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
        cursor: pointer;
    }

    /* Styling Teks agar tidak berubah warna jadi biru link */
    a.card-link {
        text-decoration: none;
        color: inherit !important;
    }

    /* Judul Kartu */
    .card-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 10px;
        color: #ffffff;
        display: flex;
        align-items: center;
    }

    /* Deskripsi Kartu */
    .card-desc {
        font-size: 0.9rem;
        color: #d0d0d0;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# --- Judul Halaman ---
st.markdown('<div style="text-align:center; font-size:3rem; font-weight:800; margin-bottom:0.5rem;">AI Traffic Data Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; font-size:1.2rem; color:#888; margin-bottom:2rem;">Pusat kendali analisis data pengunjung, pola pergerakan, dan performa area secara real-time.</div>', unsafe_allow_html=True)
st.markdown("---")

# --- Konten Utama ---
st.subheader("📂 Pilih Modul Analisis")

# 🛠️ FUNGSI PEMBUAT CLICKABLE CARD (HTML)
def make_clickable_card(emoji, title, desc, link_href):
    # link_href: Nama page di URL (biasanya nama file tanpa 'pages/' dan tanpa '.py')
    # Contoh: 'pages/1_Customer_Profile.py' -> href-nya biasanya 'Customer_Profile'
    
    html_code = f"""
    <a href="{link_href}" target="_self" class="card-link">
        <div class="card-box">
            <div class="card-title">
                <span style="margin-right: 10px;">{emoji}</span> {title}
            </div>
            <div class="card-desc">
                {desc}
            </div>
        </div>
    </a>
    """
    st.markdown(html_code, unsafe_allow_html=True)


# --- PENERAPAN LAYOUT ---
col1, col2, col3, col4, col5 = st.columns(5)

# PENTING: Pastikan 'link_href' sesuai dengan URL browser saat Anda membuka halaman tersebut.
# Biasanya Streamlit menghapus angka urutan (1_, 2_) di URL, tapi kadang tidak.
# Coba cek URL browser Anda saat buka page Customer Profile, misal: "localhost:8501/Customer_Profile"
# Maka isi href="Customer_Profile"

with col1:
    make_clickable_card(
        "👥", "Customer", 
        "Siapa yang datang? Analisis demografi, gender, usia, dan <i>dwell time</i> secara mendalam.",
        "Customer_Profile" 
    )

with col2:
    make_clickable_card(
        "🔗", "Relation", 
        "Bagaimana pergerakannya? Analisis korelasi dan hubungan antar area yang saling berasosiasi.",
        "Associated_Area"
    )

with col3:
    make_clickable_card(
        "🏬", "Potency", 
        "Area mana yang potensial? Analisis tingkat konversi dan perilaku belanja pengunjung.",
        "Area_Performance"
    )

with col4:
    make_clickable_card(
        "⏳", "Period", 
        "Kapan waktu tersibuk? Tren trafik pengunjung per jam & hari dalam seminggu.",
        "Time_Period_Traffic_Flow"
    )

with col5:
    make_clickable_card(
        "🚦", "Traffic", 
        "Berapa banyak yang lewat? Flow gabungan Gerbang & Area (In vs Out).",
        "Area_Traffic_Gate_Flow"
    )

st.markdown("---") 

# --- Footer ---
st.markdown("""
<div style="text-align:center; color:#666;">
    <small>© 2025 Data Analysis Dashboard | Dibentuk oleh N. | v1.0 Stable</small>
</div>
""", unsafe_allow_html=True)
