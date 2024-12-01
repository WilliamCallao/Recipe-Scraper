
import json

# Nombre del archivo JSON
file_name = "recetas.json"

def update_calories(file_name):
    try:
        # Leer el archivo JSON
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        # Sumar 110 a las calorías en formato string
        for receta_id, receta_data in data.items():
            if "nutricion" in receta_data and "calories" in receta_data["nutricion"]:
                try:
                    # Convertir a entero, sumar 110 y reconvertir a string
                    current_calories = int(receta_data["nutricion"]["calories"])
                    receta_data["nutricion"]["calories"] = str(current_calories + 110)
                except ValueError:
                    print(f"Advertencia: 'calories' no es un número válido en la receta {receta_id}")
        
        # Escribir los cambios de nuevo al archivo
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        
        print(f"Archivo actualizado correctamente: {file_name}")
    except Exception as e:
        print(f"Error al procesar el archivo {file_name}: {e}")

# Ejecutar la función
update_calories(file_name)
