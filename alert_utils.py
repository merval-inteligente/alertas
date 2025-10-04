"""
Utilidades para análisis mejorado de alertas
"""
import re
from typing import List, Dict, Tuple, Optional


# Tickers argentinos más relevantes
RELEVANT_TICKERS = {
    'YPF', 'GGAL', 'PAMP', 'ALUA', 'TRAN', 'EDN', 'LOMA', 'TXAR', 'COME', 'MIRG',
    'ERAR', 'CRES', 'SUPV', 'TGNO4', 'TGSU2', 'BMA', 'CEPU', 'VALO', 'BYMA', 'CGPA2'
}

# Palabras clave mejoradas con contexto
KEYWORD_PATTERNS = {
    'critical': {
        'crisis': {'weight': 1.0, 'context': ['financiera', 'bancaria', 'mercado']},
        'crash': {'weight': 1.0, 'context': ['bolsa', 'mercado', 'bursátil']},
        'colapso': {'weight': 1.0, 'context': ['económico', 'financiero']},
        'quiebra': {'weight': 1.0, 'context': ['empresa', 'banco']},
        'default': {'weight': 1.0, 'context': ['deuda', 'pago', 'bonos']},
        'suspensión': {'weight': 0.9, 'context': ['cotización', 'operaciones', 'rueda']},
        'pánico': {'weight': 0.9, 'context': ['vendedor', 'comprador', 'mercado']},
        'desplome': {'weight': 1.0, 'context': ['precio', 'acción', 'índice']},
    },
    'high': {
        'caída': {'weight': 0.7, 'context': ['fuerte', 'abrupta', 'importante']},
        'baja': {'weight': 0.6, 'context': ['significativa', 'pronunciada']},
        'descenso': {'weight': 0.6, 'context': ['marcado', 'importante']},
        'pérdida': {'weight': 0.7, 'context': ['millonaria', 'significativa']},
        'riesgo': {'weight': 0.6, 'context': ['alto', 'elevado', 'país']},
        'alerta': {'weight': 0.8, 'context': ['roja', 'máxima']},
        'retroceso': {'weight': 0.6, 'context': ['importante', 'significativo']},
        'desvalorización': {'weight': 0.7, 'context': []},
    },
    'medium': {
        'volátil': {'weight': 0.5, 'context': ['mercado', 'jornada']},
        'volatilidad': {'weight': 0.5, 'context': ['alta', 'incremento']},
        'incertidumbre': {'weight': 0.5, 'context': ['mercado', 'económica']},
        'cambio': {'weight': 0.4, 'context': ['regulatorio', 'normativa']},
        'variación': {'weight': 0.4, 'context': ['precio', 'cotización']},
        'ajuste': {'weight': 0.5, 'context': ['tarifario', 'precio']},
        'corrección': {'weight': 0.5, 'context': ['mercado', 'técnica']},
    },
    'positive': {
        'suba': {'weight': 0.7, 'context': ['fuerte', 'importante', 'récord']},
        'alza': {'weight': 0.7, 'context': ['significativa', 'importante']},
        'ganancia': {'weight': 0.8, 'context': ['récord', 'histórica', 'millonaria']},
        'crecimiento': {'weight': 0.7, 'context': ['sostenido', 'importante']},
        'récord': {'weight': 0.9, 'context': ['histórico', 'máximo']},
        'máximo': {'weight': 0.8, 'context': ['histórico', 'nuevo']},
        'repunte': {'weight': 0.7, 'context': ['fuerte', 'importante']},
        'rally': {'weight': 0.8, 'context': ['alcista', 'bursátil']},
        'recuperación': {'weight': 0.7, 'context': ['importante', 'significativa']},
    }
}

# Palabras que indican magnitud
MAGNITUDE_WORDS = {
    'fuerte': 1.3,
    'importante': 1.2,
    'significativo': 1.2,
    'significativa': 1.2,
    'histórico': 1.5,
    'histórica': 1.5,
    'récord': 1.5,
    'máximo': 1.4,
    'mínimo': 1.4,
    'millonario': 1.3,
    'millonaria': 1.3,
}

# Palabras que indican porcentajes relevantes
PERCENTAGE_PATTERN = r'(\d+(?:\.\d+)?)\s*%'


def extract_tickers(text: str, title_priority: bool = True) -> List[str]:
    """
    Extrae tickers financieros del texto
    Prioriza tickers argentinos conocidos
    """
    # Patrón para tickers: palabras en mayúsculas de 2-5 letras
    ticker_pattern = r'\b[A-Z]{2,5}\b'
    all_tickers = re.findall(ticker_pattern, text)
    
    # Filtrar tickers conocidos
    known_tickers = [t for t in all_tickers if t in RELEVANT_TICKERS]
    
    # Si hay tickers conocidos, priorizarlos
    if known_tickers:
        return list(dict.fromkeys(known_tickers))  # Eliminar duplicados manteniendo orden
    
    # Si no, retornar todos pero sin palabras comunes
    common_words = {'EN', 'LA', 'EL', 'DE', 'CON', 'POR', 'PARA', 'SI', 'NO', 'SE', 'AL'}
    filtered = [t for t in all_tickers if t not in common_words]
    
    return list(dict.fromkeys(filtered[:3]))  # Máximo 3 tickers


def extract_percentages(text: str) -> List[float]:
    """Extrae porcentajes del texto"""
    matches = re.findall(PERCENTAGE_PATTERN, text)
    return [float(m) for m in matches]


def calculate_relevance_score(text: str, keyword: str, priority: str) -> float:
    """
    Calcula un score de relevancia basado en:
    - Presencia del keyword
    - Palabras de contexto cercanas
    - Magnitud mencionada
    - Porcentajes mencionados
    """
    score = 0.0
    text_lower = text.lower()
    
    if keyword not in text_lower:
        return 0.0
    
    # Score base por prioridad
    keyword_info = KEYWORD_PATTERNS.get(priority, {}).get(keyword, {})
    score = keyword_info.get('weight', 0.5)
    
    # Bonus por palabras de contexto relevantes
    context_words = keyword_info.get('context', [])
    for context in context_words:
        if context in text_lower:
            score += 0.2
    
    # Bonus por palabras de magnitud
    for magnitude_word, multiplier in MAGNITUDE_WORDS.items():
        if magnitude_word in text_lower:
            score *= multiplier
            break  # Solo aplicar el primero encontrado
    
    # Bonus por porcentajes relevantes
    percentages = extract_percentages(text)
    if percentages:
        max_pct = max(percentages)
        if priority in ['critical', 'high'] and max_pct >= 5:
            score += 0.3
        elif priority == 'positive' and max_pct >= 3:
            score += 0.2
    
    return round(score, 2)


def find_best_keyword(text: str, keywords_dict: Dict, priority: str) -> Optional[Tuple[str, float]]:
    """
    Encuentra la mejor palabra clave con su score
    """
    best_keyword = None
    best_score = 0.0
    
    for keyword in keywords_dict.keys():
        score = calculate_relevance_score(text, keyword, priority)
        if score > best_score:
            best_score = score
            best_keyword = keyword
    
    return (best_keyword, best_score) if best_keyword else None


def extract_money_amounts(text: str) -> List[str]:
    """Extrae montos de dinero mencionados"""
    # Patrones para diferentes formatos
    patterns = [
        r'\$\s*\d+(?:\.\d+)?\s*(?:millones?|mil millones?|billones?)',
        r'USD?\s*\d+(?:\.\d+)?\s*(?:millones?|mil millones?|M|B)',
        r'\d+(?:\.\d+)?\s*(?:millones?|mil millones?)\s*(?:de)?\s*(?:pesos|dólares)',
    ]
    
    amounts = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        amounts.extend(matches)
    
    return amounts


def is_market_hours() -> bool:
    """
    Verifica si es horario de mercado (más relevante)
    Mercado argentino: Lunes a Viernes, 11:00 - 17:00 ART
    """
    from datetime import datetime
    import pytz
    
    try:
        # Zona horaria de Argentina
        tz = pytz.timezone('America/Argentina/Buenos_Aires')
        now = datetime.now(tz)
        
        # Verificar día de semana (0 = Lunes, 4 = Viernes)
        if now.weekday() > 4:
            return False
        
        # Verificar horario (11:00 - 17:00)
        hour = now.hour
        return 11 <= hour < 17
    except:
        # Si hay error, asumir que sí es horario de mercado
        return True


def should_create_alert(score: float, priority: str, during_market_hours: bool = False) -> bool:
    """
    Determina si se debe crear una alerta basado en el score y contexto
    """
    # Umbrales mínimos por prioridad
    thresholds = {
        'critical': 0.8,
        'high': 0.6,
        'medium': 0.5,
        'positive': 0.7,
        'low': 0.4
    }
    
    threshold = thresholds.get(priority, 0.5)
    
    # Reducir umbral durante horario de mercado (más sensible)
    if during_market_hours:
        threshold *= 0.8
    
    return score >= threshold
