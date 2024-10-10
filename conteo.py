import os
import json
from collections import Counter

# Define la carpeta que contiene los archivos JSON
folder_path = "recipes"

# Inicializa conjuntos y contadores
categorias_unicas = set()
ingredientes_unicos = set()
tags_contador = Counter()
ingredientes_contador = Counter()
categorias_contador = Counter()

def cargar_recetas(folder_path):
    recetas = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            with open(os.path.join(folder_path, file_name), "r", encoding="utf-8") as file:
                receta = json.load(file)
                recetas.append(receta)
    return recetas

recetas = cargar_recetas(folder_path)

# Procesar las recetas para extraer la informacion requerida
for receta in recetas:
    # Obtener categorias
    for categoria in receta.get("categories", []):
        categorias_unicas.add(categoria)
        categorias_contador[categoria] += 1
    
    # Obtener ingredientes
    for ingrediente in receta.get("ingredients", []):
        ingredientes_unicos.add(ingrediente["name"])
        ingredientes_contador[ingrediente["name"]] += 1
    
    # Obtener tags y contarlos
    for tag in receta.get("tags", []):
        tags_contador[tag] += 1

# Guardar todas las categorias unicas en un archivo txt
with open("categorias_unicas.txt", "w", encoding="utf-8") as file:
    file.write("Categorías únicas:\n")
    for categoria in categorias_unicas:
        file.write(f"{categoria}\n")

# Guardar todos los ingredientes unicos en un archivo txt
with open("ingredientes_unicos.txt", "w", encoding="utf-8") as file:
    file.write("Ingredientes únicos:\n")
    for ingrediente in ingredientes_unicos:
        file.write(f"{ingrediente}\n")

# Guardar el conteo de tags en un archivo txt
with open("conteo_tags.txt", "w", encoding="utf-8") as file:
    file.write("Conteo de Tags:\n")
    for tag, count in tags_contador.items():
        file.write(f"{tag}: {count}\n")

# Guardar el conteo de categorias en un archivo txt
with open("conteo_categorias.txt", "w", encoding="utf-8") as file:
    file.write("Conteo de Categorías:\n")
    for categoria, count in categorias_contador.items():
        file.write(f"{categoria}: {count}\n")

# Guardar el conteo de ingredientes en un archivo txt
with open("conteo_ingredientes.txt", "w", encoding="utf-8") as file:
    file.write("Conteo de Ingredientes:\n")
    for ingrediente, count in ingredientes_contador.items():
        file.write(f"{ingrediente}: {count}\n")