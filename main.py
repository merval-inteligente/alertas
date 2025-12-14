from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List

from database import connect_to_mongo, close_mongo_connection
from models import News, Tweet, Alert, AlertResponse
from services import NewsService, TweetService, AlertService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="Alertas de Noticias API",
    description="API para generar alertas basadas en noticias de MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "API de Alertas de Noticias y Tweets",
        "version": "2.0.0",
        "endpoints": {
            "GET /news": "Obtener todas las noticias",
            "GET /news/recent": "Obtener noticias recientes",
            "GET /tweets": "Obtener todos los tweets",
            "GET /tweets/recent": "Obtener tweets recientes",
            "GET /alerts": "Obtener todas las alertas",
            "POST /alerts/generate": "Generar alertas desde noticias y tweets (COMBINADO)",
            "POST /alerts/generate/news": "Generar alertas solo desde noticias",
            "POST /alerts/generate/tweets": "Generar alertas solo desde tweets",
            "POST /alerts/clean-duplicates": "Limpiar alertas duplicadas",
            "DELETE /alerts": "Eliminar todas las alertas",
            "GET /health": "Estado de salud de la API"
        }
    }


@app.get("/health")
async def health_check():
    """Verifica el estado de la API y la conexión a MongoDB"""
    try:
        from database import mongodb
        await mongodb.client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "message": "API funcionando correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error de conexión: {str(e)}")


@app.get("/news", response_model=List[News])
async def get_news():
    """Obtiene todas las noticias de la base de datos"""
    try:
        news = await NewsService.get_all_news()
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener noticias: {str(e)}")


@app.get("/news/recent", response_model=List[News])
async def get_recent_news(limit: int = 50):
    """Obtiene las noticias más recientes"""
    try:
        news = await NewsService.get_recent_news(limit=limit)
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener noticias: {str(e)}")


@app.get("/tweets", response_model=List[Tweet])
async def get_tweets():
    """Obtiene todos los tweets de la base de datos"""
    try:
        tweets = await TweetService.get_all_tweets()
        return tweets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tweets: {str(e)}")


@app.get("/tweets/recent", response_model=List[Tweet])
async def get_recent_tweets(limit: int = 100):
    """Obtiene los tweets más recientes"""
    try:
        tweets = await TweetService.get_recent_tweets(limit=limit)
        return tweets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tweets: {str(e)}")


@app.get("/alerts", response_model=List[Alert])
async def get_alerts():
    """Obtiene todas las alertas generadas"""
    try:
        alerts = await AlertService.get_all_alerts()
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alertas: {str(e)}")


@app.post("/alerts/generate", response_model=AlertResponse)
async def generate_alerts():
    """
    Procesa NOTICIAS Y TWEETS y genera alertas automáticamente (COMBINADO).
    Las alertas se guardan en la colección 'alerts' de MongoDB.
    """
    try:
        result = await AlertService.process_all_and_create_alerts()
        
        return AlertResponse(
            success=result["success"],
            alerts_created=result["alerts_created"],
            news_processed=result["news_processed"],
            tweets_processed=result["tweets_processed"],
            alerts=result["alerts"],
            message=f"Se procesaron {result['news_processed']} noticias y {result['tweets_processed']} tweets. Se crearon {result['alerts_created']} alertas"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar alertas: {str(e)}")


@app.post("/alerts/generate/news", response_model=AlertResponse)
async def generate_alerts_from_news():
    """
    Procesa solo las NOTICIAS y genera alertas.
    Las alertas se guardan en la colección 'alerts' de MongoDB.
    """
    try:
        result = await AlertService.process_news_and_create_alerts()
        
        return AlertResponse(
            success=result["success"],
            alerts_created=result["alerts_created"],
            news_processed=result["news_processed"],
            tweets_processed=result["tweets_processed"],
            alerts=result["alerts"],
            message=f"Se procesaron {result['news_processed']} noticias y se crearon {result['alerts_created']} alertas"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar alertas desde noticias: {str(e)}")


@app.post("/alerts/generate/tweets", response_model=AlertResponse)
async def generate_alerts_from_tweets():
    """
    Procesa solo los TWEETS y genera alertas.
    Las alertas se guardan en la colección 'alerts' de MongoDB.
    """
    try:
        result = await AlertService.process_tweets_and_create_alerts()
        
        return AlertResponse(
            success=result["success"],
            alerts_created=result["alerts_created"],
            news_processed=result["news_processed"],
            tweets_processed=result["tweets_processed"],
            alerts=result["alerts"],
            message=f"Se procesaron {result['tweets_processed']} tweets y se crearon {result['alerts_created']} alertas"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar alertas desde tweets: {str(e)}")


@app.delete("/alerts")
async def delete_all_alerts():
    """Elimina todas las alertas (útil para testing)"""
    try:
        from database import get_database
        db = await get_database()
        result = await db["alerts"].delete_many({})
        return {
            "success": True,
            "deleted_count": result.deleted_count,
            "message": f"Se eliminaron {result.deleted_count} alertas"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar alertas: {str(e)}")


@app.post("/alerts/clean-duplicates")
async def clean_duplicate_alerts():
    """Limpia alertas duplicadas manteniendo solo la más reciente de cada grupo"""
    try:
        from database import get_database
        from datetime import datetime
        
        db = await get_database()
        alerts = db['alerts']
        
        # Buscar alertas duplicadas por título
        pipeline = [
            {
                '$group': {
                    '_id': '$title',
                    'count': {'$sum': 1},
                    'docs': {'$push': '$$ROOT'}
                }
            },
            {
                '$match': {'count': {'$gt': 1}}
            }
        ]
        
        duplicates = await alerts.aggregate(pipeline).to_list(None)
        
        total_deleted = 0
        groups_processed = 0
        
        for dup_group in duplicates:
            docs = dup_group['docs']
            
            # Ordenar por lastTriggered (más reciente primero)
            docs_sorted = sorted(
                docs,
                key=lambda x: x.get('lastTriggered', x.get('createdAt', datetime.min)),
                reverse=True
            )
            
            # Mantener el primero (más reciente), eliminar el resto
            keep_doc = docs_sorted[0]
            to_delete = docs_sorted[1:]
            
            # Actualizar el documento que mantenemos con la suma de triggers
            total_triggers = sum(d.get('triggerCount', 1) for d in docs_sorted)
            
            await alerts.update_one(
                {'_id': keep_doc['_id']},
                {
                    '$set': {
                        'triggerCount': total_triggers,
                        'lastTriggered': datetime.utcnow()
                    }
                }
            )
            
            # Eliminar los duplicados
            for doc in to_delete:
                await alerts.delete_one({'_id': doc['_id']})
                total_deleted += 1
            
            groups_processed += 1
        
        # Estadísticas finales
        total_after = await alerts.count_documents({})
        
        return {
            "success": True,
            "groups_processed": groups_processed,
            "duplicates_deleted": total_deleted,
            "total_alerts_remaining": total_after,
            "message": f"Se procesaron {groups_processed} grupos de duplicados. Se eliminaron {total_deleted} alertas duplicadas."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar duplicados: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
