import os
import json
from googletrans import Translator
import re

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
        return text

def format_filename(file_name):
    """
    Formatea el nombre del archivo reemplazando guiones bajos por espacios antes de traducirlo.
    """
    # Reemplazar guiones bajos por espacios
    formatted_name = file_name.replace('_', ' ')
    # Traducir el nombre al español
    translated_name = translate_text(formatted_name)
    return translated_name

def translate_recipe(input_file, output_file):
    """
    Traduce el contenido relevante de un archivo JSON de recetas.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        recipe = json.load(f)
    
    # Traducir el título
    if "title" in recipe:
        recipe["title"] = translate_text(recipe["title"])
    
    # Traducir los ingredientes
    if "ingredients" in recipe:
        for ingredient in recipe["ingredients"]:
            if "name" in ingredient:
                ingredient["name"] = translate_text(ingredient["name"])
    
    # Traducir las instrucciones
    if "instructions" in recipe:
        recipe["instructions"] = [translate_text(instruction) for instruction in recipe["instructions"]]
    
    # Guardar el archivo traducido
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recipe, f, ensure_ascii=False, indent=4)

def translate_folder(input_folder, output_folder):
    """
    Traduce todos los archivos JSON en la carpeta de entrada y los guarda en la carpeta de salida.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.json'):
            input_file = os.path.join(input_folder, file_name)
            output_file_name = format_filename(os.path.splitext(file_name)[0]) + '.json'
            output_file = os.path.join(output_folder, output_file_name)
            translate_recipe(input_file, output_file)
            print(f"Receta traducida guardada en '{output_file}'")

def main():
    base_dir = os.getcwd()
    for folder_name in os.listdir(base_dir):
        if folder_name.startswith("Recipes - "):
            input_folder = os.path.join(base_dir, folder_name)
            translated_folder_name = translate_text(folder_name)
            output_folder = os.path.join(base_dir, translated_folder_name)
            translate_folder(input_folder, output_folder)

if __name__ == "__main__":
    main()