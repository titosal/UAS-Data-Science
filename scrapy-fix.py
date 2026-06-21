from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, pandas as pd

options = Options()
options.add_argument('--lang=id')
options.add_argument("accept-language=id-ID,id") # Perbaikan typo
driver = webdriver.Chrome(options=options)

# Ganti dengan URL Google Maps yang sebenarnya
driver.get("https://www.google.com/maps/place/Mie+Gacoan+Jakarta+-+Boulevard+Kelapa+Gading/@-6.2069936,106.8275253,17401m/data=!3m1!1e3!4m12!1m2!2m1!1sgacoan!3m8!1s0x2e69f5001da6fcf1:0x71d23459eef6582b!8m2!3d-6.1757353!4d106.8956292!9m1!1b1!15sCgZnYWNvYW4iA4gBAVoIIgZnYWNvYW6SAQtub29kbGVfc2hvcOABAA!16s%2Fg%2F11wxfhyg10?entry=ttu&g_ep=EgoyMDI2MDYxNi4wIKXMDSoASAFQAw%3D%3D")

wait = WebDriverWait(driver, 15)

# 1. Ambil nama tempat
try:
    nama_tempat_el = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "DUwDvf")))
    nama_tempat = nama_tempat_el.text.strip()
except:
    nama_tempat = "Unknown"

# 2. Klik tab "Ulasan" (Reviews)
try:
    tab_ulasan = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//div[contains(text(), 'Ulasan') or contains(text(), 'Reviews')]]")))
    tab_ulasan.click()
    time.sleep(4) # Waktu tunggu agar list ulasan dimuat
except Exception as e:
    print("Gagal menemukan tab Ulasan atau sudah berada di tab ulasan.")

reviews, seen = [], set()

# 3. Mulai ekstraksi
while len(reviews) < 2000:
    ulasan_elements = driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf')
    
    for c in ulasan_elements:
        user_el = c.find_elements(By.CLASS_NAME, 'd4r55')
        review_el = c.find_elements(By.CLASS_NAME, 'wiI7pd')
        rating_el = c.find_elements(By.CLASS_NAME, 'kvMYJc')
        tanggal_el = c.find_elements(By.CLASS_NAME, "rsqaWe")
        
        if not review_el or not review_el[0].text.strip():
            continue
        
        user = user_el[0].text if user_el else 'Unknown'
        review = review_el[0].text.strip()
        rating = rating_el[0].get_attribute('aria-label').split()[0] if rating_el else 'Unknown'
        tanggal = tanggal_el[0].text.strip()
        
        if (user, review) not in seen:
            seen.add((user, review))
            reviews.append({
                'nama_tempat': nama_tempat, 
                'user': user, 
                'review': review, 
                'rating': rating, 
                'tanggal': tanggal
            })
            
        if len(reviews) >= 100:
            break
            
    # 4. Scroll ke bawah menggunakan elemen terakhir
    try:
        # Perbaikan typo: scrollIntoView()
        driver.execute_script("arguments[0].scrollIntoView();", ulasan_elements[-1])
        time.sleep(2.5) # Beri waktu agar AJAX memuat data baru
    except:
        break

pd.DataFrame(reviews).to_csv('ulasan_gacoan_tanggal.csv', index=False)
print(f"[INFO] {len(reviews)} ulasan berhasil disimpan ke 'ulasan_gacoan_tanggal.csv'") 
driver.quit()