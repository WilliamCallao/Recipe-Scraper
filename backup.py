import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# Ruta del archivo JSON con las credenciales
cred = credentials.Certificate("app-programacion-movil-firebase-adminsdk-w5fg5-68d00a1c0d.json")
firebase_admin.initialize_app(cred)

# Inicializar cliente de Firestore
db = firestore.client()

def backup_collection(collection_name):
    try:
        # Referencia a la colección original
        original_collection = db.collection(collection_name)
        
        # Sufijo para la colección de respaldo
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_collection_name = f"{collection_name}_backup_{timestamp}"
        backup_collection = db.collection(backup_collection_name)
        
        # Obtener todos los documentos de la colección original usando una consulta
        docs = original_collection.get()
        
        # Copiar documentos a la colección de respaldo
        for doc in docs:
            backup_collection.document(doc.id).set(doc.to_dict())
        
        print(f"Copia de seguridad creada con éxito: {backup_collection_name}")
    except Exception as e:
        print(f"Error al crear la copia de seguridad: {e}")


# Nombre de la colección a respaldar
backup_collection("recetas")
