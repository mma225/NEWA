# Nusa Rebuilt - Windows 11 prototype

Ini adalah proyek rekonstruksi independen berdasarkan fitur yang dibahas, bukan salinan kode/aset resmi Nusa.

## Jalankan di Windows
1. Install Python 3.11 (centang Add Python to PATH).
2. Buka folder proyek.
3. Jalankan `run_windows.bat`.

Atau lewat terminal:
```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Build EXE via GitHub Actions
Upload seluruh isi folder proyek ke root repository GitHub (termasuk folder `.github`).
Buka Actions > Build NusaRebuilt Windows EXE > Run workflow.
Setelah selesai, unduh artifact `NusaRebuilt-Windows11-EXE`.

## Batasan prototype
Floating Notch, timer Pomodoro, kalender bulanan, dan panel pengaturan adalah implementasi dasar independen.
HUD di sini masih berupa opsi antarmuka; kontrol volume/brightness/Bluetooth tingkat sistem, tampilan kalender mingguan, serta fitur/asset asli Nusa belum direplikasi.
