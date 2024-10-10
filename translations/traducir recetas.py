import os
import csv
import json
from deep_translator import GoogleTranslator
import shutil
import re
import difflib

translator = GoogleTranslator(source='auto', target='es')

def load_title_translations(csv_files):
    title_dict = {}
    for csv_file in csv_files:
        try:
            with open(csv_file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    english_title = normalize_title(row["Inglés"].strip())
                    spanish_title = row["Español"].strip()
                    title_dict[english_title] = spanish_title
        except Exception as e:
            print(f"Error al cargar el archivo CSV '{csv_file}': {e}")
    return title_dict

def normalize_title(title):
    # Normalize title to ensure proper matching by removing non-letter characters, quotes, and extra whitespace
    return re.sub(r'[^a-zA-Z]', '', title).lower().strip()

def translate_text(text):
    try:
        return translator.translate(text)
    except Exception as e:
        print(f"Error al traducir el texto '{text}': {e}")
        return text

def find_closest_match(title, title_dict):
    # Find the closest match using difflib
    normalized_titles = list(title_dict.keys())
    closest_matches = difflib.get_close_matches(title, normalized_titles, n=1, cutoff=0.6)
    if closest_matches:
        return closest_matches[0]
    return None

def translate_recipe(input_file, output_file, fail_folder, translated_folder, title_dict):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            recipe = json.load(f)
        
        if "title" in recipe:
            english_title = normalize_title(recipe["title"])
            if english_title in title_dict:
                recipe["title"] = title_dict[english_title]
            else:
                # Try to find the closest match
                closest_match = find_closest_match(english_title, title_dict)
                if closest_match:
                    recipe["title"] = title_dict[closest_match]
                else:
                    raise ValueError(f"Título no encontrado en los archivos CSV: '{recipe['title']}' (normalizado: '{english_title}')")
        
        # Translate ingredients and instructions separately to avoid mixing
        translated_ingredients = []
        if "ingredients" in recipe:
            for ingredient in recipe["ingredients"]:
                if "name" in ingredient:
                    translated_ingredient = ingredient.copy()
                    translated_ingredient["name"] = translate_text(ingredient["name"])
                    translated_ingredients.append(translated_ingredient)
                else:
                    print(f"Ingrediente sin nombre en la receta '{recipe.get('title', 'sin título')}'")
        recipe["ingredients"] = translated_ingredients
        
        translated_instructions = []
        if "instructions" in recipe:
            translated_instructions = [translate_text(instruction) for instruction in recipe["instructions"]]
        else:
            print(f"Instrucciones no encontradas en la receta '{recipe.get('title', 'sin título')}'")
        recipe["instructions"] = translated_instructions
        
        # Remove or replace problematic characters from the output file name
        output_file_name = os.path.basename(output_file)
        output_file_name = re.sub(r'[\/:*?"<>|]', '', output_file_name)
        output_file = os.path.join(os.path.dirname(output_file), output_file_name)
        output_file = output_file if output_file.endswith('.json') else f"{output_file}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(recipe, f, ensure_ascii=False, indent=4)
        
        shutil.move(input_file, os.path.join(translated_folder, os.path.basename(input_file)))
        print(f"Receta traducida guardada en '{output_file}' y original movida a '{translated_folder}'")
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el archivo JSON '{input_file}': {e}")
        fail_output_file = os.path.join(fail_folder, os.path.basename(input_file))
        if not os.path.exists(fail_folder):
            os.makedirs(fail_folder)
        shutil.copy(input_file, fail_output_file)
        print(f"Archivo fallido guardado en '{fail_output_file}' debido a un error de decodificación JSON")
    except ValueError as e:
        print(f"Error al procesar el título en '{input_file}': {e}")
        fail_output_file = os.path.join(fail_folder, os.path.basename(input_file))
        if not os.path.exists(fail_folder):
            os.makedirs(fail_folder)
        shutil.copy(input_file, fail_output_file)
        print(f"Archivo fallido guardado en '{fail_output_file}' debido a un error de título")
    except Exception as e:
        print(f"Error inesperado al procesar '{input_file}': {e}")
        fail_output_file = os.path.join(fail_folder, os.path.basename(input_file))
        if not os.path.exists(fail_folder):
            os.makedirs(fail_folder)
        shutil.copy(input_file, fail_output_file)
        print(f"Archivo fallido guardado en '{fail_output_file}' debido a un error inesperado")

def translate_folder(input_folder, output_folder, fail_folder, translated_folder, title_dict):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(translated_folder):
        os.makedirs(translated_folder)
    
    def process_file(file_name):
        if file_name.endswith('.json'):
            input_file = os.path.join(input_folder, file_name)
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    recipe = json.load(f)
                    english_title = normalize_title(recipe.get("title", ""))
                output_file_name = title_dict.get(english_title, file_name)
                output_file = os.path.join(output_folder, output_file_name if output_file_name.endswith('.json') else f"{output_file_name}.json")
                translate_recipe(input_file, output_file, fail_folder, translated_folder, title_dict)
            except json.JSONDecodeError as e:
                print(f"Error al decodificar el archivo JSON '{input_file}': {e}")
                fail_output_file = os.path.join(fail_folder, os.path.basename(input_file))
                if not os.path.exists(fail_folder):
                    os.makedirs(fail_folder)
                shutil.copy(input_file, fail_output_file)
                print(f"Archivo fallido guardado en '{fail_output_file}' debido a un error de decodificación JSON")
    
    # Using single thread to avoid mixing ingredients and instructions
    for file_name in os.listdir(input_folder):
        process_file(file_name)

def main():
    base_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
    input_folder = os.path.join(base_dir, "All recipes")
    output_folder = os.path.join(base_dir, "All recipes ES")
    fail_folder = os.path.join(base_dir, "fail")
    translated_folder = os.path.join(base_dir, "Recetas ya traducidas")

    csv_files = [os.path.join(base_dir, file) for file in os.listdir(base_dir) if file.startswith("Titles - ") and file.endswith(".csv")]
    if csv_files:
        title_dict = load_title_translations(csv_files)
        if title_dict:
            print(f"Archivos CSV encontrados y cargados: {csv_files}")
            translate_folder(input_folder, output_folder, fail_folder, translated_folder, title_dict)
        else:
            print(f"Archivos CSV encontrados pero vacíos o con errores: {csv_files}")
    else:
        print(f"No se encontraron archivos CSV.")

if __name__ == "__main__":
    main()