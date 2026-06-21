import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import pandas as pd
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class GMapScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Maps Review Scraper & Cleaner")
        self.root.geometry("650x780")
        self.root.resizable(False, False)
        
        # Konfigurasi style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.create_widgets()

    def create_widgets(self):
        # --- Frame Input Scraping ---
        input_frame = ttk.LabelFrame(self.root, text="Konfigurasi Scraping", padding=(15, 15))
        input_frame.pack(fill="x", padx=15, pady=10)

        # 1. URL Input
        ttk.Label(input_frame, text="URL Google Maps:").grid(row=0, column=0, sticky="w", pady=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(input_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=0, column=1, sticky="w", pady=5, padx=5)

        # 2. Max Data Input
        ttk.Label(input_frame, text="Jumlah Maksimal Review:").grid(row=1, column=0, sticky="w", pady=5)
        self.max_var = tk.IntVar(value=50)
        self.max_entry = ttk.Entry(input_frame, textvariable=self.max_var, width=15)
        self.max_entry.grid(row=1, column=1, sticky="w", pady=5, padx=5)

        # 3. Checkboxes untuk Data
        ttk.Label(input_frame, text="Data yang diambil:").grid(row=2, column=0, sticky="nw", pady=5)
        
        checkbox_frame = ttk.Frame(input_frame)
        checkbox_frame.grid(row=2, column=1, sticky="w", pady=5, padx=5)
        
        self.var_nama = tk.BooleanVar(value=True)
        self.var_rating = tk.BooleanVar(value=True)
        self.var_waktu = tk.BooleanVar(value=True)
        self.var_teks = tk.BooleanVar(value=True)

        ttk.Checkbutton(checkbox_frame, text="Nama", variable=self.var_nama).pack(side="left", padx=5)
        ttk.Checkbutton(checkbox_frame, text="Rating", variable=self.var_rating).pack(side="left", padx=5)
        ttk.Checkbutton(checkbox_frame, text="Waktu", variable=self.var_waktu).pack(side="left", padx=5)
        ttk.Checkbutton(checkbox_frame, text="Teks Review", variable=self.var_teks).pack(side="left", padx=5)

        # 4. Tampilkan Browser Checkbox
        self.var_show_browser = tk.BooleanVar(value=False)
        ttk.Checkbutton(input_frame, text="Tampilkan Jendela Browser Chrome (Matikan Headless Mode)", 
                        variable=self.var_show_browser).grid(row=3, column=0, columnspan=2, sticky="w", pady=10)

        # --- Tombol Mulai Scraping ---
        self.btn_start = ttk.Button(self.root, text="🚀 Mulai Scraping", command=self.start_scraping_thread)
        self.btn_start.pack(pady=5)

        # --- Frame Data Cleaner ---
        cleaner_frame = ttk.LabelFrame(self.root, text="Alat Pembersih Data (Data Cleaner)", padding=(15, 10))
        cleaner_frame.pack(fill="x", padx=15, pady=5)
        
        ttk.Label(cleaner_frame, text="Bersihkan file CSV hasil scraping dari duplikat, format teks berantakan, dan rating.").pack(side="top", anchor="w", pady=(0, 5))
        
        self.btn_clean = ttk.Button(cleaner_frame, text="🧹 Pilih File CSV & Bersihkan", command=self.clean_data_ui)
        self.btn_clean.pack(pady=5)

        # --- Frame Log Console ---
        log_frame = ttk.LabelFrame(self.root, text="Log Proses", padding=(10, 10))
        log_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.log_console = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=12, state='disabled', bg="#f0f0f0")
        self.log_console.pack(fill="both", expand=True)

    def log(self, message):
        """Menulis pesan ke console log GUI dengan aman (Thread-safe)"""
        self.log_console.configure(state='normal')
        self.log_console.insert(tk.END, message + "\n")
        self.log_console.configure(state='disabled')
        self.log_console.yview(tk.END) # Auto-scroll ke bawah
        self.root.update_idletasks()

    def start_scraping_thread(self):
        """Memvalidasi input dan menjalankan scraping di thread terpisah agar GUI tidak freeze"""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showwarning("Peringatan", "URL Google Maps tidak boleh kosong!")
            return
            
        try:
            max_reviews = self.max_var.get()
            if max_reviews <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Peringatan", "Jumlah review harus berupa angka bulat positif!")
            return

        fields = []
        if self.var_nama.get(): fields.append('nama')
        if self.var_rating.get(): fields.append('rating')
        if self.var_waktu.get(): fields.append('waktu')
        if self.var_teks.get(): fields.append('teks')

        if not fields:
            messagebox.showwarning("Peringatan", "Pilih minimal satu data yang ingin diambil!")
            return

        show_browser = self.var_show_browser.get()

        # Nonaktifkan tombol saat proses berjalan
        self.btn_start.config(state="disabled")
        self.btn_clean.config(state="disabled")
        
        # Bersihkan log sebelumnya
        self.log_console.configure(state='normal')
        self.log_console.delete(1.0, tk.END)
        self.log_console.configure(state='disabled')

        # Jalankan scraping di background thread
        thread = threading.Thread(target=self.run_scraper, args=(url, max_reviews, fields, show_browser))
        thread.daemon = True
        thread.start()

    def setup_driver(self, show_browser):
        """Menyiapkan browser Chrome"""
        self.log("[SISTEM] Menyiapkan WebDriver Chrome...")
        chrome_options = Options()
        if not show_browser:
            chrome_options.add_argument("--headless") # Jalankan di background
        
        chrome_options.add_argument("--lang=id-ID")
        chrome_options.add_argument("--disable-notifications")
        # Menambahkan argumen agar lebih stabil di headless mode
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def parse_waktu_to_hari(self, waktu_str):
        """Fungsi untuk mengonversi teks waktu Google Maps menjadi estimasi hari"""
        if not isinstance(waktu_str, str):
            return None
            
        waktu_str = waktu_str.lower().strip()
        
        # Jika satuannya kurang dari sehari (baru saja, menit, jam)
        if "baru saja" in waktu_str or "menit" in waktu_str or "jam" in waktu_str:
            return 0
            
        # Penanganan kata awalan "se-" (satu)
        if "sehari" in waktu_str: return 1
        if "seminggu" in waktu_str: return 7
        if "sebulan" in waktu_str: return 30
        if "setahun" in waktu_str: return 365
        
        # Ekstrak angka dan satuan menggunakan Regex
        match = re.search(r'(\d+)\s*(hari|minggu|bulan|tahun)', waktu_str)
        if match:
            angka = int(match.group(1))
            satuan = match.group(2)
            
            if satuan == 'hari':
                return angka
            elif satuan == 'minggu':
                return angka * 7
            elif satuan == 'bulan':
                return angka * 30
            elif satuan == 'tahun':
                return angka * 365
                
        return None # Jika format tidak dikenali

    def run_scraper(self, url, max_reviews, fields, show_browser):
        """Fungsi utama yang berjalan di background thread"""
        driver = None
        try:
            driver = self.setup_driver(show_browser)
            self.log(f"[INFO] Membuka URL: {url[:50]}...")
            driver.get(url)
            
            # Beri sedikit waktu untuk memuat halaman dasar
            time.sleep(3)
            
            # --- AMBIL NAMA LOKASI ---
            self.log("[INFO] Mengambil nama lokasi...")
            location_name = "Lokasi_Tidak_Diketahui"
            try:
                # Biasanya nama tempat pada Google Maps berada di dalam tag <h1>
                h1_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
                )
                location_name = h1_elem.text.strip()
                self.log(f"[INFO] Nama Lokasi Ditemukan: {location_name}")
            except Exception:
                self.log("[WARNING] Gagal mendapatkan nama lokasi otomatis.")
            
            # --- AUTO-KLIK TAB ULASAN ---
            self.log("[INFO] Mengecek dan memastikan tab 'Ulasan' terbuka...")
            try:
                # Cari semua elemen yang berfungsi sebagai tab
                tabs = driver.find_elements(By.CSS_SELECTOR, "button[role='tab']")
                for tab in tabs:
                    # Jika teks tab mengandung kata ulasan atau reviews, klik tab tersebut
                    if "ulasan" in tab.text.lower() or "reviews" in tab.text.lower():
                        driver.execute_script("arguments[0].click();", tab)
                        self.log("[INFO] Tab 'Ulasan' diklik secara otomatis.")
                        time.sleep(3) # Tunggu ulasan dimuat setelah tab diklik
                        break
            except Exception as e:
                self.log("[WARNING] Tidak dapat mengklik tab otomatis, mencoba melanjutkan...")
            
            # 1. Scroll dan Kumpulkan Elemen
            self.log(f"[INFO] Memulai proses scrolling untuk {max_reviews} ulasan...")
            
            # Tunggu elemen pertama muncul (Menggunakan data-review-id agar kebal perubahan class Google)
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-review-id]")))
            except TimeoutException:
                self.log("[ERROR] Halaman tidak memuat ulasan. Pastikan URL langsung mengarah ke halaman tempat.")
                return

            last_review_count = 0
            scroll_attempts = 0
            
            while True:
                # Menggunakan data-review-id sebagai identifier yang stabil
                reviews = driver.find_elements(By.CSS_SELECTOR, "div[data-review-id]")
                current_review_count = len(reviews)
                
                # Update log (dikurangi spam agar log tidak penuh)
                if current_review_count > last_review_count:
                    self.log(f"   -> Terkumpul: {current_review_count}/{max_reviews} ulasan")
                
                if current_review_count >= max_reviews:
                    self.log("[INFO] Target jumlah ulasan tercapai.")
                    break
                    
                if current_review_count == last_review_count:
                    scroll_attempts += 1
                    if scroll_attempts > 5:
                        self.log("[INFO] Mencapai akhir dari ulasan (atau loading stuck).")
                        break
                else:
                    scroll_attempts = 0
                    
                last_review_count = current_review_count
                
                # Scroll menggunakan elemen ulasan terakhir ke dalam tampilan (Lebih stabil)
                if reviews:
                    driver.execute_script('arguments[0].scrollIntoView(true);', reviews[-1])
                
                time.sleep(2.5) # Jeda loading

            reviews = driver.find_elements(By.CSS_SELECTOR, "div[data-review-id]")
            self.log(f"[INFO] Selesai scrolling. Total didapat: {len(reviews)}")

            # 2. Klik "Lainnya" untuk teks panjang
            self.log("[INFO] Membuka teks ulasan yang panjang (Klik 'Lainnya')...")
            try:
                more_buttons = driver.find_elements(By.CSS_SELECTOR, "button.w8nwRe.kyuRq")
                for button in more_buttons:
                    driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
            except Exception:
                pass 

            # 3. Ekstrak Data
            self.log("[INFO] Memulai ekstraksi data...")
            scraped_data = []
            
            for i, review in enumerate(reviews):
                if i >= max_reviews: break
                data_dict = {}
                
                # Tambahkan Nama Lokasi sebagai kolom pertama
                data_dict['Nama Lokasi'] = location_name
                
                if 'nama' in fields:
                    try: data_dict['Nama'] = review.find_element(By.CSS_SELECTOR, "div.d4r55").text
                    except: data_dict['Nama'] = None

                if 'rating' in fields:
                    try:
                        rating_aria = review.find_element(By.CSS_SELECTOR, "span.kvMYJc").get_attribute("aria-label")
                        data_dict['Rating'] = rating_aria.split(' ')[0] 
                    except: data_dict['Rating'] = None

                if 'waktu' in fields:
                    try: 
                        time_rel = review.find_element(By.CSS_SELECTOR, "span.rsqaWe").text
                        data_dict['Waktu'] = time_rel
                        data_dict['Umur Komentar (Hari)'] = self.parse_waktu_to_hari(time_rel)
                    except: 
                        data_dict['Waktu'] = None
                        data_dict['Umur Komentar (Hari)'] = None

                if 'teks' in fields:
                    try: data_dict['Teks Review'] = review.find_element(By.CSS_SELECTOR, "span.wiI7pd").text
                    except: data_dict['Teks Review'] = ""

                scraped_data.append(data_dict)

            # 4. Simpan ke File CSV
            if scraped_data:
                df = pd.DataFrame(scraped_data)
                
                # Buat nama file yang aman dari nama lokasi
                safe_loc_name = re.sub(r'[^a-zA-Z0-9]', '_', location_name)
                # Batasi panjang nama file jika nama lokasi terlalu panjang
                safe_loc_name = safe_loc_name[:30].strip('_')
                if not safe_loc_name:
                    safe_loc_name = "lokasi"
                    
                filename = f"hasil_scraping_{safe_loc_name}_{int(time.time())}.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                
                # Dapatkan path lengkap tempat file disimpan
                full_path = os.path.abspath(filename)
                
                self.log(f"\n[SUKSES] Berhasil mengekstrak {len(scraped_data)} ulasan!")
                self.log(f"[SUKSES] File disimpan di:\n{full_path}")
                
                # Tampilkan pesan pop-up sukses
                messagebox.showinfo("Berhasil", f"Scraping selesai!\nData disimpan di:\n{filename}")
            else:
                self.log("[WARNING] Tidak ada data yang berhasil diekstrak.")
                messagebox.showwarning("Peringatan", "Tidak ada data yang berhasil ditarik.")

        except Exception as e:
            self.log(f"\n[ERROR] Terjadi kesalahan:\n{str(e)}")
            messagebox.showerror("Error", f"Terjadi kesalahan teknis:\n{str(e)}")
        finally:
            if driver:
                self.log("[SISTEM] Menutup browser...")
                driver.quit()
            
            # Aktifkan kembali tombol
            self.btn_start.config(state="normal")
            self.btn_clean.config(state="normal")
            self.log("[SISTEM] Proses selesai. Siap untuk tugas baru.")

    # ==========================================
    # FUNGSI PEMBERSIHAN DATA (DATA CLEANING)
    # ==========================================
    def clean_data_ui(self):
        """Membuka dialog file dan menjalankan pembersihan data di thread terpisah"""
        filepath = filedialog.askopenfilename(
            title="Pilih File CSV Hasil Scraping",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not filepath:
            return # Batal memilih file
            
        # Bersihkan log
        self.log_console.configure(state='normal')
        self.log_console.delete(1.0, tk.END)
        self.log_console.configure(state='disabled')
        
        # Nonaktifkan tombol sementara
        self.btn_start.config(state="disabled")
        self.btn_clean.config(state="disabled")

        # Jalankan di thread terpisah
        thread = threading.Thread(target=self.clean_data_process, args=(filepath,))
        thread.daemon = True
        thread.start()

    def clean_data_process(self, filepath):
        """Proses pembersihan data menggunakan Pandas"""
        self.log(f"[SISTEM] Memulai pembersihan data untuk file:\n{filepath}\n")
        try:
            # Membaca data
            df = pd.read_csv(filepath)
            initial_rows = len(df)
            
            if initial_rows == 0:
                self.log("[WARNING] File CSV kosong.")
                return

            self.log("[INFO] 1. Menghapus data duplikat...")
            df.drop_duplicates(inplace=True)

            self.log("[INFO] 2. Membersihkan kolom 'Nama'...")
            if 'Nama' in df.columns:
                df['Nama'] = df['Nama'].fillna("Anonim")
                df['Nama'] = df['Nama'].str.strip()

            self.log("[INFO] 3. Membersihkan kolom 'Rating'...")
            if 'Rating' in df.columns:
                # Mengambil angka saja menggunakan regex (contoh: "5 bintang" -> 5)
                df['Rating'] = df['Rating'].astype(str).str.extract(r'(\d+)').astype(float)

            self.log("[INFO] 4. Membersihkan kolom 'Teks Review'...")
            if 'Teks Review' in df.columns:
                # Mengisi data kosong
                df['Teks Review'] = df['Teks Review'].fillna("Tidak ada ulasan")
                # Menghapus newlines (\n atau \r) dan menggantinya dengan spasi
                df['Teks Review'] = df['Teks Review'].astype(str).str.replace(r'\n|\r', ' ', regex=True)
                # Menghapus spasi ganda
                df['Teks Review'] = df['Teks Review'].str.replace(r'\s+', ' ', regex=True)
                # Menghapus spasi di awal dan akhir teks
                df['Teks Review'] = df['Teks Review'].str.strip()
                
            self.log("[INFO] 5. Menghitung estimasi hari dari kolom 'Waktu'...")
            if 'Waktu' in df.columns:
                df['Umur Komentar (Hari)'] = df['Waktu'].apply(self.parse_waktu_to_hari)

            final_rows = len(df)
            removed_rows = initial_rows - final_rows

            # Simpan file baru
            dir_name = os.path.dirname(filepath)
            base_name = os.path.basename(filepath)
            # Menambahkan awalan 'cleaned_' pada nama file asli
            new_filename = os.path.join(dir_name, f"cleaned_{base_name}")

            # Rapikan urutan kolom jika kolom Umur Komentar ditambahkan
            if 'Waktu' in df.columns and 'Umur Komentar (Hari)' in df.columns:
                cols = df.columns.tolist()
                # Pindahkan Umur Komentar tepat setelah kolom Waktu
                cols.insert(cols.index('Waktu') + 1, cols.pop(cols.index('Umur Komentar (Hari)')))
                df = df[cols]

            df.to_csv(new_filename, index=False, encoding='utf-8-sig')

            self.log("\n[SUKSES] Pembersihan data selesai!")
            self.log(f"   -> Total baris awal: {initial_rows}")
            self.log(f"   -> Baris duplikat dihapus: {removed_rows}")
            self.log(f"   -> Sisa baris bersih: {final_rows}")
            self.log(f"[SUKSES] File bersih disimpan di:\n{new_filename}")

            messagebox.showinfo(
                "Pembersihan Selesai", 
                f"Data berhasil dibersihkan!\n\nDuplikat dihapus: {removed_rows}\nTotal baris sekarang: {final_rows}\n\nDisimpan sebagai:\ncleaned_{base_name}"
            )

        except Exception as e:
            self.log(f"\n[ERROR] Gagal membersihkan data: {str(e)}")
            messagebox.showerror("Error", f"Gagal membersihkan data:\n{str(e)}")
        finally:
            self.btn_start.config(state="normal")
            self.btn_clean.config(state="normal")
            self.log("\n[SISTEM] Proses selesai. Siap untuk tugas baru.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GMapScraperApp(root)
    root.mainloop()