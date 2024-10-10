import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# Inicializar Firebase con serviceAccountKey.json
cred = credentials.Certificate("app-programacion-movil-firebase-adminsdk-w5fg5-cf518d27e5.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def create_collection():
    try:
        # Crear un documento con la estructura de una receta en la colección 'recetas' para definir la estructura
        doc_ref = db.collection('recetas').document('placeholder')
        doc_ref.set({
            'titulo': 'placeholder',
            'keywords': 'placeholder',
            'tiempo_preparacion': 'PT0M',
            'tiempo_coccion': 'PT0M',
            'categorias': ['placeholder'],
            'imagen_url': 'https://example.com/placeholder.jpg',
            'porciones': '0 servings',
            'ingredientes': [
                {
                    'nombre': 'placeholder',
                    'cantidad_us': '0',
                    'cantidad_metrica': '0'
                }
            ],
            'instrucciones': ['placeholder'],
            'etiquetas': ['placeholder'],
            'nutricion': {
                'calorias': '0',
                'total_fat': '0g',
                'saturated_fat': '0g',
                'trans_fat': '0g',
                'cholesterol': '0mg',
                'sodium': '0mg',
                'total_carbohydrate': '0g',
                'fiber': '0g',
                'sugar': '0g',
                'added_sugar': '0g',
                'protein': '0g'
            },
            'url': 'https://example.com/placeholder'
        })
        print("Colección 'recetas' creada exitosamente con un documento de marcador de posición.")
    except Exception as e:
        print(f"Error al crear la colección 'recetas': {e}")

def main():
    create_collection()

if __name__ == "__main__":
    main()