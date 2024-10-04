import os
import glob
from collections import Counter

# Obtener la ruta actual donde se está ejecutando el script
current_directory = os.getcwd()

# Buscar todos los archivos CSV que comienzan con "Urls- " en la ruta actual
csv_files = glob.glob(os.path.join(current_directory, "Urls-*.csv"))

# Contador para llevar la cuenta de cuántos archivos hay con el mismo prefijo
file_counter = Counter()

# Contar los archivos
for file in csv_files:
    # Extraer el prefijo sin la extensión para contar cuántos hay de cada uno
    file_name = os.path.basename(file)
    prefix = file_name.split(".csv")[0]
    file_counter[prefix] += 1

# Imprimir el conteo de cada tipo de archivo
print("Cantidad de archivos por nombre:")
for prefix, count in file_counter.items():
    print(f"{prefix}: {count}")

# Imprimir el total de archivos CSV encontrados
total_files = len(csv_files)
print(f"\nTotal de archivos CSV encontrados: {total_files}")
