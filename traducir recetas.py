import os
import json
from googletrans import Translator
import re
from concurrent.futures import ThreadPoolExecutor

# Crear una instancia del traductor
translator = Translator()

def translate_text(text, dest_language="es"):
    """
    Traduce un texto al idioma deseado.
    """
    try:
        translated = translator.translate(text, dest=dest_language)
        return translated.text
    except Exception as e:
        print(f"Error al traducir el texto: {e}")
        return None

def format_filename(file_name):
    """
    Formatea el nombre del archivo reemplazando guiones bajos por espacios antes de traducirlo.
    """
    # Reemplazar guiones bajos por espacios
    formatted_name = file_name.replace('_', ' ')
    # Traducir el nombre al español
    translated_name = translate_text(formatted_name)
    return translated_name if translated_name else file_name

def translate_recipe(input_file, output_file, fail_folder):
    """
    Traduce el contenido relevante de un archivo JSON de recetas.
    Si falla, guarda el archivo en la carpeta de fallos correspondiente.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            recipe = json.load(f)
        
        # Traducir el título
        if "title" in recipe:
            translated_title = translate_text(recipe["title"])
            if translated_title:
                recipe["title"] = translated_title
            else:
                raise Exception("Fallo al traducir el título.")
        
        # Traducir los ingredientes
        if "ingredients" in recipe:
            for ingredient in recipe["ingredients"]:
                if "name" in ingredient:
                    translated_name = translate_text(ingredient["name"])
                    if translated_name:
                        ingredient["name"] = translated_name
                    else:
                        raise Exception("Fallo al traducir un ingrediente.")
        
        # Traducir las instrucciones
        if "instructions" in recipe:
            translated_instructions = [translate_text(instruction) for instruction in recipe["instructions"]]
            if all(translated_instructions):
                recipe["instructions"] = translated_instructions
            else:
                raise Exception("Fallo al traducir las instrucciones.")
        
        # Guardar el archivo traducido
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

def translate_folder(input_folder, output_folder, fail_folder):
    """
    Traduce todos los archivos JSON en la carpeta de entrada y los guarda en la carpeta de salida.
    Si falla, guarda el archivo en la carpeta de fallos correspondiente.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    def process_file(file_name):
        if file_name.endswith('.json'):
            input_file = os.path.join(input_folder, file_name)
            output_file_name = format_filename(os.path.splitext(file_name)[0]) + '.json'
            output_file = os.path.join(output_folder, output_file_name)
            translate_recipe(input_file, output_file, fail_folder)
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(process_file, os.listdir(input_folder))

def main():
    base_dir = os.getcwd()
    fail_folder = os.path.join(base_dir, "fail")
    if not os.path.exists(fail_folder):
        os.makedirs(fail_folder)
    
    for folder_name in os.listdir(base_dir):
        if folder_name.startswith("Recipes - "):
            input_folder = os.path.join(base_dir, folder_name)
            translated_folder_name = translate_text(folder_name)
            output_folder = os.path.join(base_dir, translated_folder_name)
            translate_folder(input_folder, output_folder, fail_folder)

if __name__ == "__main__":
    main()