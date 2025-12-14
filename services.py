from typing import List
from datetime import datetime, timedelta
from models import News, Tweet, Alert
from database import get_database
import re
from alert_utils import (
    extract_tickers, extract_percentages, calculate_relevance_score,
    find_best_keyword, should_create_alert, is_market_hours,
    KEYWORD_PATTERNS, extract_money_amounts
)


class NewsService:
    """Servicio para manejar noticias"""
    
    @staticmethod
    async def get_all_news() -> List[News]:
        """Obtiene todas las noticias de la colección news"""
        db = await get_database()
        news_collection = db["news"]
        
        news_list = []
        async for news_doc in news_collection.find():
            if "_id" in news_doc:
                news_doc["_id"] = str(news_doc["_id"])
            news_list.append(News(**news_doc))
        
        return news_list
    
    @staticmethod
    async def get_recent_news(limit: int = 50, hours: int = 168) -> List[News]:
        """Obtiene las noticias más recientes (por _id si no hay fecha)"""
        db = await get_database()
        news_collection = db["news"]
        
        cutoff_date = datetime.utcnow() - timedelta(hours=hours)
        
        news_list = []
        # Buscar noticias con fecha válida O sin fecha (null)
        cursor = news_collection.find({
            "$or": [
                {"published_date": {"$gte": cutoff_date}},
                {"published_date": None},
                {"published_date": {"$exists": False}}
            ]
        }).sort("_id", -1).limit(limit)
        
        async for news_doc in cursor:
            if "_id" in news_doc:
                news_doc["_id"] = str(news_doc["_id"])
            news_list.append(News(**news_doc))
        
        return news_list


class TweetService:
    """Servicio para manejar tweets"""
    
    @staticmethod
    async def get_all_tweets() -> List[Tweet]:
        """Obtiene todos los tweets de la colección tweets"""
        db = await get_database()
        tweets_collection = db["tweets"]
        
        tweets_list = []
        async for tweet_doc in tweets_collection.find():
            if "_id" in tweet_doc:
                tweet_doc["_id"] = str(tweet_doc["_id"])
            tweets_list.append(Tweet(**tweet_doc))
        
        return tweets_list
    
    @staticmethod
    async def get_recent_tweets(limit: int = 100, hours: int = 72) -> List[Tweet]:
        """Obtiene los tweets más recientes (por _id si no hay fecha)"""
        db = await get_database()
        tweets_collection = db["tweets"]
        
        cutoff_date = datetime.utcnow() - timedelta(hours=hours)
        
        tweets_list = []
        # Buscar tweets con fecha válida O sin fecha (null)
        cursor = tweets_collection.find({
            "$or": [
                {"created_at": {"$gte": cutoff_date}},
                {"created_at": None},
                {"created_at": {"$exists": False}}
            ]
        }).sort("_id", -1).limit(limit)
        
        async for tweet_doc in cursor:
            if "_id" in tweet_doc:
                tweet_doc["_id"] = str(tweet_doc["_id"])
            tweets_list.append(Tweet(**tweet_doc))
        
        return tweets_list


class AlertService:
    """Servicio mejorado para generar y guardar alertas"""
    
    @staticmethod
    def analyze_news_for_alerts(news: News) -> List[Alert]:
        """
        Análisis mejorado de noticias con sistema de scoring
        Genera SOLO UNA alerta por noticia (la más relevante)
        """
        alerts = []
        
        text_full = f"{news.title or ''} {news.content or ''}".lower()
        text_title = (news.title or '').lower()
        
        # Extraer información relevante
        tickers = extract_tickers(news.title or '')
        percentages = extract_percentages(text_full)
        money_amounts = extract_money_amounts(text_full)
        during_market = is_market_hours()
        
        # Buscar LA MEJOR keyword (solo una)
        priorities = ['critical', 'high', 'medium', 'positive']
        best_match = None
        best_priority = None
        best_score = 0.0
        
        for priority in priorities:
            keywords = KEYWORD_PATTERNS.get(priority, {})
            result = find_best_keyword(text_full, keywords, priority)
            
            if result:
                keyword, score = result
                if score > best_score and should_create_alert(score, priority, during_market):
                    best_match = keyword
                    best_priority = priority
                    best_score = score
        
        # Crear SOLO UNA alerta con el mejor match
        if best_match and best_priority:
            symbol = tickers[0] if tickers else 'MERVAL'
            
            # Configurar según prioridad
            if best_priority == 'critical':
                alerts.append(Alert(
                    title=f"🚨 {symbol}: {best_match.capitalize()} detectado",
                    description=f"{news.title}",
                    alert_type="news",
                    enabled=True,
                    icon="warning",
                    config={
                        "symbol": symbol,
                        "condition": "critical_event",
                        "threshold": 0,
                        "timeframe": "1d",
                        "source": news.source,
                        "url": news.url,
                        "relevance_score": best_score,
                        "percentages": percentages,
                        "money_amounts": money_amounts
                    },
                    created_at=datetime.utcnow(),
                    last_triggered=datetime.utcnow(),
                    trigger_count=1,
                    priority="critical",
                    source_title=news.title,
                    source_id=news.id,
                    keywords=[best_match] + tickers,
                    metadata={
                        "source": news.source,
                        "url": news.url,
                        "category": news.category,
                        "content_type": "news",
                        "relevance_score": best_score,
                        "during_market_hours": during_market
                    }
                ))
            
            elif best_priority == 'high':
                # Determinar icono según contexto
                icon = "trending-down" if best_match in ['caída', 'baja', 'descenso', 'pérdida'] else "warning"
                
                # Calcular threshold estimado
                threshold = -abs(percentages[0]) if percentages else -3
                
                alerts.append(Alert(
                    title=f"⚠️ {symbol}: {best_match.capitalize()} importante",
                    description=f"{news.title}",
                    alert_type="price",
                    enabled=True,
                    icon=icon,
                    config={
                        "symbol": symbol,
                        "condition": "change_percent",
                        "threshold": threshold,
                        "timeframe": "1d",
                        "source": news.source,
                        "url": news.url,
                        "relevance_score": best_score,
                        "percentages": percentages
                    },
                    created_at=datetime.utcnow(),
                    last_triggered=datetime.utcnow(),
                    trigger_count=1,
                    priority="high",
                    source_title=news.title,
                    source_id=news.id,
                    keywords=[best_match] + tickers,
                    metadata={
                        "source": news.source,
                        "url": news.url,
                        "category": news.category,
                        "content_type": "news",
                        "relevance_score": best_score,
                        "during_market_hours": during_market
                    }
                ))
            
            elif best_priority == 'medium':
                alerts.append(Alert(
                    title=f"📊 {symbol}: Análisis de mercado",
                    description=f"{news.title}",
                    alert_type="news",
                    enabled=True,
                    icon="stats-chart",
                    config={
                        "symbol": symbol,
                        "condition": "market_analysis",
                        "threshold": 0,
                        "timeframe": "1d",
                        "source": news.source,
                        "url": news.url,
                        "relevance_score": best_score
                    },
                    created_at=datetime.utcnow(),
                    last_triggered=datetime.utcnow(),
                    trigger_count=1,
                    priority="medium",
                    source_title=news.title,
                    source_id=news.id,
                    keywords=[best_match] + tickers,
                    metadata={
                        "source": news.source,
                        "url": news.url,
                        "category": news.category,
                        "content_type": "news",
                        "relevance_score": best_score
                    }
                ))
            
            elif best_priority == 'positive':
                threshold = percentages[0] if percentages else 0
                
                alerts.append(Alert(
                    title=f"📈 {symbol}: {best_match.capitalize()}",
                    description=f"{news.title}",
                    alert_type="news",
                    enabled=True,
                    icon="trending-up",
                    config={
                        "symbol": symbol,
                        "condition": "positive_news",
                        "threshold": threshold,
                        "timeframe": "1d",
                        "source": news.source,
                        "url": news.url,
                        "relevance_score": best_score,
                        "percentages": percentages
                    },
                    created_at=datetime.utcnow(),
                    last_triggered=datetime.utcnow(),
                    trigger_count=1,
                    priority="low",
                    source_title=news.title,
                    source_id=news.id,
                    keywords=[best_match] + tickers,
                    metadata={
                        "source": news.source,
                        "url": news.url,
                        "category": news.category,
                        "content_type": "news",
                        "relevance_score": best_score,
                        "during_market_hours": during_market
                    }
                ))
        
        return alerts
    
    @staticmethod
    def analyze_tweet_for_alerts(tweet: Tweet) -> List[Alert]:
        """
        Análisis mejorado de tweets con sistema de scoring
        Genera SOLO UNA alerta por tweet (la más relevante)
        """
        alerts = []
        
        text = (tweet.text or '').lower()
        
        # Detectar tickers con formato $TICKER
        ticker_pattern = r'\$[A-Z]{2,5}'
        tickers = re.findall(ticker_pattern, tweet.text or '')
        
        # Calcular métricas de engagement
        engagement = (tweet.retweet_count or 0) + (tweet.like_count or 0) + (tweet.reply_count or 0)
        
        # Umbrales de viralidad ajustados
        is_highly_viral = engagement > 500
        is_viral = engagement > 100
        is_significant = engagement > 50
        
        # Extraer información
        percentages = extract_percentages(text)
        during_market = is_market_hours()
        
        # Buscar LA MEJOR keyword (solo una)
        priorities = ['critical', 'high', 'medium', 'positive']
        best_match = None
        best_priority = None
        best_score = 0.0
        
        for priority in priorities:
            keywords = KEYWORD_PATTERNS.get(priority, {})
            result = find_best_keyword(text, keywords, priority)
            
            if result:
                keyword, score = result
                # Ajustar score por engagement
                if is_highly_viral:
                    score *= 1.5
                elif is_viral:
                    score *= 1.2
                
                if score > best_score:
                    best_match = keyword
                    best_priority = priority
                    best_score = score
        
        # Crear SOLO UNA alerta con el mejor match si es relevante
        if (len(tickers) > 0 or is_highly_viral) and best_match:
            symbol = tickers[0] if tickers else 'MERVAL'
            
            # Determinar prioridad final basada en viralidad
            if best_priority == 'critical' or (best_priority == 'high' and is_highly_viral):
                final_priority = "critical"
            elif best_priority == 'high' or (best_priority == 'medium' and is_highly_viral):
                final_priority = "high"
            elif is_viral:
                final_priority = "medium"
            else:
                final_priority = "low"
            
            # Crear UNA alerta si es suficientemente relevante
            if final_priority in ['critical', 'high'] or (final_priority == 'medium' and is_viral):
                icon_map = {
                    'critical': 'warning',
                    'high': 'flash',
                    'medium': 'bar-chart',
                    'low': 'trending-up'
                }
                
                # Retornar solo UNA alerta
                return [Alert(
                    title=f"{'🔥 ' if is_highly_viral else ''}Twitter: {symbol} - {best_match.capitalize()}",
                    description=f"@{tweet.username}: {tweet.text[:100]}...",
                    alert_type="volume" if final_priority in ['critical', 'high'] else "news",
                    enabled=True,
                    icon=icon_map.get(final_priority, 'notifications'),
                    config={
                        "symbol": symbol,
                        "condition": "social_trending",
                        "threshold": engagement,
                        "timeframe": "1h",
                        "engagement": engagement,
                        "username": tweet.username,
                        "relevance_score": best_score,
                        "is_viral": is_viral
                    },
                    created_at=datetime.utcnow(),
                    last_triggered=datetime.utcnow(),
                    trigger_count=1,
                    priority=final_priority,
                    source_title=f"@{tweet.username}: {tweet.text[:80]}",
                    source_id=tweet.id,
                    keywords=[best_match] + tickers,
                    metadata={
                        "author": tweet.author,
                        "username": tweet.username,
                        "engagement": engagement,
                        "retweets": tweet.retweet_count,
                        "likes": tweet.like_count,
                        "replies": tweet.reply_count,
                        "hashtags": tweet.hashtags,
                        "tickers": tickers,
                        "content_type": "tweet",
                        "url": tweet.url,
                        "relevance_score": best_score,
                        "is_viral": is_viral,
                        "is_highly_viral": is_highly_viral,
                        "during_market_hours": during_market
                    }
                )]
        
        return []
    
    @staticmethod
    async def save_alerts(alerts: List[Alert]) -> int:
        """Guarda o actualiza las alertas en la colección alerts"""
        if not alerts:
            return 0
        
        db = await get_database()
        alerts_collection = db["alerts"]
        
        modified_count = 0
        
        for alert in alerts:
            # Convertir alerta a diccionario
            alert_data = alert.model_dump(by_alias=True, exclude_none=True)
            if "_id" in alert_data:
                del alert_data["_id"]
            
            try:
                if alert.source_id:
                    # Buscar alerta existente por source_id
                    existing = await alerts_collection.find_one({"sourceId": alert.source_id})
                    
                    if existing:
                        # Si existe, actualizar solo si el contenido cambió significativamente
                        # Comparar títulos para evitar duplicados de contenido
                        if existing.get("title") == alert_data.get("title"):
                            # Mismo contenido, solo actualizar timestamp y contador
                            await alerts_collection.update_one(
                                {"sourceId": alert.source_id},
                                {
                                    "$set": {
                                        "lastTriggered": datetime.utcnow()
                                    },
                                    "$inc": {"triggerCount": 1}
                                }
                            )
                        else:
                            # Contenido diferente, reemplazar alerta completa
                            alert_data["triggerCount"] = existing.get("triggerCount", 0) + 1
                            alert_data["lastTriggered"] = datetime.utcnow()
                            
                            await alerts_collection.update_one(
                                {"sourceId": alert.source_id},
                                {"$set": alert_data}
                            )
                    else:
                        # No existe, insertar nueva alerta
                        await alerts_collection.insert_one(alert_data)
                    
                    modified_count += 1
                else:
                    # Sin source_id, insertar directamente
                    await alerts_collection.insert_one(alert_data)
                    modified_count += 1
                    
            except Exception as e:
                print(f"Error guardando alerta: {e}")
                continue
        
        return modified_count
    
    @staticmethod
    async def get_all_alerts() -> List[Alert]:
        """Obtiene todas las alertas ordenadas por fecha"""
        db = await get_database()
        alerts_collection = db["alerts"]
        
        alerts_list = []
        async for alert_doc in alerts_collection.find().sort("createdAt", -1):
            if "_id" in alert_doc:
                alert_doc["_id"] = str(alert_doc["_id"])
            alerts_list.append(Alert(**alert_doc))
        
        return alerts_list
    
    @staticmethod
    async def process_news_and_create_alerts() -> dict:
        """Procesa noticias recientes y crea alertas"""
        news_list = await NewsService.get_recent_news(limit=100, hours=168)  # 7 días
        
        all_alerts = []
        for news in news_list:
            alerts = AlertService.analyze_news_for_alerts(news)
            all_alerts.extend(alerts)
        
        count = await AlertService.save_alerts(all_alerts)
        
        return {
            "success": True,
            "news_processed": len(news_list),
            "tweets_processed": 0,
            "alerts_created": count,
            "alerts": all_alerts
        }
    
    @staticmethod
    async def process_tweets_and_create_alerts() -> dict:
        """Procesa tweets recientes y crea alertas"""
        tweets_list = await TweetService.get_recent_tweets(limit=200, hours=72)  # 3 días
        
        all_alerts = []
        for tweet in tweets_list:
            alerts = AlertService.analyze_tweet_for_alerts(tweet)
            all_alerts.extend(alerts)
        
        count = await AlertService.save_alerts(all_alerts)
        
        return {
            "success": True,
            "news_processed": 0,
            "tweets_processed": len(tweets_list),
            "alerts_created": count,
            "alerts": all_alerts
        }
    
    @staticmethod
    async def process_all_and_create_alerts() -> dict:
        """Procesa noticias Y tweets, y crea alertas combinadas"""
        # Obtener contenido reciente (7 días noticias, 3 días tweets)
        news_list = await NewsService.get_recent_news(limit=100, hours=168)  # 7 días
        tweets_list = await TweetService.get_recent_tweets(limit=200, hours=72)  # 3 días
        
        all_alerts = []
        
        # Procesar noticias
        for news in news_list:
            alerts = AlertService.analyze_news_for_alerts(news)
            all_alerts.extend(alerts)
        
        # Procesar tweets
        for tweet in tweets_list:
            alerts = AlertService.analyze_tweet_for_alerts(tweet)
            all_alerts.extend(alerts)
        
        # Guardar alertas
        count = await AlertService.save_alerts(all_alerts)
        
        return {
            "success": True,
            "news_processed": len(news_list),
            "tweets_processed": len(tweets_list),
            "alerts_created": count,
            "alerts": all_alerts
        }
