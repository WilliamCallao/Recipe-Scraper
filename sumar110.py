import json
import os

# Lista de archivos JSON
json_files = [
    "almuerzo_recetas.json",
    "cena_recetas.json",
    "desayuno_recetas.json",
    "snacks_recetas.json"
]

def update_carbohydrates(file_name):
    try:
        # Leer el archivo JSON
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        # Sumar 110 al atributo "carbohidratos"
        for receta in data:
            if "carbohidratos" in receta:
                receta["carbohidratos"] += 110
        
        # Sobrescribir el archivo original con los datos actualizados
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        
        print(f"Archivo actualizado correctamente: {file_name}")
    except Exception as e:
        print(f"Error al procesar el archivo {file_name}: {e}")

# Actualizar cada archivo JSON
for json_file in json_files:
    if os.path.exists(json_file):
        update_carbohydrates(json_file)
    else:
        print(f"El archivo no existe: {json_file}")
