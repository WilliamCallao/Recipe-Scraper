import os
import json
import shutil

def main():
    # Directorio base donde se encuentra el script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Directorio donde se almacenarán las recetas únicas
    all_recipes_dir = os.path.join(base_dir, "All recipes")
    os.makedirs(all_recipes_dir, exist_ok=True)
    
    # Conjunto para almacenar las URLs de recetas únicas
    unique_urls = set()
    # Contador de recetas únicas copiadas
    unique_recipe_count = 0

    # Buscar directorios que comiencen con "Recipes - "
    for dir_name in os.listdir(base_dir):
        dir_path = os.path.join(base_dir, dir_name)
        if os.path.isdir(dir_path) and dir_name.startswith("Recipes - "):
            # Buscar archivos JSON en el directorio
            for file_name in os.listdir(dir_path):
                if file_name.endswith(".json"):
                    file_path = os.path.join(dir_path, file_name)
                    # Leer el archivo JSON
                    with open(file_path, "r", encoding="utf-8") as file:
                        try:
                            recipe = json.load(file)
                            # Verificar si la receta tiene el campo 'url'
                            url = recipe.get("url")
                            if url and url not in unique_urls:
                                # Copiar el archivo a "All recipes" si es único
                                unique_urls.add(url)
                                shutil.copy(file_path, os.path.join(all_recipes_dir, file_name))
                                unique_recipe_count += 1
                        except json.JSONDecodeError:
                            print(f"Error al leer el archivo JSON: {file_path}")

    # Imprimir el número total de recetas únicas copiadas
    print(f"Total de recetas únicas copiadas: {unique_recipe_count}")

if __name__ == "__main__":
    main()
