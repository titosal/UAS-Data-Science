from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time, pandas as pd

options = Options()
options.add_argument('--lang=id')
options.add_argument("accep-language-id-ID,id")
driver = webdriver.Chrome(options=options)

driver.get("https://www.google.com/maps/place/Mie+Gacoan+Jakarta+-+Boulevard+Kelapa+Gading/@-6.2069936,106.8275253,17401m/data=!3m1!1e3!4m12!1m2!2m1!1sgacoan!3m8!1s0x2e69f5001da6fcf1:0x71d23459eef6582b!8m2!3d-6.1757353!4d106.8956292!9m1!1b1!15sCgZnYWNvYW4iA4gBAVoIIgZnYWNvYW6SAQtub29kbGVfc2hvcOABAA!16s%2Fg%2F11wxfhyg10?entry=ttu&g_ep=EgoyMDI2MDYxNi4wIKXMDSoASAFQAw%3D%3D")
time.sleep(750)

try:
    nama_tempat = driver.find_element(By.CLASS_NAME, "DUwDvf").text.strip()
except:
    nama_tempat = "Unknown"
    
try:
    driver.find_element(
        By.XPATH,
        "//span[contains(text(),'Lainnya') or contains(text(), 'More')]/ancestor::Button"
    ).click()
    time.sleep(3)
except:
    pass

reviews, seen = [], set()

while len(reviews) <100:
    for c in driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf'):
        user_el = c.find_elements(By.CLASS_NAME,'d4r55')
        review_el = c.find_elements(By.CLASS_NAME,'wiI7pd')
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
            reviews.append({'nama_tempat': nama_tempat, 'user': user, 'review': review, 'rating':rating, 'tanggal':tanggal})
            
    try:
        driver.execute_script("arguments[0].scrollIntoViews();", driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf')[-1])
        
    except:
        break
    time.sleep(2)

pd.DataFrame(reviews).to_csv('ulasan_gacoan_tanggal_jak_boul.csv', index=False)
print(f"[INFO] {len(reviews)} ulasan berhasil disimpan ke 'ulasan_gacoan_Tanggal_jak_boul.csv'") 
driver.quit()   