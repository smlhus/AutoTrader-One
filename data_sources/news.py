#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nyhetsprovider for AutoTrader One.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import random
import asyncio
from typing import Dict, List, Optional
from newsapi import NewsApiClient

class NewsProvider(ABC):
    """Abstrakt baseklasse for nyhetsprovideren."""
    
    @abstractmethod
    async def get_news(self, symbol: str, start_date: datetime, end_date: datetime, api_key: str) -> List[Dict]:
        """
        Henter nyheter for et symbol.
        
        Args:
            symbol (str): Aksjesymbol
            start_date (datetime): Startdato
            end_date (datetime): Sluttdato
            api_key (str): API-nøkkel
            
        Returns:
            list: Liste med nyhetsartikler
        """
        pass

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
        
        # Hent konfigurasjon
        self.api_key = config.get('api_key', 'test_api_key_123')
        self.language = config.get('language', 'no')
        self.days_back = config.get('days_back', 7)
        
        # Initialiser NewsAPI-klient
        self.client = None
        if self.api_key != 'test_api_key_123':
            self.client = NewsApiClient(api_key=self.api_key)
    
    async def get_news(self, symbol: str) -> List[Dict]:
        """
        Henter nyheter for et symbol.
        
        Args:
            symbol (str): Symbol å hente nyheter for
            
        Returns:
            List[Dict]: Liste med nyhetsartikler
        """
        try:
            # Hvis vi ikke har en gyldig API-nøkkel, returner dummy-data
            if not self.client:
                self.logger.warning(f"Mangler gyldig API-nøkkel, returnerer dummy-nyheter for {symbol}")
                return self._get_dummy_news(symbol)
            
            # Konverter symbol til selskapsnavn
            company_name = self._get_company_name(symbol)
            
            # Sett opp søkeparametere
            from_date = (datetime.now() - timedelta(days=self.days_back)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            # Utfør søk
            self.logger.info(f"Henter nyheter for {company_name} fra {from_date} til {to_date}")
            response = self.client.get_everything(
                q=company_name,
                language=self.language,
                from_param=from_date,
                to=to_date,
                sort_by='relevancy'
            )
            
            # Konverter til vårt format
            articles = []
            for article in response.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', '')
                })
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Feil ved henting av nyheter for {symbol}: {str(e)}")
            return self._get_dummy_news(symbol)
    
    def _get_company_name(self, symbol: str) -> str:
        """
        Konverterer symbol til selskapsnavn.
        
        Args:
            symbol (str): Symbol å konvertere
            
        Returns:
            str: Selskapsnavn
        """
        # Mapping for norske selskaper
        company_names = {
            'EQNR.OL': 'Equinor',
            'DNB.OL': 'DNB Bank',
            'MOWI.OL': 'Mowi',
            'YAR.OL': 'Yara International',
            'AKRBP.OL': 'Aker BP',
            'TEL.OL': 'Telenor',
            'ORK.OL': 'Orkla',
            'AKSO.OL': 'Aker Solutions',
            'BAKKA.OL': 'Bakkafrost',
            'GOGL.OL': 'Golden Ocean Group'
        }
        
        # Fjern børssuffiks og konverter til selskapsnavn
        base_symbol = symbol.split('.')[0]
        return company_names.get(symbol, base_symbol)
    
    def _get_dummy_news(self, symbol: str) -> List[Dict]:
        """
        Genererer dummy-nyheter for testing.
        
        Args:
            symbol (str): Symbol å generere nyheter for
            
        Returns:
            List[Dict]: Liste med dummy-nyhetsartikler
        """
        company_name = self._get_company_name(symbol)
        current_time = datetime.now()
        
        return [
            {
                'title': f"{company_name} rapporterer sterke resultater",
                'description': f"{company_name} leverer bedre enn forventet i siste kvartal med solid vekst i både omsetning og resultat.",
                'content': "Dette er en dummy-artikkel for testing.",
                'url': 'https://example.com/news/1',
                'published_at': (current_time - timedelta(days=1)).isoformat(),
                'source': 'Dummy News'
            },
            {
                'title': f"Analytikere positive til {company_name}",
                'description': f"Flere analytikere oppgraderer sine anbefalinger for {company_name} etter sterke markedsutsikter.",
                'content': "Dette er en dummy-artikkel for testing.",
                'url': 'https://example.com/news/2',
                'published_at': (current_time - timedelta(days=2)).isoformat(),
                'source': 'Dummy News'
            },
            {
                'title': f"{company_name} investerer i bærekraft",
                'description': f"{company_name} annonserer nye miljøvennlige initiativer og investeringer i grønn teknologi.",
                'content': "Dette er en dummy-artikkel for testing.",
                'url': 'https://example.com/news/3',
                'published_at': (current_time - timedelta(days=3)).isoformat(),
                'source': 'Dummy News'
            }
        ]

class FinnhubNewsProvider(NewsProvider):
    """Provider for Finnhub nyheter."""
    
    def __init__(self):
        """Initialiserer Finnhub provider."""
        self.logger = logging.getLogger(__name__)
    
    async def get_news(self, symbol, start_date, end_date, api_key=None):
        """
        Henter nyheter fra Finnhub.
        
        Args:
            symbol (str): Aksjesymbol
            start_date (datetime): Startdato
            end_date (datetime): Sluttdato
            api_key (str, optional): API-nøkkel
            
        Returns:
            list: Nyhetsartikler
        """
        self.logger.info("Finnhub støtte ikke implementert ennå")
        return []

def get_news_provider(provider_name: str = 'newsapi') -> NewsProvider:
    """
    Factory-funksjon for å opprette news providers.
    
    Args:
        provider_name (str): Navn på provideren
        
    Returns:
        NewsProvider: Provider-instans
    """
    if provider_name.lower() == 'newsapi':
        return NewsAPIProvider()
    else:
        raise ValueError(f"Ukjent news provider: {provider_name}")

