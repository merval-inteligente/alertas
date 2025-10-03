from motor.motor_asyncio import AsyncIOMotorClient
from config import settings


class MongoDB:
    client: AsyncIOMotorClient = None
    
    
mongodb = MongoDB()


async def get_database():
    """Retorna la instancia de la base de datos"""
    return mongodb.client[settings.database_name]


async def connect_to_mongo():
    """Conecta a MongoDB"""
    print("Conectando a MongoDB...")
    mongodb.client = AsyncIOMotorClient(settings.mongodb_uri)
    # Verificar la conexión
    try:
        await mongodb.client.admin.command('ping')
        print("✓ Conectado exitosamente a MongoDB")
    except Exception as e:
        print(f"✗ Error al conectar a MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Cierra la conexión a MongoDB"""
    print("Cerrando conexión a MongoDB...")
    if mongodb.client:
        mongodb.client.close()
        print("✓ Conexión cerrada")
