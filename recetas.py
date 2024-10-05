import os
import glob
import csv
import requests
from bs4 import BeautifulSoup
import json
import re
import time

current_directory = os.getcwd()

csv_files = glob.glob(os.path.join(current_directory, "Urls - Dinner*.csv"))

def split_keywords(keywords_str):
    if not keywords_str:
        return []
    keywords = re.split(r',\s*', keywords_str)
    return [kw.strip() for kw in keywords if kw.strip()]

def ensure_list(value):
    if isinstance(value, list):
        return value
    elif value:
        return [value]
    else:
        return []

def replace_specific_terms(text):
    # replacements = {
    #     r'\bclove\b': 'diente'
    # }
    # for pattern, replacement in replacements.items():
    #     text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def extract_recipe_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')

        recipe_info = {}

        title_element = soup.find('h1')
        recipe_info['title'] = title_element.get_text().strip() if title_element else 'Sin título'

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

        if script_tag:
            try:
                for item in json_data.get('@graph', []):
                    if item.get('@type') == 'Recipe':
                        recipe_info['prep_time'] = item.get('prepTime', 'Desconocido')
            except Exception as e:
                print(f"Error al extraer prep_time en {url}: {e}")
                recipe_info['prep_time'] = 'Desconocido'

        if script_tag:
            try:
                for item in json_data.get('@graph', []):
                    if item.get('@type') == 'Recipe':
                        categories = item.get('recipeCategory', [])
                        recipe_info['categories'] = ensure_list(categories)
            except Exception as e:
                print(f"Error al extraer categories en {url}: {e}")
                recipe_info['categories'] = []

        if script_tag:
            try:
                for item in json_data.get('@graph', []):
                    if item.get('@type') == 'Recipe':
                        image_info = item.get('image', {})
                        recipe_info['image_url'] = image_info.get('url', '') if isinstance(image_info, dict) else image_info
            except Exception as e:
                print(f"Error al extraer image_url en {url}: {e}")
                recipe_info['image_url'] = ''

        servings_element = soup.find('span', class_='js-servings-label')
        recipe_info['servings'] = servings_element.get_text().strip() if servings_element else 'Desconocido'

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

        steps = soup.find('ol', class_='recipe-steps')
        if steps:
            recipe_info['instructions'] = [step.get_text().replace('\n', ' ').strip() for step in steps.find_all('li')]
        else:
            recipe_info['instructions'] = []

        tags = soup.find('div', class_='recipe-tags-section')
        if tags:
            tags_list = [tag.get_text().strip() for tag in tags.find_all('a')]
            recipe_info['tags'] = ensure_list(tags_list)
        else:
            recipe_info['tags'] = []

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

        recipe_info['nutrition'] = nutrition_info

        recipe_info['url'] = url

        return recipe_info

    except Exception as e:
        print(f"Error al extraer datos de la receta en {url}: {e}")
        return None

output_directory = os.path.join(current_directory, 'recetas_json')
os.makedirs(output_directory, exist_ok=True)

for file in csv_files:
    print(f"Procesando archivo: {file}")
    
    with open(file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row.get('Enlace')
            if not url:
                print(f"Fila sin URL encontrada en el archivo {file}. Saltando...")
                continue
            print(f"Extrayendo datos de la URL: {url}")
            
            recipe = extract_recipe_data(url)
            
            if recipe:
                sanitized_title = re.sub(r'[^\w\s-]', '', recipe['title']).strip().replace(' ', '_')
                filename = f"{sanitized_title}.json"
                filepath = os.path.join(output_directory, filename)

                try:
                    with open(filepath, 'w', encoding='utf-8') as jsonfile:
                        json.dump(recipe, jsonfile, ensure_ascii=False, indent=4)
                    print(f"Receta guardada en {filepath}")
                except Exception as e:
                    print(f"Error al guardar el archivo JSON para {url}: {e}")

print(f"Extracción completada. Los datos de las recetas se guardaron en la carpeta '{output_directory}'.")
