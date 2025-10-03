from typing import List
from datetime import datetime
from models import News, Tweet, Alert
from database import get_database
import re


class NewsService:
    """Servicio para manejar noticias"""
    
    @staticmethod
    async def get_all_news() -> List[News]:
        """Obtiene todas las noticias de la colección news"""
        db = await get_database()
        news_collection = db["news"]
        
        news_list = []
        async for news_doc in news_collection.find():
            # Convertir ObjectId a string
            if "_id" in news_doc:
                news_doc["_id"] = str(news_doc["_id"])
            news_list.append(News(**news_doc))
        
        return news_list
    
    @staticmethod
    async def get_recent_news(limit: int = 50) -> List[News]:
        """Obtiene las noticias más recientes"""
        db = await get_database()
        news_collection = db["news"]
        
        news_list = []
        cursor = news_collection.find().sort("published_date", -1).limit(limit)
        
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
            # Convertir ObjectId a string
            if "_id" in tweet_doc:
                tweet_doc["_id"] = str(tweet_doc["_id"])
            tweets_list.append(Tweet(**tweet_doc))
        
        return tweets_list
    
    @staticmethod
    async def get_recent_tweets(limit: int = 100) -> List[Tweet]:
        """Obtiene los tweets más recientes"""
        db = await get_database()
        tweets_collection = db["tweets"]
        
        tweets_list = []
        cursor = tweets_collection.find().sort("created_at", -1).limit(limit)
        
        async for tweet_doc in cursor:
            if "_id" in tweet_doc:
                tweet_doc["_id"] = str(tweet_doc["_id"])
            tweets_list.append(Tweet(**tweet_doc))
        
        return tweets_list


class AlertService:
    """Servicio para generar y guardar alertas"""
    
    @staticmethod
    def analyze_news_for_alerts(news: News) -> List[Alert]:
        """
        Analiza una noticia y genera alertas basadas en diferentes criterios
        """
        alerts = []
        
        # Palabras clave para diferentes tipos de alertas
        critical_keywords = ['crisis', 'crash', 'colapso', 'quiebra', 'default', 'suspensión']
        high_keywords = ['caída', 'baja', 'descenso', 'pérdida', 'riesgo', 'alerta']
        medium_keywords = ['volátil', 'incertidumbre', 'cambio', 'variación']
        positive_keywords = ['suba', 'ganancia', 'crecimiento', 'récord', 'máximo']
        
        text_to_analyze = f"{news.title or ''} {news.content or ''}".lower()
        
        # Detectar tickers en el texto
        ticker_pattern = r'\b[A-Z]{2,5}\b'
        tickers = list(set(re.findall(ticker_pattern, news.title or '')))
        
        # Detectar alertas críticas
        for keyword in critical_keywords:
            if keyword in text_to_analyze:
                symbol = tickers[0] if tickers else 'MERVAL'
                alerts.append(Alert(
                    title=f"Alerta Crítica: {keyword.capitalize()} detectado",
                    description=f"Se detectó '{keyword}' en: {news.title}",
                    alert_type="news",
                    enabled=True,
                    icon="warning",
                    config={
                        "symbol": symbol,
                        "condition": "critical_event",
                        "threshold": 0,
                        "timeframe": "1d",
                        "source": news.source,
                        "url": news.url
                    },
                    created_at=datetime.utcnow(),
                    last_triggered=datetime.utcnow(),
                    trigger_count=1,
                    priority="critical",
                    source_title=news.title,
                    source_id=news.id,
                    keywords=[keyword] + tickers,
                    metadata={
                        "source": news.source,
                        "url": news.url,
                        "category": news.category,
                        "content_type": "news"
                    }
                ))
                break
        
        # Detectar alertas de alta severidad
        if len(alerts) == 0:
            for keyword in high_keywords:
                if keyword in text_to_analyze:
                    symbol = tickers[0] if tickers else 'MERVAL'
                    alerts.append(Alert(
                        title=f"Movimiento importante: {symbol}",
                        description=f"Se detectó '{keyword}' en: {news.title}",
                        alert_type="price",
                        enabled=True,
                        icon="trending-down",
                        config={
                            "symbol": symbol,
                            "condition": "change_percent",
                            "threshold": -3,
                            "timeframe": "1d",
                            "source": news.source,
                            "url": news.url
                        },
                        created_at=datetime.utcnow(),
                        last_triggered=datetime.utcnow(),
                        trigger_count=1,
                        priority="high",
                        source_title=news.title,
                        source_id=news.id,
                        keywords=[keyword] + tickers,
                        metadata={
                            "source": news.source,
                            "url": news.url,
                            "category": news.category,
                            "content_type": "news"
                        }
                    ))
                    break
        
        # Detectar alertas de severidad media
        if len(alerts) == 0:
            for keyword in medium_keywords:
                if keyword in text_to_analyze:
                    symbol = tickers[0] if tickers else 'MERVAL'
                    alerts.append(Alert(
                        title=f"Análisis de mercado: {symbol}",
                        description=f"Se detectó '{keyword}' en: {news.title}",
                        alert_type="news",
                        enabled=True,
                        icon="stats-chart",
                        config={
                            "symbol": symbol,
                            "condition": "market_analysis",
                            "threshold": 0,
                            "timeframe": "1d",
                            "source": news.source,
                            "url": news.url
                        },
                        created_at=datetime.utcnow(),
                        last_triggered=datetime.utcnow(),
                        trigger_count=1,
                        priority="medium",
                        source_title=news.title,
                        source_id=news.id,
                        keywords=[keyword] + tickers,
                        metadata={
                            "source": news.source,
                            "url": news.url,
                            "category": news.category,
                            "content_type": "news"
                        }
                    ))
                    break
        
        # Detectar noticias positivas
        if len(alerts) == 0:
            for keyword in positive_keywords:
                if keyword in text_to_analyze:
                    symbol = tickers[0] if tickers else 'MERVAL'
                    alerts.append(Alert(
                        title=f"{symbol} - Noticia Positiva",
                        description=f"Se detectó '{keyword}' en: {news.title}",
                        alert_type="news",
                        enabled=True,
                        icon="trending-up",
                        config={
                            "symbol": symbol,
                            "condition": "positive_news",
                            "threshold": 0,
                            "timeframe": "1d",
                            "source": news.source,
                            "url": news.url
                        },
                        created_at=datetime.utcnow(),
                        last_triggered=datetime.utcnow(),
                        trigger_count=1,
                        priority="low",
                        source_title=news.title,
                        source_id=news.id,
                        keywords=[keyword] + tickers,
                        metadata={
                            "source": news.source,
                            "url": news.url,
                            "category": news.category,
                            "content_type": "news"
                        }
                    ))
                    break
        
        # Si no se detectó ninguna alerta específica, crear una alerta informativa
        if len(alerts) == 0 and news.title:
            symbol = tickers[0] if tickers else 'MERVAL'
            alerts.append(Alert(
                title=f"Nueva noticia: {symbol}",
                description=news.title,
                alert_type="news",
                enabled=True,
                icon="document-text",
                config={
                    "symbol": symbol,
                    "condition": "news_update",
                    "threshold": 0,
                    "timeframe": "1d",
                    "source": news.source,
                    "url": news.url
                },
                created_at=datetime.utcnow(),
                trigger_count=0,
                priority="low",
                source_title=news.title,
                source_id=news.id,
                keywords=news.keywords or tickers,
                metadata={
                    "source": news.source,
                    "url": news.url,
                    "category": news.category,
                    "content_type": "news"
                }
            ))
        
        return alerts
    
    @staticmethod
    def analyze_tweet_for_alerts(tweet: Tweet) -> List[Alert]:
        """
        Analiza un tweet y genera alertas basadas en diferentes criterios
        """
        alerts = []
        
        # Palabras clave para diferentes tipos de alertas
        critical_keywords = ['crisis', 'crash', 'colapso', 'quiebra', 'default', 'suspensión', 'pánico']
        high_keywords = ['caída', 'baja', 'descenso', 'pérdida', 'riesgo', 'alerta', 'cuidado']
        medium_keywords = ['volátil', 'incertidumbre', 'cambio', 'variación', 'atención']
        positive_keywords = ['suba', 'ganancia', 'crecimiento', 'récord', 'máximo', 'bull', 'rally']
        
        # Símbolos financieros comunes
        ticker_pattern = r'\$[A-Z]{2,5}'
        
        text_to_analyze = (tweet.text or '').lower()
        
        # Detectar tickers mencionados
        tickers = re.findall(ticker_pattern, tweet.text or '')
        
        # Calcular engagement (viralidad)
        engagement = (tweet.retweet_count or 0) + (tweet.like_count or 0) + (tweet.reply_count or 0)
        is_viral = engagement > 100  # Umbral de viralidad
        
        # Detectar alertas críticas
        for keyword in critical_keywords:
            if keyword in text_to_analyze:
                priority = "critical" if is_viral else "high"
                symbol = tickers[0] if tickers else 'MERVAL'
                
                alerts.append(Alert(
                    title=f"Alerta Twitter: {keyword.capitalize()} - {symbol}",
                    description=f"Tweet {'viral ' if is_viral else ''}detectó '{keyword}': {tweet.text[:100]}...",
                    alert_type="news",
                    enabled=True,
                    icon="warning",
                    config={
                        "symbol": symbol,
                        "condition": "social_critical",
                        "threshold": 0,
                        "timeframe": "1h",
                        "engagement": engagement,
                        "username": tweet.username
                    },
                    created_at=datetime.utcnow(),
                    last_triggered=datetime.utcnow(),
                    trigger_count=1,
                    priority=priority,
                    source_title=f"@{tweet.username}: {tweet.text[:80]}",
                    source_id=tweet.id,
                    keywords=[keyword] + tickers,
                    metadata={
                        "author": tweet.author,
                        "username": tweet.username,
                        "engagement": engagement,
                        "retweets": tweet.retweet_count,
                        "likes": tweet.like_count,
                        "hashtags": tweet.hashtags,
                        "tickers": tickers,
                        "content_type": "tweet",
                        "url": tweet.url
                    }
                ))
                break
        
        # Detectar alertas de alta severidad
        if len(alerts) == 0:
            for keyword in high_keywords:
                if keyword in text_to_analyze:
                    priority = "high" if is_viral else "medium"
                    symbol = tickers[0] if tickers else 'MERVAL'
                    
                    alerts.append(Alert(
                        title=f"{symbol} - Alerta en redes sociales",
                        description=f"Tweet detectó '{keyword}': {tweet.text[:100]}...",
                        alert_type="volume",
                        enabled=True,
                        icon="bar-chart",
                        config={
                            "symbol": symbol,
                            "condition": "social_alert",
                            "threshold": engagement,
                            "timeframe": "1h",
                            "engagement": engagement,
                            "username": tweet.username
                        },
                        created_at=datetime.utcnow(),
                        last_triggered=datetime.utcnow(),
                        trigger_count=1,
                        priority=priority,
                        source_title=f"@{tweet.username}: {tweet.text[:80]}",
                        source_id=tweet.id,
                        keywords=[keyword] + tickers,
                        metadata={
                            "author": tweet.author,
                            "username": tweet.username,
                            "engagement": engagement,
                            "retweets": tweet.retweet_count,
                            "likes": tweet.like_count,
                            "hashtags": tweet.hashtags,
                            "tickers": tickers,
                            "content_type": "tweet",
                            "url": tweet.url
                        }
                    ))
                    break
        
        # Detectar tendencias (tweets virales con tickers)
        if len(alerts) == 0 and is_viral and len(tickers) > 0:
            symbol = tickers[0]
            alerts.append(Alert(
                title=f"{symbol} en tendencia en redes",
                description=f"Tweet viral sobre {', '.join(tickers)}: {tweet.text[:100]}...",
                alert_type="volume",
                enabled=True,
                icon="flash",
                config={
                    "symbol": symbol,
                    "condition": "volume_spike",
                    "threshold": 200,
                    "timeframe": "1h",
                    "engagement": engagement,
                    "username": tweet.username
                },
                created_at=datetime.utcnow(),
                last_triggered=datetime.utcnow(),
                trigger_count=1,
                priority="medium",
                source_title=f"@{tweet.username}: {tweet.text[:80]}",
                source_id=tweet.id,
                keywords=tickers,
                metadata={
                    "author": tweet.author,
                    "username": tweet.username,
                    "engagement": engagement,
                    "retweets": tweet.retweet_count,
                    "likes": tweet.like_count,
                    "hashtags": tweet.hashtags,
                    "tickers": tickers,
                    "content_type": "tweet",
                    "url": tweet.url
                }
            ))
        
        # Detectar sentimiento positivo
        if len(alerts) == 0:
            for keyword in positive_keywords:
                if keyword in text_to_analyze:
                    symbol = tickers[0] if tickers else 'MERVAL'
                    
                    alerts.append(Alert(
                        title=f"{symbol} - Sentimiento positivo",
                        description=f"Tweet positivo: {tweet.text[:100]}...",
                        alert_type="news",
                        enabled=True,
                        icon="trending-up",
                        config={
                            "symbol": symbol,
                            "condition": "positive_sentiment",
                            "threshold": 0,
                            "timeframe": "1h",
                            "engagement": engagement,
                            "username": tweet.username
                        },
                        created_at=datetime.utcnow(),
                        trigger_count=0,
                        priority="low",
                        source_title=f"@{tweet.username}: {tweet.text[:80]}",
                        source_id=tweet.id,
                        keywords=[keyword] + tickers,
                        metadata={
                            "author": tweet.author,
                            "username": tweet.username,
                            "engagement": engagement,
                            "retweets": tweet.retweet_count,
                            "likes": tweet.like_count,
                            "hashtags": tweet.hashtags,
                            "tickers": tickers,
                            "content_type": "tweet",
                            "url": tweet.url
                        }
                    ))
                    break
        
        return alerts
    
    @staticmethod
    async def save_alerts(alerts: List[Alert]) -> int:
        """Guarda las alertas en la colección alerts"""
        if not alerts:
            return 0
        
        db = await get_database()
        alerts_collection = db["alerts"]
        
        # Convertir alertas a diccionarios usando los alias
        alerts_dict = []
        for alert in alerts:
            alert_data = alert.model_dump(by_alias=True, exclude_none=True)
            # Asegurar que _id no esté presente para que MongoDB lo genere
            if "_id" in alert_data:
                del alert_data["_id"]
            alerts_dict.append(alert_data)
        
        # Insertar en la base de datos
        result = await alerts_collection.insert_many(alerts_dict)
        
        return len(result.inserted_ids)
    
    @staticmethod
    async def get_all_alerts() -> List[Alert]:
        """Obtiene todas las alertas"""
        db = await get_database()
        alerts_collection = db["alerts"]
        
        alerts_list = []
        async for alert_doc in alerts_collection.find().sort("createdAt", -1):
            # Convertir _id a string
            if "_id" in alert_doc:
                alert_doc["_id"] = str(alert_doc["_id"])
            alerts_list.append(Alert(**alert_doc))
        
        return alerts_list
    
    @staticmethod
    async def process_news_and_create_alerts() -> dict:
        """Procesa todas las noticias y crea alertas"""
        # Obtener noticias recientes
        news_list = await NewsService.get_recent_news(limit=100)
        
        all_alerts = []
        for news in news_list:
            alerts = AlertService.analyze_news_for_alerts(news)
            all_alerts.extend(alerts)
        
        # Guardar alertas
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
        """Procesa todos los tweets y crea alertas"""
        # Obtener tweets recientes
        tweets_list = await TweetService.get_recent_tweets(limit=200)
        
        all_alerts = []
        for tweet in tweets_list:
            alerts = AlertService.analyze_tweet_for_alerts(tweet)
            all_alerts.extend(alerts)
        
        # Guardar alertas
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
        # Obtener noticias recientes
        news_list = await NewsService.get_recent_news(limit=100)
        
        # Obtener tweets recientes
        tweets_list = await TweetService.get_recent_tweets(limit=200)
        
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
