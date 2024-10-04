import os
import glob
import csv
import requests
from bs4 import BeautifulSoup
import json
import re

# Obtener la ruta actual donde se está ejecutando el script
current_directory = os.getcwd()

# Buscar todos los archivos CSV que comienzan con "Urls- " en la ruta actual
csv_files = glob.glob(os.path.join(current_directory, "Urls - Dinner*.csv"))

# Función para extraer información de recetas de una URL
def extract_recipe_data(url):
    try:
        # Realizar la petición HTTP para obtener el contenido de la página
        response = requests.get(url)
        response.raise_for_status()
        
        # Parsear el HTML usando BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Inicializar un diccionario para almacenar los datos extraídos
        recipe_info = {}

        # Extraer nombre de la receta
        title_element = soup.find('h1')
        recipe_info['title'] = title_element.get_text().strip() if title_element else 'Sin título'

        # Extraer keywords desde el bloque JSON-LD o meta tag
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            json_data = json.loads(script_tag.string)
            for item in json_data.get('@graph', []):
                if item.get('@type') == 'Recipe':
                    recipe_info['keywords'] = item.get('keywords', '')

        # Extraer tiempo de preparación
        if script_tag:
            for item in json_data.get('@graph', []):
                if item.get('@type') == 'Recipe':
                    recipe_info['prep_time'] = item.get('prepTime', 'Desconocido')

        # Extraer categorías de la receta
        if script_tag:
            for item in json_data.get('@graph', []):
                if item.get('@type') == 'Recipe':
                    recipe_info['categories'] = item.get('recipeCategory', [])

        # Extraer imagen de la receta desde el JSON-LD
        if script_tag:
            for item in json_data.get('@graph', []):
                if item.get('@type') == 'Recipe':
                    image_info = item.get('image', {})
                    recipe_info['image_url'] = image_info.get('url', '') if isinstance(image_info, dict) else image_info

        # Extraer porciones (cantidad de raciones)
        servings_element = soup.find('span', class_='js-servings-label')
        recipe_info['servings'] = servings_element.get_text().strip() if servings_element else 'Desconocido'

        # Extraer ingredientes detallados
        ingredients_section = soup.find_all('div', class_='ingredient-wrapper')
        ingredients_list = []
        for ingredient in ingredients_section:
            label = ingredient.find('div', class_='ingredient-label')
            us_amount = ingredient.find('div', class_='ingredient-us')
            metric_amount = ingredient.find('div', class_='ingredient-metric hidden')

            if label and us_amount:
                ingredient_info = {
                    'name': label.get_text().strip(),
                    'us_amount': us_amount.get_text().strip(),
                    'metric_amount': metric_amount.get_text().strip() if metric_amount else 'No disponible'
                }
                ingredients_list.append(ingredient_info)

        recipe_info['ingredients'] = ingredients_list

        # Extraer pasos de la receta (instrucciones)
        steps = soup.find('ol', class_='recipe-steps')
        if steps:
            recipe_info['instructions'] = [step.get_text().strip() for step in steps.find_all('li')]
        else:
            recipe_info['instructions'] = []

        # Extraer etiquetas (tags)
        tags = soup.find('div', class_='recipe-tags-section')
        if tags:
            recipe_info['tags'] = ', '.join([tag.get_text().strip() for tag in tags.find_all('a')])
        else:
            recipe_info['tags'] = ''

        # Extraer información nutricional
        nutrition_info = {}
        nutrition_section = soup.find('div', class_='nutrition__content')
        if nutrition_section:
            calories = nutrition_section.find('span', itemprop='calories')
            nutrition_info['calories'] = calories.get_text().strip() if calories else 'Desconocido'

            fat = nutrition_section.find('span', itemprop='fatContent')
            nutrition_info['total_fat'] = fat.get_text().strip() if fat else 'Desconocido'

            saturated_fat = nutrition_section.find('span', itemprop='saturatedFatContent')
            nutrition_info['saturated_fat'] = saturated_fat.get_text().strip() if saturated_fat else 'Desconocido'

            trans_fat = nutrition_section.find('span', itemprop='transFatContent')
            nutrition_info['trans_fat'] = trans_fat.get_text().strip() if trans_fat else 'Desconocido'

            cholesterol = nutrition_section.find('span', itemprop='cholesterolContent')
            nutrition_info['cholesterol'] = cholesterol.get_text().strip() if cholesterol else 'Desconocido'

            sodium = nutrition_section.find('span', itemprop='sodiumContent')
            nutrition_info['sodium'] = sodium.get_text().strip() if sodium else 'Desconocido'

            carbs = nutrition_section.find('span', itemprop='carbohydrateContent')
            nutrition_info['total_carbohydrate'] = carbs.get_text().strip() if carbs else 'Desconocido'

            fiber = nutrition_section.find('span', itemprop='fiberContent')
            nutrition_info['fiber'] = fiber.get_text().strip() if fiber else 'Desconocido'

            sugar = nutrition_section.find('span', itemprop='sugarContent')
            nutrition_info['sugar'] = sugar.get_text().strip() if sugar else 'Desconocido'

            added_sugar = nutrition_section.find('span', itemprop='addedSugarContent')
            nutrition_info['added_sugar'] = added_sugar.get_text().strip() if added_sugar else 'Desconocido'

            protein = nutrition_section.find('span', itemprop='proteinContent')
            nutrition_info['protein'] = protein.get_text().strip() if protein else 'Desconocido'

        # Añadir la información nutricional al diccionario principal
        recipe_info['nutrition'] = nutrition_info

        # Añadir la URL a los datos de la receta
        recipe_info['url'] = url

        return recipe_info

    except Exception as e:
        print(f"Error al extraer datos de la receta en {url}: {e}")
        return None

# Crear una carpeta para guardar los archivos JSON de cada receta
output_directory = os.path.join(current_directory, 'recetas_json')
os.makedirs(output_directory, exist_ok=True)

# Iterar sobre cada archivo CSV y extraer las URLs
for file in csv_files:
    print(f"Procesando archivo: {file}")
    
    with open(file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row['Enlace']
            print(f"Extrayendo datos de la URL: {url}")
            
            # Extraer la información de la receta
            recipe = extract_recipe_data(url)
            
            if recipe:
                # Generar un nombre de archivo JSON basado en el título de la receta
                sanitized_title = re.sub(r'[^\w\s-]', '', recipe['title']).strip().replace(' ', '_')
                filename = f"{sanitized_title}.json"
                filepath = os.path.join(output_directory, filename)

                # Guardar la receta en un archivo JSON individual
                with open(filepath, 'w', encoding='utf-8') as jsonfile:
                    json.dump(recipe, jsonfile, ensure_ascii=False, indent=4)

print(f"Extracción completada. Los datos de las recetas se guardaron en la carpeta '{output_directory}'.")
