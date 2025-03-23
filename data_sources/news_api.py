#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NewsAPI dataprovider for AutoTrader One.
"""

import logging
from typing import Dict, List, Optional
import requests
from datetime import datetime, timedelta
from textblob import TextBlob

class NewsAPIProvider:
    """Klasse for å hente nyheter fra NewsAPI."""
    
    def __init__(self, config: Dict):
        """
        Initialiserer NewsAPIProvider.
        
        Args:
            config (Dict): Konfigurasjon for dataprovideren
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Hent API-nøkkel fra konfigurasjon
        self.api_key = config.get('api_key')
        if not self.api_key:
            raise ValueError("NewsAPI API-nøkkel mangler i konfigurasjonen")
        
        # Sett opp base URL
        self.base_url = "https://newsapi.org/v2"
        
        # Sett opp cache
        self.cache = {}
        self.cache_timeout = config.get('cache_timeout', 1800)  # 30 minutter som standard
    
    async def get_news(self, symbol: str, days: int = 7) -> Optional[List[Dict]]:
        """
        Henter nyheter for et symbol.
        
        Args:
            symbol (str): Symbol å hente nyheter for
            days (int): Antall dager å hente nyheter for
            
        Returns:
            Optional[List[Dict]]: Liste med nyheter eller None ved feil
        """
        try:
            # Sjekk cache
            cache_key = f"news_{symbol}_{days}"
            if self._is_cache_valid(cache_key):
                self.logger.debug(f"Bruker cachet nyheter for {symbol}")
                return self.cache[cache_key]['data']
            
            # Hent data fra NewsAPI
            self.logger.info(f"Henter nyheter for {symbol}")
            
            # Beregn datoer
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Hent nyheter
            params = {
                'q': symbol,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'language': 'en',
                'sortBy': 'publishedAt',
                'apiKey': self.api_key
            }
            
            response = requests.get(f"{self.base_url}/everything", params=params)
            
            # Sjekk status
            if response.status_code != 200:
                self.logger.error(f"API-feil: {response.status_code} - {response.text}")
                return None
            
            # Parse JSON
            data = response.json()
            
            # Sjekk for feilmeldinger
            if data.get('status') != 'ok':
                self.logger.error(f"API-feilmelding: {data.get('message', 'Ukjent feil')}")
                return None
            
            # Analyser sentiment for hver nyhet
            articles = data.get('articles', [])
            for article in articles:
                # Hent sentiment
                sentiment = self._analyze_sentiment(article.get('description', ''))
                
                # Legg til sentiment i artikkelen
                article['sentiment'] = sentiment
            
            # Cache data
            self._cache_data(cache_key, articles)
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Feil ved henting av nyheter for {symbol}: {str(e)}")
            return None
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """
        Analyserer sentiment i tekst.
        
        Args:
            text (str): Tekst å analysere
            
        Returns:
            Dict: Sentiment-analyse
        """
        try:
            # Analyser med TextBlob
            analysis = TextBlob(text)
            
            # Beregn sentiment-score
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity
            
            # Bestem sentiment
            if polarity > 0:
                sentiment = 'positive'
            elif polarity < 0:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity
            }
            
        except Exception as e:
            self.logger.error(f"Feil ved sentiment-analyse: {str(e)}")
            return {
                'sentiment': 'neutral',
                'polarity': 0.0,
                'subjectivity': 0.0
            }
    
    def _is_cache_valid(self, key: str) -> bool:
        """
        Sjekker om cachet data er gyldig.
        
        Args:
            key (str): Cache-nøkkel
            
        Returns:
            bool: True hvis cache er gyldig
        """
        if key not in self.cache:
            return False
            
        cache_entry = self.cache[key]
        cache_age = (datetime.now() - cache_entry['timestamp']).total_seconds()
        
        return cache_age < self.cache_timeout
    
    def _cache_data(self, key: str, data: any) -> None:
        """
        Cacher data.
        
        Args:
            key (str): Cache-nøkkel
            data (any): Data som skal caches
        """
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        self.logger.debug(f"Cachet data med nøkkel {key}") 