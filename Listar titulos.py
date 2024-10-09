import os
import json

def list_recipe_titles():
    # Obtener la ruta absoluta del directorio actual
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Recorrer todas las carpetas en el directorio actual
    for folder_name in os.listdir(base_path):
        # Verificar si la carpeta comienza con 'Recipes - '
        if os.path.isdir(os.path.join(base_path, folder_name)) and folder_name.lower().startswith('recipes - '):
            folder_path = os.path.join(base_path, folder_name)
            
            # Obtener la descripción que sigue a 'Recipes - '
            description = folder_name[9:]
            output_file_name = f'titles - {description}.txt'
            
            # Crear o limpiar el archivo de texto
            with open(output_file_name, 'w', encoding='utf-8') as output_file:
                # Recorrer todos los archivos en la carpeta
                for filename in os.listdir(folder_path):
                    if filename.endswith('.json'):
                        file_path = os.path.join(folder_path, filename)
                        
                        # Leer el archivo JSON
                        with open(file_path, 'r', encoding='utf-8') as json_file:
                            try:
                                recipe = json.load(json_file)
                                # Verificar si el JSON tiene el campo 'title'
                                if 'title' in recipe:
                                    output_file.write(recipe['title'] + '\n')
                            except json.JSONDecodeError:
                                print(f"Error leyendo el archivo {filename}. Asegúrate de que sea un JSON válido.")

if __name__ == "__main__":
    list_recipe_titles()
    print("Se han guardado todos los títulos en los archivos correspondientes.")