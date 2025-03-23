#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Financial Modeling Prep dataprovider for AutoTrader One.
"""

import logging
from typing import Dict, Optional
import pandas as pd
import requests
from datetime import datetime, timedelta

class FMPProvider:
    """Klasse for å hente data fra Financial Modeling Prep."""
    
    def __init__(self, config: Dict):
        """
        Initialiserer FMPProvider.
        
        Args:
            config (Dict): Konfigurasjon for dataprovideren
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Hent API-nøkkel fra konfigurasjon
        self.api_key = config.get('api_key')
        if not self.api_key:
            raise ValueError("FMP API-nøkkel mangler i konfigurasjonen")
        
        # Sett opp base URL
        self.base_url = "https://financialmodelingprep.com/api/v3"
        
        # Sett opp cache
        self.cache = {}
        self.cache_timeout = config.get('cache_timeout', 3600)  # 1 time som standard
    
    async def get_fundamental_data(self, symbol: str) -> Optional[Dict]:
        """
        Henter fundamental data for et symbol.
        
        Args:
            symbol (str): Symbol å hente data for
            
        Returns:
            Optional[Dict]: Fundamental data eller None ved feil
        """
        try:
            # Sjekk cache
            cache_key = f"fundamental_{symbol}"
            if self._is_cache_valid(cache_key):
                self.logger.debug(f"Bruker cachet fundamental data for {symbol}")
                return self.cache[cache_key]['data']
            
            # Hent data fra FMP
            self.logger.info(f"Henter fundamental data for {symbol}")
            
            # Hent profil
            profile = self._make_request(f"/profile/{symbol}")
            if not profile:
                return None
            
            # Hent inntektsdata
            income = self._make_request(f"/income-statement/{symbol}", limit=5)
            
            # Hent balanse
            balance = self._make_request(f"/balance-sheet-statement/{symbol}", limit=5)
            
            # Hent kontantstrøm
            cash_flow = self._make_request(f"/cash-flow-statement/{symbol}", limit=5)
            
            # Hent nøkkeltall
            ratios = self._make_request(f"/ratios/{symbol}", limit=5)
            
            # Samle data
            fundamental_data = {
                'profile': profile[0] if profile else {},
                'income': income if income else [],
                'balance': balance if balance else [],
                'cash_flow': cash_flow if cash_flow else [],
                'ratios': ratios if ratios else []
            }
            
            # Cache data
            self._cache_data(cache_key, fundamental_data)
            
            return fundamental_data
            
        except Exception as e:
            self.logger.error(f"Feil ved henting av fundamental data for {symbol}: {str(e)}")
            return None
    
    async def get_historical_fundamentals(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Henter historiske fundamentale data for et symbol.
        
        Args:
            symbol (str): Symbol å hente data for
            
        Returns:
            Optional[pd.DataFrame]: Historiske fundamentale data eller None ved feil
        """
        try:
            # Sjekk cache
            cache_key = f"historical_fundamental_{symbol}"
            if self._is_cache_valid(cache_key):
                self.logger.debug(f"Bruker cachet historiske fundamentale data for {symbol}")
                return self.cache[cache_key]['data']
            
            # Hent data fra FMP
            self.logger.info(f"Henter historiske fundamentale data for {symbol}")
            
            # Hent 5 års historiske data
            data = self._make_request(f"/income-statement/{symbol}", limit=5)
            
            if not data:
                return None
            
            # Konverter til DataFrame
            df = pd.DataFrame(data)
            
            # Rydd opp data
            df = self._clean_historical_fundamentals(df)
            
            # Cache data
            self._cache_data(cache_key, df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Feil ved henting av historiske fundamentale data for {symbol}: {str(e)}")
            return None
    
    def _make_request(self, endpoint: str, **params) -> Optional[list]:
        """
        Utfører API-forespørsel.
        
        Args:
            endpoint (str): API-endepunkt
            **params: Ekstra parametre
            
        Returns:
            Optional[list]: API-respons eller None ved feil
        """
        try:
            # Legg til API-nøkkel
            params['apikey'] = self.api_key
            
            # Utfør forespørsel
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params)
            
            # Sjekk status
            if response.status_code != 200:
                self.logger.error(f"API-feil: {response.status_code} - {response.text}")
                return None
            
            # Parse JSON
            data = response.json()
            
            # Sjekk for feilmeldinger
            if isinstance(data, dict) and 'Error Message' in data:
                self.logger.error(f"API-feilmelding: {data['Error Message']}")
                return None
            
            return data
            
        except Exception as e:
            self.logger.error(f"Feil ved API-forespørsel: {str(e)}")
            return None
    
    def _clean_historical_fundamentals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rydder opp historiske fundamentale data.
        
        Args:
            df (pd.DataFrame): Rå data fra FMP
            
        Returns:
            pd.DataFrame: Ryddet data
        """
        try:
            # Konverter datoer
            df['date'] = pd.to_datetime(df['date'])
            
            # Sett dato som indeks
            df.set_index('date', inplace=True)
            
            # Sorter etter dato (nyeste først)
            df.sort_index(ascending=False, inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Feil ved opprydding av historiske fundamentale data: {str(e)}")
            return df
    
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