import os
import glob
import csv
import requests
from bs4 import BeautifulSoup
import json
import re
from googletrans import Translator
import time

# Crear una instancia del traductor de Google
translator = Translator()

# Obtener la ruta actual donde se está ejecutando el script
current_directory = os.getcwd()

# Buscar todos los archivos CSV que comienzan con "Urls - Dinner" en la ruta actual
csv_files = glob.glob(os.path.join(current_directory, "Urls - Dinner*.csv"))

# Función para limpiar y separar keywords
def split_keywords(keywords_str):
    if not keywords_str:
        return []
    # Usar expresión regular para separar por comas y eliminar espacios
    keywords = re.split(r',\s*', keywords_str)
    # Filtrar cualquier keyword vacía
    return [kw.strip() for kw in keywords if kw.strip()]

# Función para traducir una lista de textos
def translate_list(text_list, dest_language='es'):
    translated_list = []
    for text in text_list:
        try:
            if text:  # Verificar que el texto no esté vacío
                translation = translator.translate(text, dest=dest_language)
                if translation and hasattr(translation, 'text'):
                    translated_text = translation.text
                else:
                    translated_text = text  # Mantener el texto original si la traducción falla
                translated_list.append(translated_text)
                # Opcional: esperar un breve tiempo para evitar sobrecargar el traductor
                time.sleep(0.1)
            else:
                translated_list.append(text)
        except Exception as e:
            print(f"Error al traducir el texto '{text}': {e}")
            translated_list.append(text)  # Mantener el texto original en caso de error
    return translated_list

# Función para traducir una cadena de texto
def translate_text(text, dest_language='es'):
    try:
        if text:  # Verificar que el texto no esté vacío
            translation = translator.translate(text, dest=dest_language)
            if translation and hasattr(translation, 'text'):
                translated = translation.text
            else:
                translated = text  # Mantener el texto original si la traducción falla
            # Opcional: esperar un breve tiempo para evitar sobrecargar el traductor
            time.sleep(0.1)
            return translated
        else:
            return text
    except Exception as e:
        print(f"Error al traducir el texto '{text}': {e}")
        return text  # Mantener el texto original en caso de error

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
            try:
                json_data = json.loads(script_tag.string)
                for item in json_data.get('@graph', []):
                    if item.get('@type') == 'Recipe':
                        recipe_info['keywords'] = item.get('keywords', '')
            except json.JSONDecodeError as e:
                print(f"Error al parsear JSON-LD en {url}: {e}")
                recipe_info['keywords'] = ''

        # Extraer tiempo de preparación
        if script_tag:
            try:
                for item in json_data.get('@graph', []):
                    if item.get('@type') == 'Recipe':
                        recipe_info['prep_time'] = item.get('prepTime', 'Desconocido')
            except Exception as e:
                print(f"Error al extraer prep_time en {url}: {e}")
                recipe_info['prep_time'] = 'Desconocido'

        # Extraer categorías de la receta
        if script_tag:
            try:
                for item in json_data.get('@graph', []):
                    if item.get('@type') == 'Recipe':
                        categories = item.get('recipeCategory', [])
                        # Asegurarse de que 'categories' sea una lista
                        if isinstance(categories, str):
                            categories = [categories]
                        recipe_info['categories'] = categories
            except Exception as e:
                print(f"Error al extraer categories en {url}: {e}")
                recipe_info['categories'] = []

        # Extraer imagen de la receta desde el JSON-LD
        if script_tag:
            try:
                for item in json_data.get('@graph', []):
                    if item.get('@type') == 'Recipe':
                        image_info = item.get('image', {})
                        recipe_info['image_url'] = image_info.get('url', '') if isinstance(image_info, dict) else image_info
            except Exception as e:
                print(f"Error al extraer image_url en {url}: {e}")
                recipe_info['image_url'] = ''

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
            recipe_info['instructions'] = [step.get_text().replace('\n', ' ').strip() for step in steps.find_all('li')]
        else:
            recipe_info['instructions'] = []

        # Extraer etiquetas (tags)
        tags = soup.find('div', class_='recipe-tags-section')
        if tags:
            recipe_info['tags'] = [tag.get_text().strip() for tag in tags.find_all('a')]
        else:
            recipe_info['tags'] = []

        # Extraer información nutricional
        nutrition_info = {}
        nutrition_section = soup.find('div', class_='nutrition__content')
        if nutrition_section:
            def get_nutrition_item(prop):
                element = nutrition_section.find('span', itemprop=prop)
                return element.get_text().strip() if element else 'Desconocido'

            nutrition_info['calories'] = get_nutrition_item('calories')
            nutrition_info['total_fat'] = get_nutrition_item('fatContent')
            nutrition_info['saturated_fat'] = get_nutrition_item('saturatedFatContent')
            nutrition_info['trans_fat'] = get_nutrition_item('transFatContent')
            nutrition_info['cholesterol'] = get_nutrition_item('cholesterolContent')
            nutrition_info['sodium'] = get_nutrition_item('sodiumContent')
            nutrition_info['total_carbohydrate'] = get_nutrition_item('carbohydrateContent')
            nutrition_info['fiber'] = get_nutrition_item('fiberContent')
            nutrition_info['sugar'] = get_nutrition_item('sugarContent')
            nutrition_info['added_sugar'] = get_nutrition_item('addedSugarContent')
            nutrition_info['protein'] = get_nutrition_item('proteinContent')

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
            url = row.get('Enlace')  # Asegurarse de que la clave exista
            if not url:
                print(f"Fila sin URL encontrada en el archivo {file}. Saltando...")
                continue
            print(f"Extrayendo datos de la URL: {url}")
            
            # Extraer la información de la receta
            recipe = extract_recipe_data(url)
            
            if recipe:
                # Traducir cada campo específico al español
                try:
                    # Traducir título
                    recipe['title'] = translate_text(recipe['title'], dest_language='es')

                    # Traducir keywords
                    if recipe.get('keywords'):
                        keywords_list = split_keywords(recipe['keywords'])
                        translated_keywords = translate_list(keywords_list, dest_language='es')
                        recipe['keywords'] = ', '.join(translated_keywords)

                    # Traducir categorías
                    if recipe.get('categories'):
                        translated_categories = translate_list(recipe['categories'], dest_language='es')
                        recipe['categories'] = translated_categories

                    # Traducir nombres de los ingredientes
                    for ingredient in recipe['ingredients']:
                        if ingredient.get('name'):
                            ingredient['name'] = translate_text(ingredient['name'], dest_language='es')

                    # Traducir etiquetas (tags)
                    if recipe.get('tags'):
                        translated_tags = translate_list(recipe['tags'], dest_language='es')
                        recipe['tags'] = translated_tags

                    # Traducir instrucciones
                    if recipe.get('instructions'):
                        translated_instructions = translate_list(recipe['instructions'], dest_language='es')
                        recipe['instructions'] = translated_instructions

                    # Traducir porciones
                    if recipe.get('servings'):
                        recipe['servings'] = translate_text(recipe['servings'], dest_language='es')

                except Exception as e:
                    print(f"Error al traducir los campos de la receta en {url}: {e}")

                # Generar un nombre de archivo JSON basado en el título de la receta
                sanitized_title = re.sub(r'[^\w\s-]', '', recipe['title']).strip().replace(' ', '_')
                filename = f"{sanitized_title}.json"
                filepath = os.path.join(output_directory, filename)

                # Guardar la receta en un archivo JSON individual
                try:
                    with open(filepath, 'w', encoding='utf-8') as jsonfile:
                        json.dump(recipe, jsonfile, ensure_ascii=False, indent=4)
                    print(f"Receta guardada en {filepath}")
                except Exception as e:
                    print(f"Error al guardar el archivo JSON para {url}: {e}")

print(f"Extracción completada. Los datos de las recetas se guardaron en la carpeta '{output_directory}'.")
