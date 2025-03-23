#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markedsdata-provider for AutoTrader One.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import random
import yfinance as yf
import pandas as pd
import asyncio
from typing import Dict, Optional, List

class MarketDataProvider(ABC):
    """Abstrakt baseklasse for markedsdata-providers."""
    
    @abstractmethod
    async def get_historical_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        """
        Henter historiske data for et symbol.
        
        Args:
            symbol (str): Aksjesymbol
            period (str): Periode (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            pd.DataFrame: Historiske data
        """
        pass

class YahooFinanceProvider(MarketDataProvider):
    """Klasse for å hente markedsdata fra Yahoo Finance."""
    
    def __init__(self, config: Dict):
        """
        Initialiserer YahooFinanceProvider.
        
        Args:
            config (Dict): Konfigurasjon for dataprovideren
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Sett standardverdier
        self.period = config.get('period', '1y')
        self.interval = config.get('interval', '1d')
    
    async def get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Henter historiske data for et symbol.
        
        Args:
            symbol (str): Symbol å hente data for
            
        Returns:
            Optional[pd.DataFrame]: Historiske data eller None ved feil
        """
        try:
            self.logger.info(f"Henter historiske data for {symbol}")
            
            # Hent data fra Yahoo Finance
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=self.period, interval=self.interval)
            
            if df.empty:
                self.logger.warning(f"Ingen data funnet for {symbol}")
                return None
            
            # Sjekk om vi har justerte sluttkurser
            if 'Adj Close' not in df.columns:
                self.logger.warning(f"Mangler justerte sluttkurser for {symbol}, bruker vanlige sluttkurser")
                df['Adj Close'] = df['Close']
            
            # Fyll manglende verdier
            df = df.ffill()
            
            return df
            
        except Exception as e:
            self.logger.error(f"Feil ved henting av historiske data for {symbol}: {str(e)}")
            return None
    
    async def get_fundamentals(self, symbol: str) -> Optional[Dict]:
        """
        Henter fundamental data for et symbol.
        
        Args:
            symbol (str): Symbol å hente data for
            
        Returns:
            Optional[Dict]: Fundamental data eller None ved feil
        """
        try:
            self.logger.info(f"Henter fundamental data for {symbol}")
            
            # Hent data fra Yahoo Finance
            ticker = yf.Ticker(symbol)
            
            # Hent nøkkeltall
            info = ticker.info
            
            # Hent siste pris
            df = ticker.history(period='1d')
            current_price = df['Close'].iloc[-1] if not df.empty else None
            
            # Samle fundamental data
            fundamentals = {
                'price': current_price,
                'market_cap': info.get('marketCap'),
                'earnings_per_share': info.get('trailingEps'),
                'book_value_per_share': info.get('bookValue'),
                'total_debt': info.get('totalDebt'),
                'total_equity': info.get('totalStockholderEquity'),
                'current_assets': info.get('totalCurrentAssets'),
                'current_liabilities': info.get('totalCurrentLiabilities'),
                'net_income': info.get('netIncomeToCommon'),
                'revenue': info.get('totalRevenue'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'return_on_equity': info.get('returnOnEquity'),
                'return_on_assets': info.get('returnOnAssets'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                'beta': info.get('beta'),
                'enterprise_value': info.get('enterpriseValue'),
                'enterprise_to_revenue': info.get('enterpriseToRevenue'),
                'enterprise_to_ebitda': info.get('enterpriseToEbitda'),
                'forward_pe': info.get('forwardPE'),
                'trailing_pe': info.get('trailingPE'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months')
            }
            
            return fundamentals
            
        except Exception as e:
            self.logger.error(f"Feil ved henting av fundamental data for {symbol}: {str(e)}")
            return None
    
    async def get_available_tickers(self, exchange: str = "OSL") -> list:
        """
        Henter tilgjengelige symboler fra en børs.
        
        Args:
            exchange (str): Børssymbol
            
        Returns:
            list: Liste over tilgjengelige symboler
        """
        # TODO: Implementer funksjonalitet for å hente tilgjengelige symboler
        self.logger.warning("Henting av tilgjengelige symboler er ikke implementert ennå")
        return []

class AlphaVantageProvider(MarketDataProvider):
    """Provider for Alpha Vantage markedsdata."""
    
    def __init__(self):
        """Initialiserer Alpha Vantage provider."""
        self.logger = logging.getLogger(__name__)
    
    async def get_historical_data(self, symbol, start_date, end_date):
        """
        Henter historiske data fra Alpha Vantage.
        
        Args:
            symbol (str): Aksjesymbol
            start_date (datetime): Startdato
            end_date (datetime): Sluttdato
            
        Returns:
            dict: Historiske data
        """
        self.logger.info("Alpha Vantage støtte ikke implementert ennå")
        return {}

def get_market_data_provider(provider_name: str = 'yahoo') -> MarketDataProvider:
    """
    Factory-funksjon for å opprette market data providers.
    
    Args:
        provider_name (str): Navn på provideren
        
    Returns:
        MarketDataProvider: Provider-instans
    """
    if provider_name.lower() == 'yahoo':
        return YahooFinanceProvider()
    else:
        raise ValueError(f"Ukjent market data provider: {provider_name}")

