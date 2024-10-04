import os
import glob
import csv
from collections import Counter

current_directory = os.getcwd()

csv_files = glob.glob(os.path.join(current_directory, "Urls -*.csv"))

file_counter = Counter()

total_records = 0

for file in csv_files:
    file_name = os.path.basename(file)
    prefix = file_name.split(".csv")[0]
    file_counter[prefix] += 1

    with open(file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        record_count = sum(1 for row in reader)
        total_records += record_count

print("Cantidad de archivos por nombre:")
for prefix, count in file_counter.items():
    print(f"{prefix}: {count}")

total_files = len(csv_files)
print(f"\nTotal de archivos CSV encontrados: {total_files}")

print(f"Total de registros en todos los archivos CSV: {total_records}")
