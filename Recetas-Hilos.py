import os
import csv
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import threading
from urllib.parse import urlparse
import hashlib
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor

init(autoreset=True)

input_csv = "Urls - Budget-friendly.csv"
output_dir = "Urls - Budget-friendly"
failed_csv = "failed.csv"

lock = threading.Lock()
existing_filenames = set()
failed_rows = []

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
    replacements = {
        r'\bclove\b': 'diente',
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def sanitize_filename(name):
    sanitized = re.sub(r'[\\/*?:"<>|]', "", name)
    sanitized = sanitized.replace(' ', '_')
    return sanitized[:100]

def generate_unique_filename(base_name):
    with lock:
        if base_name not in existing_filenames:
            existing_filenames.add(base_name)
            return base_name
        else:
            counter = 1
            while True:
                new_name = f"{base_name}_{counter}"
                if new_name not in existing_filenames:
                    existing_filenames.add(new_name)
                    return new_name
                counter += 1

def extract_recipe_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        recipe_info = {}
        title_element = soup.find('h1')
        recipe_info['title'] = title_element.get_text().strip() if title_element else 'Sin_título'
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            try:
                json_data = json.loads(script_tag.string)
                if '@graph' in json_data:
                    graph = json_data['@graph']
                else:
                    graph = [json_data]
                for item in graph:
                    if item.get('@type') == 'Recipe':
                        recipe_info['keywords'] = item.get('keywords', '')
                        recipe_info['prep_time'] = item.get('prepTime', 'Desconocido')
                        recipe_info['cook_time'] = item.get('cookTime', 'Desconocido')
                        recipe_info['categories'] = ensure_list(item.get('recipeCategory', []))
                        image_info = item.get('image', {})
                        recipe_info['image_url'] = image_info.get('url', '') if isinstance(image_info, dict) else image_info
            except json.JSONDecodeError as e:
                print(Fore.YELLOW + f"Advertencia al parsear JSON-LD en {url}: {e}")
                recipe_info['keywords'] = ''
                recipe_info['prep_time'] = 'Desconocido'
                recipe_info['cook_time'] = 'Desconocido'
                recipe_info['categories'] = []
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
                    'us_amount': replace_specific_terms(us_amount.get_text().strip()),
                    'metric_amount': replace_specific_terms(metric_amount.get_text().strip()) if metric_amount else 'No_disponible'
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
    except requests.RequestException as e:
        print(Fore.RED + f"Error de conexión al acceder a {url}: {e}")
        return None
    except Exception as e:
        print(Fore.RED + f"Error al extraer la receta de {url}: {e}")
        return None

def process_url(row):
    url = row.get('Enlace')
    if not url:
        print(Fore.YELLOW + f"Advertencia: Fila sin URL en '{input_csv}'. Saltando...")
        return
    print(Fore.CYAN + f"Procesando URL: {url}")
    recipe = extract_recipe_data(url)
    if recipe:
        base_name = sanitize_filename(recipe['title'])
        if not base_name:
            base_name = hashlib.md5(url.encode('utf-8')).hexdigest()
        unique_name = generate_unique_filename(base_name)
        filename = f"{unique_name}.json"
        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(recipe, jsonfile, ensure_ascii=False, indent=4)
            print(Fore.GREEN + f"Guardado: '{filepath}'.")
        except Exception as e:
            print(Fore.RED + f"Error al guardar '{filepath}': {e}")
    else:
        with lock:
            failed_rows.append(row)
        print(Fore.RED + f"Falló la extracción de la receta de {url}.")

def main():
    os.makedirs(output_dir, exist_ok=True)
    try:
        with open(input_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            with ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(process_url, rows)
        if failed_rows:
            with open(failed_csv, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = rows[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(failed_rows)
            print(Fore.YELLOW + f"Proceso completado con errores. Recetas fallidas guardadas en '{failed_csv}'.")
        else:
            print(Fore.GREEN + f"Proceso completado. Recetas guardadas en '{output_dir}'.")
    except FileNotFoundError:
        print(Fore.RED + f"Error: El archivo CSV '{input_csv}' no se encontró.")
    except Exception as e:
        print(Fore.RED + f"Error al procesar el archivo CSV: {e}")

if __name__ == "__main__":
    main()