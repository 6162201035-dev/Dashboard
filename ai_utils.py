import streamlit as st
import google.generativeai as genai

def analyze_with_gemini(data_summary, user_question):
    """
    Mengirim ringkasan data dan pertanyaan user ke Gemini AI.
    """
    # 1. Ambil API Key
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Error: API Key tidak ditemukan di .streamlit/secrets.toml"

    # 2. Konfigurasi Gemini
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest') # Model cepat & murah
        
        # 3. Buat Prompt (Instruksi)
        prompt = f"""
        Kamu adalah Data Analyst Senior untuk sebuah retail store. 
        Tugasmu adalah menganalisis profil pelanggan berdasarkan data berikut:
        
        DATA CONTEXT:
        {data_summary}
        
        USER QUESTION:
        {user_question}
        
        Berikan jawaban dalam Bahasa Indonesia yang profesional, ringkas, dan actionable (bisa ditindaklanjuti).
        Gunakan bullet points jika perlu.
        """

        # 4. Kirim ke AI
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"⚠️ Terjadi kesalahan pada AI: {str(e)}"
