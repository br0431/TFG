from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By #selector de tipo búsqueda de Selenium
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager #detecta versión de chrome, descarga el webdriver compatible, la guarda en caché y se lo pasa a selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time


service = Service(ChromeDriverManager().install()) #en vez de instalar el driver usamos esto directamente
driver = webdriver.Chrome(service=service)

driver.get("https://www.google.com/?hl=es")
time.sleep(10)

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CLASS_NAME, "gLFyf"))
)

input_element = driver.find_element(By.CLASS_NAME,"gLFyf")
input_element.send_keys("ETSISI UPM" + Keys.ENTER)

#link = driver.find_element(By.PARTIAL_LINK_TEXT, "escritorioUPM")
#link.click()

time.sleep(10)

driver.quit()