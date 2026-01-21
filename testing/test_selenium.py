from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By #selector de tipo búsqueda de Selenium
from webdriver_manager.chrome import ChromeDriverManager #detecta versión de chrome, descarga el webdriver compatible, la guarda en caché y se lo pasa a selenium
import time

service = Service(ChromeDriverManager().install()) #en vez de instalar el driver usamos esto directamente
driver = webdriver.Chrome(service=service)

driver.get("https://www.metatft.com/units/BaronNashor")
time.sleep(5)

unit_overlay = driver.find_element(By.CLASS_NAME, "UnitNameOverlay") #aquí usamos By para buscar por nombre de clase al ver que había nombres de clases
print(unit_overlay.text)

driver.quit()
