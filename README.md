# 🚨 API de Alertas - Noticias y Tweets

Sistema FastAPI que analiza noticias y tweets desde MongoDB, generando alertas automáticas inteligentes basadas en **scoring de relevancia**, palabras clave contextuales, y detección de patrones financieros.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Ejecución](#-ejecución)
- [Endpoints](#-endpoints)
- [Modelos de Datos](#-modelos-de-datos)
- [Tipos de Alertas](#-tipos-de-alertas)
- [Sistema de Scoring](#-sistema-de-scoring)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Personalización](#-personalización)

---

## ✨ Características

- 🔌 Conexión a MongoDB Atlas (Motor async)
- 📰 Análisis de noticias (colección `news`)
- 🐦 Análisis de tweets (colección `tweets`)
- 🎯 **Sistema de scoring inteligente** para relevancia
- 📊 Detección prioritaria de tickers argentinos (`YPF`, `GGAL`, `PAMP`, etc.)
- 🧠 Análisis contextual (palabras de magnitud, porcentajes, montos)
- ⏰ Filtros temporales (últimas 24h noticias, 12h tweets)
- 🕐 Ajuste de sensibilidad según horario de mercado
- 🔥 Identificación de contenido viral con engagement
- 💾 Almacenamiento en MongoDB (colección `alerts`)
- 🎯 Sistema de prioridades (low, medium, high, critical)
- 🌐 API REST completa con FastAPI

> **Nota:** Este sistema usa **análisis basado en reglas mejorado** con scoring contextual y umbrales dinámicos, no Machine Learning.

---

## � Instalación

```bash
# Clonar/Descargar el proyecto
cd Alertas

# Instalar dependencias
pip install fastapi uvicorn[standard] motor pymongo python-dotenv pydantic pydantic-settings
```

---

## ⚙️ Configuración

Crear archivo `.env` en la raíz del proyecto:

```env
MONGODB_URI=mongodb+srv://admin:password@cluster.mongodb.net/MervalDB?retryWrites=true&w=majority
DATABASE_NAME=MervalDB
DB_PORT=27017
```

---

## ▶️ Ejecución

```bash
# Opción 1: Directo
python main.py

# Opción 2: Con uvicorn
uvicorn main:app --reload

# Opción 3: Puerto personalizado
uvicorn main:app --host 0.0.0.0 --port 8000
```

**URL:** `http://localhost:8000`

**Documentación:** `http://localhost:8000/docs`

---

## � Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Info de la API |
| `GET` | `/health` | Estado de conexión |
| `GET` | `/news` | Todas las noticias |
| `GET` | `/news/recent?limit=50` | Noticias recientes |
| `GET` | `/tweets` | Todos los tweets |
| `GET` | `/tweets/recent?limit=100` | Tweets recientes |
| `GET` | `/alerts` | Todas las alertas |
| `POST` | `/alerts/generate` | ⭐ Generar alertas (combinado) |
| `POST` | `/alerts/generate/news` | Alertas solo de noticias |
| `POST` | `/alerts/generate/tweets` | Alertas solo de tweets |
| `DELETE` | `/alerts` | Eliminar todas las alertas |

---

## 📊 Modelos de Datos

### News (Noticias)

```python
{
  "_id": "ObjectId",           # ID de MongoDB
  "title": "string",           # Título de la noticia
  "content": "string",         # Contenido completo
  "source": "string",          # Fuente (ej: "Ámbito")
  "url": "string",             # URL de la noticia
  "published_date": "datetime", # Fecha de publicación
  "category": "string",        # Categoría
  "keywords": ["string"]       # Palabras clave
}
```

### Tweet (Tweets)

```python
{
  "_id": "ObjectId",
  "text": "string",            # Contenido del tweet
  "author": "string",          # Nombre del autor
  "username": "string",        # @username
  "created_at": "datetime",    # Fecha de creación
  "retweet_count": "int",      # Cantidad de RTs
  "like_count": "int",         # Cantidad de likes
  "reply_count": "int",        # Cantidad de respuestas
  "hashtags": ["string"],      # Hashtags
  "mentions": ["string"],      # Menciones
  "url": "string"              # URL del tweet
}
```

### Alert (Alertas)

```python
{
  "_id": "ObjectId",
  "title": "string",           # Título de la alerta
  "description": "string",     # Descripción detallada
  "type": "string",            # 'news', 'price', 'volume', 'portfolio'
  "enabled": "boolean",        # Estado (default: true)
  "icon": "string",            # Icono UI (ej: 'warning', 'trending-up')
  "config": {                  # Configuración específica
    "symbol": "string",        # Ticker (ej: "YPF", "$AAPL")
    "condition": "string",     # Tipo de condición
    "threshold": "number",     # Umbral numérico
    "timeframe": "string",     # Marco temporal ('1h', '1d')
    "engagement": "number",    # Engagement (solo tweets)
    "username": "string",      # Usuario (solo tweets)
    "source": "string",        # Fuente original
    "url": "string"            # URL de la fuente
  },
  "createdAt": "datetime",     # Fecha de creación
  "lastTriggered": "datetime", # Última activación
  "triggerCount": "int",       # Veces activada
  "priority": "string",        # 'low', 'medium', 'high', 'critical'
  "sourceTitle": "string",     # Título de la fuente original
  "sourceId": "string",        # ID de la noticia/tweet original
  "keywords": ["string"],      # Palabras clave detectadas
  "metadata": {                # Metadata adicional
    "content_type": "string",  # 'news' o 'tweet'
    "author": "string",        # Autor (tweets)
    "engagement": "number",    # Engagement total (tweets)
    "retweets": "number",      # RTs (tweets)
    "likes": "number",         # Likes (tweets)
    "tickers": ["string"],     # Tickers detectados (tweets)
    "hashtags": ["string"],    # Hashtags (tweets)
    "category": "string",      # Categoría (news)
    "source": "string"         # Fuente
  }
}
```

---

## 🎯 Tipos de Alertas

### Por Tipo (`type`)

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `news` | Noticias y eventos | Noticias críticas, positivas |
| `price` | Movimientos de precio | Caídas importantes |
| `volume` | Volumen anormal | Tweets virales, tendencias |
| `portfolio` | Alertas de cartera | (Futuro) |

### Por Prioridad (`priority`)

| Prioridad | Condición | Ejemplo |
|-----------|-----------|---------|
| `critical` | Eventos críticos + viralidad | Crisis en tweet viral |
| `high` | Movimientos importantes | Caídas, alertas sociales |
| `medium` | Análisis, tendencias | Volatilidad, tickers virales |
| `low` | Informativo, positivo | Noticias generales, ganancias |

---

## 🧠 Sistema de Scoring

El sistema evalúa la relevancia de cada noticia/tweet mediante un **score de 0.0 a 2.0+**:

### Componentes del Score

1. **Peso Base de Keyword** (0.5 - 1.0)
   - `critical`: 1.0 (crisis, default, colapso)
   - `high`: 0.8 (caída, alza, volatilidad)
   - `medium`: 0.6 (análisis, proyección)
   - `positive`: 0.5 (ganancia, récord)

2. **Contexto** (+0.2 - +0.5)
   - Palabras de refuerzo cerca de la keyword
   - Ejemplo: "caída **fuerte**" → +0.3

3. **Magnitud** (×1.2 - ×1.5)
   - Palabras como "fuerte", "histórico", "récord"
   - Multiplican el score base

4. **Porcentajes Detectados** (+0.1 - +0.3)
   - Presencia de % específicos aumenta relevancia

5. **Engagement (Tweets)** (×1.2 - ×1.5)
   - >100 engagement: ×1.2
   - >500 engagement: ×1.5

### Umbrales de Creación

Las alertas se crean cuando **score ≥ threshold**:

| Prioridad | Threshold Normal | Durante Mercado |
|-----------|-----------------|-----------------|
| `critical` | 0.8 | 0.64 (-20%) |
| `high` | 0.6 | 0.48 (-20%) |
| `medium` | 0.5 | 0.40 (-20%) |
| `positive` | 0.7 | 0.56 (-20%) |

> **Horario de mercado argentino:** Lunes a Viernes, 11:00-17:00 ART

### Ejemplo de Cálculo

**Noticia:** "YPF sufre caída fuerte del 8% por default de Argentina"

```python
# 1. Keyword "caída" (high) → peso base: 0.8
# 2. Contexto "fuerte" → +0.3
# 3. Magnitud "fuerte" → ×1.3
# 4. Porcentaje "8%" → +0.2
# 5. Score final: (0.8 + 0.3) × 1.3 + 0.2 = 1.63

# ✅ 1.63 > 0.6 (threshold high) → Se crea alerta HIGH
```

### Filtros Temporales

- **Noticias:** Últimas 24 horas
- **Tweets:** Últimas 12 horas

### Tickers Priorizados

El sistema prioriza **20 tickers argentinos**:
```
YPF, GGAL, PAMP, ALUA, BMA, COME, CRES, EDN, 
LOMA, MIRG, SUPV, TECO2, TGNO4, TGSU2, TRAN, 
TXAR, VALO, CEPU, BYMA, BBAR
```

---

### Iconos Utilizados

| Icono | Uso |
|-------|-----|
| `trending-up` | Noticias positivas, subas |
| `trending-down` | Caídas, pérdidas |
| `warning` | Alertas críticas |
| `stats-chart` | Análisis de mercado |
| `flash` | Tendencias virales |
| `bar-chart` | Volumen anormal |
| `document-text` | Noticias generales |

---

## � Ejemplos de Uso

### 1. Generar Alertas (Noticias + Tweets)

```bash
curl -X POST http://localhost:8000/alerts/generate
```

**Respuesta:**
```json
{
  "success": true,
  "alerts_created": 145,
  "news_processed": 100,
  "tweets_processed": 200,
  "message": "Se procesaron 100 noticias y 200 tweets. Se crearon 145 alertas",
  "alerts": [...]
}
```

### 2. Ver Alertas Generadas

```bash
curl http://localhost:8000/alerts
```

### 3. Obtener Tweets Recientes

```bash
curl http://localhost:8000/tweets/recent?limit=50
```

### 4. Python - Filtrar por Prioridad

```python
import requests

# Obtener todas las alertas
response = requests.get('http://localhost:8000/alerts')
alerts = response.json()

# Filtrar por prioridad
critical = [a for a in alerts if a['priority'] == 'critical']
high = [a for a in alerts if a['priority'] == 'high']

print(f"Alertas críticas: {len(critical)}")
print(f"Alertas altas: {len(high)}")
```

### 5. Python - Alertas por Ticker

```python
import requests

response = requests.get('http://localhost:8000/alerts')
alerts = response.json()

# Buscar alertas de un ticker específico
ypf_alerts = [
    a for a in alerts 
    if 'YPF' in a.get('config', {}).get('symbol', '') or
       'YPF' in str(a.get('keywords', []))
]

for alert in ypf_alerts:
    print(f"[{alert['priority'].upper()}] {alert['title']}")
```

---

## 🛠️ Personalización

### Modificar Palabras Clave

Edita `services.py` en las funciones `analyze_news_for_alerts()` y `analyze_tweet_for_alerts()`:

```python
# Ejemplo: agregar nueva palabra crítica
critical_keywords = ['crisis', 'crash', 'colapso', 'quiebra', 'default', 'suspensión', 'bancarrota']
```

### Ajustar Umbral de Viralidad

En `services.py`, método `analyze_tweet_for_alerts()`:

```python
# Cambiar de 100 a 500
is_viral = engagement > 500
```

### Cambiar Límites de Procesamiento

En `services.py`, métodos `process_*_and_create_alerts()`:

```python
# Cambiar cantidad de items a procesar
news_list = await NewsService.get_recent_news(limit=200)  # era 100
tweets_list = await TweetService.get_recent_tweets(limit=500)  # era 200
```

### Agregar Nuevos Tipos de Alertas

En `services.py`, agregar nueva lógica en las funciones `analyze_*_for_alerts()`:

```python
# Ejemplo: detectar dividendos
dividend_keywords = ['dividendo', 'dividendos', 'pago', 'distribución']
for keyword in dividend_keywords:
    if keyword in text_to_analyze:
        alerts.append(Alert(
            title=f"Dividendos: {symbol}",
            description=f"Anuncio de dividendos detectado",
            alert_type="news",
            icon="cash",
            priority="medium",
            # ... resto de campos
        ))
```

---

## 📁 Estructura del Proyecto

```
Alertas/
├── main.py              # Aplicación FastAPI principal
├── config.py            # Configuración y variables de entorno
├── database.py          # Conexión a MongoDB
├── models.py            # Modelos Pydantic (News, Tweet, Alert)
├── services.py          # Lógica de negocio y análisis
├── requirements.txt     # Dependencias
├── .env                 # Variables de entorno
├── .gitignore          # Archivos ignorados
├── README.md           # Esta documentación
├── FORMATO_ALERTAS.md  # Ejemplos de formato JSON
└── EJEMPLOS_USO.md     # Ejemplos adicionales
```

---

## � Detalles de Análisis

### Detección de Tickers

**En Noticias:**
- Busca palabras en mayúsculas de 2-5 letras
- Ejemplo: `YPF`, `GGAL`, `MERVAL`

**En Tweets:**
- Busca símbolos con `$` adelante
- Ejemplo: `$AAPL`, `$TSLA`, `$YPF`

### Cálculo de Engagement (Tweets)

```python
engagement = retweet_count + like_count + reply_count
is_viral = engagement > 100
```

### Escalado de Prioridad

Los tweets virales (engagement > 100) escalan la prioridad:
- `medium` → `high`
- `high` → `critical`

### Sistema de Análisis

**Método:** Análisis basado en reglas determinísticas (sin Machine Learning)

```python
# Búsqueda simple de palabras clave
critical_keywords = ['crisis', 'crash', 'colapso']
if keyword in text.lower():
    create_critical_alert()

# Comparación numérica
engagement = retweets + likes + replies
if engagement > 100:
    mark_as_viral()
```

**Ventajas:**
- ⚡ Rápido y eficiente
- 🎯 Predecible y controlable
- 🔧 Fácil de personalizar
- 💰 Sin costos de ML/APIs externas

---

## 📝 Notas

- Las alertas se crean con `enabled: true` por defecto
- `lastTriggered` se establece solo si la alerta se activó
- `triggerCount` cuenta cuántas veces se activó
- Los campos opcionales pueden ser `null`
- Las fechas se guardan en formato ISO 8601
- Los `_id` de MongoDB se convierten a strings

---

## 🔗 Enlaces Útiles

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 📄 Licencia

Proyecto de uso libre para análisis de mercados financieros.

---

**Versión:** 2.0.0 | **Fecha:** Octubre 2025
