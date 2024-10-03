from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import csv

# Configuración de opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Maximizar ventana para mejor visibilidad
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Inicializar el ChromeDriver (asegúrate de tener la versión correcta instalada)
service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)

# Abrir la página inicial
driver.get("https://diabetesfoodhub.org/recipes/kidney-friendly")

# Crear una función para cargar más recetas
def load_more_recipes(driver):
    try:
        # Esperar hasta que el botón 'Cargar más' sea visible y clicable
        load_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Load more')]"))
        )
        ActionChains(driver).move_to_element(load_more_button).click(load_more_button).perform()
        time.sleep(2)  # Dar tiempo para cargar más recetas
        return True
    except Exception as e:
        print(f"No se pudo cargar más recetas: {e}")
        return False

# Hacer clic en el botón "Cargar más" repetidamente hasta que no haya más que cargar
while True:
    success = load_more_recipes(driver)
    if not success:
        break  # Terminar si no se puede cargar más

# Extraer el contenido de la página después de cargar todas las recetas
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Cerrar el navegador después de la extracción
driver.quit()

# Extraer las recetas y evitar duplicados
recipes = soup.find_all('div', class_='recipe-card')
unique_recipes = set()

for recipe in recipes:
    title_element = recipe.find('h3', class_='recipe-card__headline')
    link_element = recipe.find('a', href=True)
    image_element = recipe.find('img', src=True)

    # Verificar si se encontraron los elementos
    title = title_element.text.strip() if title_element else 'Sin título'
    link = link_element['href'] if link_element else 'Sin enlace'
    image = image_element['src'] if image_element else 'Sin imagen'

    # Usar el enlace como identificador único para evitar duplicados
    if link not in unique_recipes:
        unique_recipes.add((title, link, image))

# Serializar las recetas únicas en un archivo CSV
with open('recetas_unicas.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Titulo', 'Enlace', 'Imagen']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for title, link, image in unique_recipes:
        writer.writerow({'Titulo': title, 'Enlace': link, 'Imagen': image})

# Mostrar el número total de recetas únicas extraídas
print(f"Se extrajeron {len(unique_recipes)} recetas únicas y se guardaron en 'recetas_unicas.csv'.")
