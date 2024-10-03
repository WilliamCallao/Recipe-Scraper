from bs4 import BeautifulSoup
import json

# Leer el archivo HTML local
with open('html1.html', 'r', encoding='utf-8') as file:
    content = file.read()

# Parsear el contenido HTML
soup = BeautifulSoup(content, 'html.parser')

# Extraer las recetas iniciales
recipes = soup.find_all('div', class_='recipe-card')
for recipe in recipes:
    title = recipe.find('h3', class_='recipe-card__headline').text.strip()
    link = recipe.find('a')['href']
    image = recipe.find('img')['src']
    print(f'Título: {title}, Enlace: {link}, Imagen: {image}')

# Aquí puedes agregar más lógica según lo que necesitas analizar o procesar del archivo local.
