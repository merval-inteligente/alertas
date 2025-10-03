from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class News(BaseModel):
    """Modelo para las noticias"""
    id: Optional[str] = Field(None, alias="_id")
    title: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    published_date: Optional[datetime] = None
    category: Optional[str] = None
    keywords: Optional[List[str]] = []
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class Tweet(BaseModel):
    """Modelo para los tweets"""
    id: Optional[str] = Field(None, alias="_id")
    text: Optional[str] = None
    author: Optional[str] = None
    username: Optional[str] = None
    created_at: Optional[datetime] = None
    retweet_count: Optional[int] = 0
    like_count: Optional[int] = 0
    reply_count: Optional[int] = 0
    hashtags: Optional[List[str]] = []
    mentions: Optional[List[str]] = []
    url: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class Alert(BaseModel):
    """Modelo para las alertas generadas"""
    id: Optional[str] = Field(None, alias="_id")
    title: str
    description: str
    alert_type: str = Field(..., alias="type")  # 'price', 'volume', 'news', 'sentiment', 'portfolio', etc.
    enabled: bool = True
    icon: str = "notifications"  # 'trending-up', 'warning', 'stats-chart', etc.
    config: dict = Field(default_factory=dict)  # Configuración específica de la alerta
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    last_triggered: Optional[datetime] = Field(None, alias="lastTriggered")
    trigger_count: int = Field(default=0, alias="triggerCount")
    priority: str = "medium"  # 'low', 'medium', 'high', 'critical'
    
    # Campos adicionales opcionales
    source_title: Optional[str] = Field(None, alias="sourceTitle")
    source_id: Optional[str] = Field(None, alias="sourceId")  # ID de la noticia/tweet
    keywords: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[dict] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class AlertResponse(BaseModel):
    """Respuesta al crear alertas"""
    success: bool
    alerts_created: int
    alerts: List[Alert]
    news_processed: int = 0
    tweets_processed: int = 0
    message: str
