#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Alpha Vantage dataprovider for AutoTrader One.
"""

import logging
from typing import Dict, Optional
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from datetime import datetime, timedelta

class AlphaVantageProvider:
    """Klasse for å hente data fra Alpha Vantage."""
    
    def __init__(self, config: Dict):
        """
        Initialiserer AlphaVantageProvider.
        
        Args:
            config (Dict): Konfigurasjon for dataprovideren
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Hent API-nøkkel fra konfigurasjon
        self.api_key = config.get('api_key')
        if not self.api_key:
            raise ValueError("Alpha Vantage API-nøkkel mangler i konfigurasjonen")
        
        # Initialiser Alpha Vantage klienter
        self.ts = TimeSeries(key=self.api_key, output_format='pandas')
        self.ti = TechIndicators(key=self.api_key, output_format='pandas')
        
        # Sett opp cache
        self.cache = {}
        self.cache_timeout = config.get('cache_timeout', 300)  # 5 minutter som standard
    
    async def get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Henter historiske data for et symbol.
        
        Args:
            symbol (str): Symbol å hente data for
            
        Returns:
            Optional[pd.DataFrame]: Historiske data eller None ved feil
        """
        try:
            # Sjekk cache
            cache_key = f"historical_{symbol}"
            if self._is_cache_valid(cache_key):
                self.logger.debug(f"Bruker cachet historiske data for {symbol}")
                return self.cache[cache_key]['data']
            
            # Hent data fra Alpha Vantage
            self.logger.info(f"Henter historiske data for {symbol}")
            data, meta_data = self.ts.get_daily_adjusted(symbol=symbol, outputsize='full')
            
            if data.empty:
                self.logger.warning(f"Ingen data funnet for {symbol}")
                return None
            
            # Rydd opp data
            data = self._clean_historical_data(data)
            
            # Cache data
            self._cache_data(cache_key, data)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Feil ved henting av historiske data for {symbol}: {str(e)}")
            return None
    
    async def get_technical_indicators(self, symbol: str) -> Optional[Dict]:
        """
        Henter tekniske indikatorer for et symbol.
        
        Args:
            symbol (str): Symbol å hente indikatorer for
            
        Returns:
            Optional[Dict]: Tekniske indikatorer eller None ved feil
        """
        try:
            # Sjekk cache
            cache_key = f"indicators_{symbol}"
            if self._is_cache_valid(cache_key):
                self.logger.debug(f"Bruker cachet tekniske indikatorer for {symbol}")
                return self.cache[cache_key]['data']
            
            # Hent RSI
            rsi, _ = self.ti.get_rsi(symbol=symbol, interval='daily', time_period=14)
            
            # Hent SMA
            sma_20, _ = self.ti.get_sma(symbol=symbol, interval='daily', time_period=20)
            sma_50, _ = self.ti.get_sma(symbol=symbol, interval='daily', time_period=50)
            
            # Hent MACD
            macd, macd_signal, macd_hist, _ = self.ti.get_macd(
                symbol=symbol,
                interval='daily',
                series_type='close',
                fastperiod=12,
                slowperiod=26,
                signalperiod=9
            )
            
            # Samle indikatorer
            indicators = {
                'rsi': rsi,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'macd': macd,
                'macd_signal': macd_signal,
                'macd_hist': macd_hist
            }
            
            # Cache data
            self._cache_data(cache_key, indicators)
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Feil ved henting av tekniske indikatorer for {symbol}: {str(e)}")
            return None
    
    def _clean_historical_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Rydder opp historiske data.
        
        Args:
            data (pd.DataFrame): Rå data fra Alpha Vantage
            
        Returns:
            pd.DataFrame: Ryddet data
        """
        try:
            # Fjern unødvendige kolonner
            columns_to_keep = ['1. open', '2. high', '3. low', '4. close', '5. adjusted close', '6. volume']
            data = data[columns_to_keep]
            
            # Rename kolonner
            data.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            
            # Sorter etter dato (nyeste først)
            data = data.sort_index()
            
            return data
            
        except Exception as e:
            self.logger.error(f"Feil ved opprydding av historiske data: {str(e)}")
            return data
    
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