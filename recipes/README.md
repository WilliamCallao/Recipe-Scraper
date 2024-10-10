
# Proyecto de Scraping de Recetas

Este proyecto extrae datos de recetas basados en URLs proporcionadas en archivos CSV, y guarda las recetas extraídas como archivos JSON.

## Requisitos previos

Antes de comenzar, asegúrate de haber cumplido con los siguientes requisitos:

- Tener Python 3.x instalado en tu máquina.

## Instalación

1. Clona el repositorio o descarga los archivos del proyecto.
2. Instala las bibliotecas necesarias de Python. Puedes hacerlo ejecutando el siguiente comando:

```bash
pip install -r requirements.txt
```

Esto instalará las siguientes dependencias:
- `requests`
- `beautifulsoup4`
- `colorama`

## Uso

### Ejecutando el Scraper de Recetas

Para ejecutar el scraper y extraer las recetas, sigue estos pasos:

1. Asegúrate de tener el archivo CSV con las URLs listo en la carpeta `Scraper`. Por ejemplo, si deseas usar el archivo `Urls - Dinner.csv`:

2. Puedes cambiar las siguientes variables en el archivo `Recetas.py` según tus preferencias:
   - **`input_csv`**: Define qué archivo CSV se usará. Cámbialo para apuntar al archivo correcto si es necesario.
   - **`output_dir`**: Es el nombre de la carpeta donde se guardarán las recetas extraídas como archivos JSON. Actualiza esta variable si deseas almacenar las recetas en otra carpeta.

   Ejemplo:

   ```python
   input_csv = "Urls - Dinner.csv"  # Cambia esto a cualquier otro archivo CSV que desees utilizar.
   output_dir = "recetas_Dinner"  # Cambia esto para modificar el nombre de la carpeta de salida.
   ```

3. Para iniciar el script, ejecuta:

```bash
python Recetas.py
```

Esto procesará las URLs en el archivo CSV y guardará las recetas extraídas como archivos JSON en la carpeta especificada.

## Archivos CSV

Los siguientes archivos CSV se proporcionan en este proyecto:
- `Urls - Breakfast and Brunch.csv`
- `Urls - Budget-friendly.csv`
- `Urls - Dessert.csv`
- `Urls - Dinner.csv`
- `Urls - Kid Friendly.csv`
- `Urls - Kidney-friendly.csv`
- `Urls - Lower Carb.csv`
- `Urls - Lunch.csv`
- `Urls - Quick-easy.csv`
- `Urls - Snacks.csv`
- `Urls - Vegetarian.csv`
- `Urls - Veggie Rich.csv`

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo LICENSE.md para más detalles.
