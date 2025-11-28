@echo off
cd /d "C:\Users\IT-ASSET028\Desktop\retail_dashboard"

:: Aktifkan virtual environment
call .venv\Scripts\activate

:: Jalankan dashboard Streamlit
streamlit run Home.py

pause