📘 Notebook Panduan: Menjalankan Google Maps Scraper GUI di VS Code

Panduan ini akan membantu Anda menjalankan kode Python GUI (Tkinter) untuk Scraping Google Maps di PC (Windows) maupun Mac menggunakan Visual Studio Code.

🛠️ Tahap 1: Persiapan Perangkat Lunak (Prerequisites)

Sebelum mulai, pastikan Anda telah menginstal dua perangkat lunak utama ini di komputer Anda:

Python

Windows/Mac: Unduh dan instal dari python.org.

PENTING (Windows): Saat proses instalasi, pastikan Anda mencentang opsi "Add Python to PATH" di bagian bawah jendela installer.

Visual Studio Code (VS Code)

Unduh dan instal dari code.visualstudio.com.

Browser Google Chrome

Karena aplikasi ini menggunakan Selenium dengan Chrome, pastikan Google Chrome sudah terinstal di komputer Anda.

📂 Tahap 2: Membuat Project di VS Code

Buat sebuah folder baru di komputer Anda (misalnya di Desktop, beri nama Gmaps_Scraper).

Buka VS Code.

Pilih menu File > Open Folder... (atau Open... di Mac) dan pilih folder Gmaps_Scraper yang baru saja Anda buat.

Di panel sebelah kiri (Explorer), klik ikon New File (kertas dengan tanda +).

Beri nama file tersebut: gmaps_scraper_gui.py.

Salin (copy) seluruh kode Python GUI yang ada di Canvas sebelumnya, lalu tempel (paste) ke dalam file gmaps_scraper_gui.py ini.

Simpan file dengan menekan Ctrl + S (Windows) atau Cmd + S (Mac).

🔌 Tahap 3: Menginstal Ekstensi & Library Python

Agar VS Code mengenali kode Python dan bisa menjalankan library yang dibutuhkan, ikuti langkah berikut:

A. Instal Ekstensi Python di VS Code

Klik ikon Extensions di menu sebelah kiri VS Code (atau tekan Ctrl+Shift+X / Cmd+Shift+X).

Cari "Python" (biasanya buatan Microsoft).

Klik Install.

B. Buka Terminal VS Code

Klik menu Terminal > New Terminal di bagian atas VS Code.

Sebuah panel terminal akan terbuka di bagian bawah layar.

C. Instal Library (Dependencies)

Ketik perintah berikut di Terminal yang baru terbuka, lalu tekan Enter:

Untuk Windows:

pip install selenium webdriver-manager pandas


Untuk Mac:
(Catatan: Mac biasanya menggunakan pip3)

pip3 install selenium webdriver-manager pandas


(Tunggu hingga proses unduhan dan instalasi selesai 100%)

🚀 Tahap 4: Menjalankan Aplikasi

Ada dua cara untuk menjalankan aplikasi GUI ini:

Cara 1: Menggunakan Tombol "Play" (Sangat Mudah)

Buka file gmaps_scraper_gui.py di editor.

Lihat ke pojok kanan atas layar VS Code, Anda akan melihat ikon tombol Play (segitiga / "Run Python File").

Klik tombol tersebut. Aplikasi GUI akan langsung terbuka.

Cara 2: Menggunakan Terminal

Di panel Terminal bagian bawah, ketik perintah berikut dan tekan Enter:

Untuk Windows:

python gmaps_scraper_gui.py


Untuk Mac:

python3 gmaps_scraper_gui.py


💡 Troubleshooting (Solusi Masalah Umum)

Jika Anda menemui error saat mencoba menjalankannya, berikut adalah solusi untuk masalah yang paling sering terjadi:

1. Error: ModuleNotFoundError: No module named 'tkinter' (Khusus Mac)

Penyebab: Mac terkadang tidak menyertakan modul Tkinter (GUI) secara bawaan.

Solusi: Buka terminal Mac Anda dan instal Tkinter menggunakan Homebrew dengan perintah: brew install python-tk (Jika belum punya Homebrew, instal dulu via brew.sh).

2. Error: pip is not recognized as an internal or external command (Khusus Windows)

Penyebab: Python belum masuk ke dalam PATH komputer Anda.

Solusi: Instal ulang Python dan pastikan kotak "Add Python to PATH" dicentang pada langkah pertama instalasi.

3. Error terkait Session not created: This version of ChromeDriver only supports Chrome version...

Penyebab: Versi browser Google Chrome Anda tidak cocok.

Solusi: Seharusnya webdriver-manager mengurus ini secara otomatis. Namun jika tetap error, coba perbarui Google Chrome Anda ke versi terbaru (Buka Chrome > Settings > About Chrome).

Selamat mencoba! Jika GUI sudah muncul, Anda tinggal memasukkan URL Google Maps dan klik "Mulai Scraping". File CSV akan otomatis tersimpan di folder Gmaps_Scraper yang Anda buat di Tahap 2.