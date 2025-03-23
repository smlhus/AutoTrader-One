#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DataCollector for AutoTrader One.
"""

import logging
from typing import Dict, Optional
import pandas as pd
from datetime import datetime, timedelta

from .market_data import YahooFinanceProvider
from .news import NewsAPIProvider

class DataCollector:
    """Klasse for å samle data fra ulike kilder."""
    
    def __init__(self, config: Dict):
        """
        Initialiserer DataCollector.
        
        Args:
            config (Dict): Konfigurasjon for datainnsamling
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialiser dataprovideren
        self.market_data_provider = YahooFinanceProvider(
            config.get('market_data', {})
        )
        self.news_provider = NewsAPIProvider(
            config.get('news', {})
        )
        
        # Sett opp caching
        self.cache = {}
        self.cache_timeout = {
            'market_data': config.get('market_data', {}).get('cache_timeout', 300),
            'news': config.get('news', {}).get('cache_timeout', 300),
            'fundamental': config.get('fundamental', {}).get('cache_timeout', 3600)
        }
    
    async def get_market_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Henter markedsdata for et symbol.
        
        Args:
            symbol (str): Symbol å hente data for
            
        Returns:
            Optional[pd.DataFrame]: Markedsdata eller None ved feil
        """
        try:
            cache_key = f"market_data_{symbol}"
            
            # Sjekk cache
            if self._is_cache_valid(cache_key, 'market_data'):
                self.logger.debug(f"Bruker cachet markedsdata for {symbol}")
                return self.cache[cache_key]['data']
            
            # Hent ferske data
            self.logger.info(f"Henter markedsdata for {symbol}")
            data = await self.market_data_provider.get_historical_data(symbol)
            
            # Cache data
            if data is not None:
                self._cache_data(cache_key, data, 'market_data')
            
            return data
            
        except Exception as e:
            self.logger.error(f"Feil ved henting av markedsdata for {symbol}: {str(e)}")
            return None
    
    async def get_news_data(self, symbol: str) -> Optional[list]:
        """
        Henter nyhetsdata for et symbol.
        
        Args:
            symbol (str): Symbol å hente data for
            
        Returns:
            Optional[list]: Nyhetsdata eller None ved feil
        """
        try:
            cache_key = f"news_{symbol}"
            
            # Sjekk cache
            if self._is_cache_valid(cache_key, 'news'):
                self.logger.debug(f"Bruker cachet nyhetsdata for {symbol}")
                return self.cache[cache_key]['data']
            
            # Hent ferske data
            self.logger.info(f"Henter nyhetsdata for {symbol}")
            data = await self.news_provider.get_news(symbol)
            
            # Cache data
            if data is not None:
                self._cache_data(cache_key, data, 'news')
            
            return data
            
        except Exception as e:
            self.logger.error(f"Feil ved henting av nyhetsdata for {symbol}: {str(e)}")
            return None
    
    async def get_fundamental_data(self, symbol: str) -> Optional[Dict]:
        """
        Henter fundamental data for et symbol.
        
        Args:
            symbol (str): Symbol å hente data for
            
        Returns:
            Optional[Dict]: Fundamental data eller None ved feil
        """
        try:
            cache_key = f"fundamental_{symbol}"
            
            # Sjekk cache
            if self._is_cache_valid(cache_key, 'fundamental'):
                self.logger.debug(f"Bruker cachet fundamental data for {symbol}")
                return self.cache[cache_key]['data']
            
            # Hent ferske data
            self.logger.info(f"Henter fundamental data for {symbol}")
            data = await self.market_data_provider.get_fundamentals(symbol)
            
            # Cache data
            if data is not None:
                self._cache_data(cache_key, data, 'fundamental')
            
            return data
            
        except Exception as e:
            self.logger.error(f"Feil ved henting av fundamental data for {symbol}: {str(e)}")
            return None
    
    def _is_cache_valid(self, key: str, data_type: str) -> bool:
        """
        Sjekker om cachet data er gyldig.
        
        Args:
            key (str): Cache-nøkkel
            data_type (str): Type data
            
        Returns:
            bool: True hvis cache er gyldig
        """
        if key not in self.cache:
            return False
            
        cache_entry = self.cache[key]
        cache_age = (datetime.now() - cache_entry['timestamp']).total_seconds()
        
        return cache_age < self.cache_timeout[data_type]
    
    def _cache_data(self, key: str, data: any, data_type: str) -> None:
        """
        Cacher data.
        
        Args:
            key (str): Cache-nøkkel
            data (any): Data som skal caches
            data_type (str): Type data
        """
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        self.logger.debug(f"Cachet {data_type} data med nøkkel {key}")
    
    def clear_cache(self) -> None:
        """Tømmer cachen."""
        self.cache = {}
        self.logger.info("Cache tømt") 