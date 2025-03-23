#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Datainnsamlingsmodul for AutoTrader One.
"""

import logging
import os
import asyncio
import time
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
from functools import lru_cache

from data_sources.market_data import get_market_data_provider
from data_sources.news import get_news_provider
from data_sources.fundamentals import get_fundamentals_provider

class DataCollector:
    """Klasse for å samle inn data fra ulike kilder."""
    
    def __init__(self, config: Dict):
        """
        Initialiserer DataCollector.
        
        Args:
            config (dict): Applikasjonskonfigurasjon
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Opprett datakatalog hvis den ikke eksisterer
        self.data_dir = 'data'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Initialiser dataprovideren
        market_config = config.get('data_sources', {}).get('market_data', {})
        news_config = config.get('data_sources', {}).get('news', {})
        fundamentals_config = config.get('data_sources', {}).get('fundamentals', {})
        
        self.market_provider = get_market_data_provider(market_config.get('provider', 'yahoo'))
        self.news_provider = get_news_provider(news_config.get('provider', 'newsapi'))
        self.fundamentals_provider = get_fundamentals_provider(fundamentals_config.get('provider', 'yahoo'))
        
        # Cache-innstillinger
        self.cache_ttl = config.get('data_sources', {}).get('cache_ttl', 3600)  # 1 time som standard
    
    async def collect_all(self, symbols: List[str]) -> Dict:
        """
        Samler inn all data for de gitte symbolene asynkront.
        
        Args:
            symbols (list): Liste med aksjesymboler
            
        Returns:
            dict: Samlet markedsdata
        """
        self.logger.info("Starter datainnsamling for %d symboler", len(symbols))
        
        result = {
            'market_data': {},
            'news': {},
            'fundamentals': {},
            'collected_at': datetime.now().isoformat()
        }
        
        # Opprett oppgaver for hvert symbol
        tasks = []
        for symbol in symbols:
            tasks.extend([
                self._collect_symbol_data(symbol, 'market_data'),
                self._collect_symbol_data(symbol, 'news'),
                self._collect_symbol_data(symbol, 'fundamentals')
            ])
        
        # Utfør alle oppgaver parallelt
        results = await asyncio.gather(*tasks)
        
        # Organiser resultatene
        for symbol, data_type, data in results:
            if data_type == 'market_data':
                result['market_data'][symbol] = data
            elif data_type == 'news':
                result['news'][symbol] = data
            elif data_type == 'fundamentals':
                result['fundamentals'][symbol] = data
        
        # Lagre rådata
        await self._save_raw_data(result)
        
        return result
    
    async def _collect_symbol_data(self, symbol: str, data_type: str) -> tuple:
        """
        Samler inn data for et symbol og datatype.
        
        Args:
            symbol (str): Aksjesymbol
            data_type (str): Type data å samle inn
            
        Returns:
            tuple: (symbol, data_type, data)
        """
        try:
            if data_type == 'market_data':
                data = await self.collect_market_data(symbol)
            elif data_type == 'news':
                data = await self.collect_news(symbol)
            elif data_type == 'fundamentals':
                data = await self.collect_fundamentals(symbol)
            else:
                raise ValueError(f"Ukjent datatype: {data_type}")
            
            return symbol, data_type, data
            
        except Exception as e:
            self.logger.error(f"Feil ved innsamling av {data_type} for {symbol}: {str(e)}")
            return symbol, data_type, None
    
    @lru_cache(maxsize=100)
    async def collect_market_data(self, symbol: str) -> Dict:
        """
        Samler inn markedsdata for et symbol med caching.
        
        Args:
            symbol (str): Aksjesymbol
            
        Returns:
            dict: Markedsdata
        """
        days_history = self.config.get('data_sources', {}).get('market_data', {}).get('days_history', 90)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_history)
        
        return await self.market_provider.get_historical_data(symbol, start_date, end_date)
    
    @lru_cache(maxsize=100)
    async def collect_news(self, symbol: str) -> List[Dict]:
        """
        Samler inn nyheter for et symbol med caching.
        
        Args:
            symbol (str): Aksjesymbol
            
        Returns:
            list: Nyhetsartikler
        """
        days_history = self.config.get('data_sources', {}).get('news', {}).get('days_history', 7)
        api_key = self.config.get('data_sources', {}).get('news', {}).get('api_key', '')
        
        if not api_key:
            self.logger.warning("Ingen API-nøkkel for nyheter. Bruker dummydata.")
            return self._get_dummy_news(symbol)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_history)
        
        return await self.news_provider.get_news(symbol, start_date, end_date, api_key)
    
    @lru_cache(maxsize=100)
    async def collect_fundamentals(self, symbol: str) -> Dict:
        """
        Samler inn fundamentale data for et symbol med caching.
        
        Args:
            symbol (str): Aksjesymbol
            
        Returns:
            dict: Fundamentale data
        """
        return await self.fundamentals_provider.get_fundamentals(symbol)
    
    async def _save_raw_data(self, data: Dict) -> None:
        """
        Lagrer rådata til disk asynkront.
        
        Args:
            data (dict): Data som skal lagres
        """
        today = datetime.now().strftime("%Y-%m-%d")
        filename = os.path.join(self.data_dir, f"raw_data_{today}.json")
        
        try:
            # Bruk asyncio for å unngå å blokkere hovedtråden
            await asyncio.to_thread(self._write_json_file, filename, data)
            self.logger.info("Rådata lagret til %s", filename)
        except Exception as e:
            self.logger.error("Feil ved lagring av rådata: %s", str(e))
    
    def _write_json_file(self, filename: str, data: Dict) -> None:
        """Hjelpefunksjon for å skrive JSON-fil synkront."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def _get_dummy_news(self, symbol: str) -> List[Dict]:
        """
        Genererer dummynyheter for testing.
        
        Args:
            symbol (str): Aksjesymbol
            
        Returns:
            list: Dummynyhetsartikler
        """
        return [
            {
                'title': f'Positiv utvikling for {symbol}',
                'description': f'{symbol} viser sterk vekst i siste kvartal.',
                'published_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'source': 'Dummy News',
                'url': f'https://example.com/news/{symbol.lower()}'
            },
            {
                'title': f'Analytikere oppgraderer {symbol}',
                'description': f'Flere analytikere har oppgradert sine anbefalinger for {symbol}.',
                'published_at': (datetime.now() - timedelta(days=3)).isoformat(),
                'source': 'Dummy Financial',
                'url': f'https://example.com/financial/{symbol.lower()}'
            }
        ]

