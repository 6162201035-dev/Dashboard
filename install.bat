@echo off
echo ====================================================
echo == Menginstal Python Virtual Environment (venv)... ==
echo ====================================================
python -m venv .venv

echo.
echo ====================================================
echo == Mengaktifkan venv & Menginstal library...     ==
echo == Ini mungkin butuh beberapa menit. Harap tunggu. ==
echo ====================================================
call .\.venv\Scripts\activate
pip install -r requirements.txt

echo.
echo ====================================================
echo ==         INSTALASI SELESAI!                   ==
echo ====================================================
echo.
echo Anda sekarang bisa menutup jendela ini dan
echo menjalankan file 'run.bat'.
echo.
pause