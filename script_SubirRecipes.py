import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

cred = credentials.Certificate("app-programacion-movil-firebase-adminsdk-w5fg5-cf518d27e5.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_image_url(image_data):
    if isinstance(image_data, list):
        for item in image_data:
            if isinstance(item, str) and item.startswith('http'):
                return item
        return ''
    return image_data if isinstance(image_data, str) else ''

def upload_recipes(folder_path, limit=300):
    try:
        count = 0
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.json') and count < limit:
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    recipe = json.load(f)
                    image_url = get_image_url(recipe.get('image_url', ''))
                    doc_ref = db.collection('recipes').document()
                    doc_ref.set({
                        'titulo': recipe.get('title', ''),
                        'keywords': recipe.get('keywords', ''),
                        'tiempo_preparacion': recipe.get('prep_time', ''),
                        'tiempo_coccion': recipe.get('cook_time', ''),
                        'categorias': recipe.get('categories', []),
                        'imagen_url': image_url,
                        'porciones': recipe.get('servings', ''),
                        'ingredientes': [
                            {
                                'nombre': ing.get('name', ''),
                                'cantidad_us': ing.get('us_amount', ''),
                                'cantidad_metrica': ing.get('metric_amount', '')
                            } for ing in recipe.get('ingredients', [])
                        ],
                        'instrucciones': recipe.get('instructions', []),
                        'etiquetas': recipe.get('tags', []),
                        'nutricion': recipe.get('nutrition', {}),
                        'url': recipe.get('url', '')
                    })
                    print(f"Receta '{recipe.get('title', 'Sin título')}' subida exitosamente.")
                    count += 1
        print(f"Subida de recetas completada: {count} recetas subidas.")
    except Exception as e:
        print(f"Error al subir las recetas: {e}")

def main():
    folder_path = "All recipes"
    upload_recipes(folder_path, limit=300)

if __name__ == "__main__":
    main()
