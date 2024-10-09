import os
import csv
import json
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor
import shutil

translator = GoogleTranslator(source='auto', target='es')

def load_title_translations(csv_file):
    title_dict = {}
    try:
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                english_title = row["Inglés"].strip()
                spanish_title = row["Español"].strip()
                title_dict[english_title] = spanish_title
    except Exception as e:
        print(f"Error al cargar el archivo CSV '{csv_file}': {e}")
    return title_dict

def translate_text(text):
    try:
        return translator.translate(text)
    except Exception as e:
        print(f"Error al traducir el texto: {e}")
        return text

def translate_recipe(input_file, output_file, fail_folder, title_dict):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            recipe = json.load(f)
        
        if "title" in recipe:
            english_title = recipe["title"].strip()
            if english_title in title_dict:
                recipe["title"] = title_dict[english_title]
            else:
                raise ValueError(f"Título no encontrado en el archivo CSV: {english_title}")
        
        if "ingredients" in recipe:
            for ingredient in recipe["ingredients"]:
                if "name" in ingredient:
                    ingredient["name"] = translate_text(ingredient["name"])
        
        if "instructions" in recipe:
            recipe["instructions"] = [translate_text(instruction) for instruction in recipe["instructions"]]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(recipe, f, ensure_ascii=False, indent=4)
        print(f"Receta traducida guardada en '{output_file}'")
    except Exception as e:
        print(f"Error al procesar '{input_file}': {e}")
        fail_output_folder = os.path.join(fail_folder, os.path.basename(os.path.dirname(input_file)))
        if not os.path.exists(fail_output_folder):
            os.makedirs(fail_output_folder)
        fail_output_file = os.path.join(fail_output_folder, os.path.basename(input_file))
        shutil.copy(input_file, fail_output_file)
        print(f"Archivo fallido guardado en '{fail_output_file}'")

def translate_folder(input_folder, output_folder, fail_folder, title_dict):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    def process_file(file_name):
        if file_name.endswith('.json'):
            input_file = os.path.join(input_folder, file_name)
            with open(input_file, 'r', encoding='utf-8') as f:
                recipe = json.load(f)
            english_title = recipe["title"].strip()
            if english_title in title_dict:
                output_file_name = title_dict[english_title] + '.json'
                output_file = os.path.join(output_folder, output_file_name)
                translate_recipe(input_file, output_file, fail_folder, title_dict)
            else:
                print(f"Título no encontrado en el archivo CSV: {english_title}")
                fail_output_folder = os.path.join(fail_folder, os.path.basename(os.path.dirname(input_file)))
                if not os.path.exists(fail_output_folder):
                    os.makedirs(fail_output_folder)
                fail_output_file = os.path.join(fail_output_folder, os.path.basename(input_file))
                shutil.copy(input_file, fail_output_file)
                print(f"Archivo fallido guardado en '{fail_output_file}'")
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(process_file, os.listdir(input_folder))

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
    fail_folder = os.path.join(base_dir, "fail")
    if not os.path.exists(fail_folder):
        os.makedirs(fail_folder)
    
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        if os.path.isdir(folder_path) and folder_name.startswith("Recipes - "):
            csv_file = os.path.join(base_dir, f"Titles -  {folder_name.split(' - ')[1].strip()}.csv")
            if os.path.exists(csv_file):
                title_dict = load_title_translations(csv_file)
                if title_dict:
                    print(f"Archivo CSV encontrado y cargado: {csv_file}")
                    translated_folder_name = "Recetas - " + folder_name.split(' - ')[1]
                    output_folder = os.path.join(base_dir, translated_folder_name)
                    translate_folder(folder_path, output_folder, fail_folder, title_dict)
                else:
                    print(f"Archivo CSV encontrado pero vacío o con errores: {csv_file}")
            else:
                print(f"Archivo CSV no encontrado: {csv_file}")

if __name__ == "__main__":
    main()