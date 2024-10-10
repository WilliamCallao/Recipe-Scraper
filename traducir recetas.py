import os
import csv
import json
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor
import shutil

translator = GoogleTranslator(source='auto', target='es')

def load_title_translations(csv_files):
    title_dict = {}
    for csv_file in csv_files:
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

def translate_recipe(input_file, output_file, fail_folder, translated_folder, title_dict):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            recipe = json.load(f)
        
        if "title" in recipe:
            english_title = recipe["title"].strip()
            if english_title in title_dict:
                recipe["title"] = title_dict[english_title]
            else:
                raise ValueError(f"Título no encontrado en los archivos CSV: {english_title}")
        
        if "ingredients" in recipe:
            for ingredient in recipe["ingredients"]:
                if "name" in ingredient:
                    ingredient["name"] = translate_text(ingredient["name"])
        
        if "instructions" in recipe:
            recipe["instructions"] = [translate_text(instruction) for instruction in recipe["instructions"]]
        
        output_file = output_file if output_file.endswith('.json') else f"{output_file}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(recipe, f, ensure_ascii=False, indent=4)
        
        shutil.move(input_file, os.path.join(translated_folder, os.path.basename(input_file)))
        print(f"Receta traducida guardada en '{output_file}' y original movida a '{translated_folder}'")
    except Exception as e:
        print(f"Error al procesar '{input_file}': {e}")
        fail_output_file = os.path.join(fail_folder, os.path.basename(input_file))
        if not os.path.exists(fail_folder):
            os.makedirs(fail_folder)
        shutil.copy(input_file, fail_output_file)
        print(f"Archivo fallido guardado en '{fail_output_file}'")

def translate_folder(input_folder, output_folder, fail_folder, translated_folder, title_dict):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(translated_folder):
        os.makedirs(translated_folder)
    
    def process_file(file_name):
        if file_name.endswith('.json'):
            input_file = os.path.join(input_folder, file_name)
            output_file_name = title_dict.get(json.load(open(input_file, 'r', encoding='utf-8'))["title"].strip(), file_name)
            output_file = os.path.join(output_folder, output_file_name)
            translate_recipe(input_file, output_file, fail_folder, translated_folder, title_dict)
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(process_file, os.listdir(input_folder))

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