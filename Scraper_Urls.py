from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from bs4 import BeautifulSoup
import csv

chrome_options = Options()
chrome_options.add_argument("--start-maximized") 
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://diabetesfoodhub.org/recipes/kid-friendly")

with open('recetas_unicas.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Titulo', 'Enlace', 'Imagen']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    def load_more_recipes(driver, max_retries=5):
        retries = 0
        while retries < max_retries:
            try:
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Load more') and not(contains(@class, 'recipe-card__link'))]"))
                )
                if load_more_button.is_displayed() and load_more_button.is_enabled():
                    ActionChains(driver).move_to_element(load_more_button).click(load_more_button).perform()
                    time.sleep(2)
                    return True
            except TimeoutException:
                print("Botón 'Cargar más' no encontrado, reintentando...")
                retries += 1
                time.sleep(2) 
            except Exception as e:
                print(f"Error al intentar cargar más recetas: {e}")
                retries += 1
                time.sleep(2)
        return False

    unique_recipes = set()

    max_total_retries = 10
    total_retries = 0
    while total_retries < max_total_retries:
        success = load_more_recipes(driver)
        if not success:
            total_retries += 1
            if total_retries >= max_total_retries:
                print("Se alcanzó el número máximo de reintentos, finalizando.")
                break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        recipes = soup.find_all('div', class_='recipe-card')
        for recipe in recipes:
            title_element = recipe.find('h3', class_='recipe-card__headline')
            link_element = recipe.find('a', href=True)
            image_element = recipe.find('img', src=True)

            title = title_element.text.strip() if title_element else 'Sin título'
            link = link_element['href'] if link_element and '/recipes/' in link_element['href'] else None  # Verificar que sea un enlace a receta
            image = image_element['src'] if image_element else 'Sin imagen'


            if link and link not in unique_recipes:
                unique_recipes.add(link)

                writer.writerow({'Titulo': title, 'Enlace': link, 'Imagen': image})

driver.quit()

print(f"Se extrajeron {len(unique_recipes)} recetas únicas y se guardaron en 'recetas_unicas.csv'.")
