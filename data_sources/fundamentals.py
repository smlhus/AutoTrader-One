#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fundamentaldata-provider for AutoTrader One.
"""

import logging
import yfinance as yf
from typing import Dict, Optional
import asyncio

class FundamentalsProvider:
    """Abstrakt baseklasse for fundamentaldata-providers."""
    
    async def get_fundamentals(self, symbol: str) -> Dict:
        """
        Henter fundamentale data for et symbol.
        
        Args:
            symbol (str): Aksjesymbol
            
        Returns:
            dict: Fundamentale data
        """
        raise NotImplementedError("Subklasser må implementere get_fundamentals")

class YahooFinanceFundamentalsProvider(FundamentalsProvider):
    """Provider for fundamentale data fra Yahoo Finance."""
    
    def __init__(self):
        """Initialiserer YahooFinanceFundamentalsProvider."""
        self.logger = logging.getLogger(__name__)
    
    async def get_fundamentals(self, symbol: str) -> Dict:
        """
        Henter fundamentale data fra Yahoo Finance.
        
        Args:
            symbol (str): Aksjesymbol
            
        Returns:
            dict: Fundamentale data
        """
        self.logger.info(f"Henter fundamentale data for {symbol} fra Yahoo Finance")
        
        try:
            # Bruk asyncio for å kjøre yfinance-kall i en separat tråd
            info = await asyncio.to_thread(self._get_info, symbol)
            
            # Beregn nøkkeltall
            metrics = {}
            
            # P/E-ratio
            if info.get('trailingPE') is not None:
                metrics['pe_ratio'] = {
                    'value': info['trailingPE'],
                    'description': 'Pris/Fortjeneste-forhold',
                    'signal': 'buy' if info['trailingPE'] < 15 else ('sell' if info['trailingPE'] > 30 else 'neutral')
                }
            
            # EPS (Earnings Per Share)
            if info.get('trailingEps') is not None:
                metrics['eps'] = {
                    'value': info['trailingEps'],
                    'description': 'Fortjeneste per aksje',
                    'signal': 'buy' if info['trailingEps'] > 0 else 'sell'
                }
            
            # Inntektsvekst
            if info.get('revenueGrowth') is not None:
                metrics['revenue_growth'] = {
                    'value': info['revenueGrowth'] * 100,  # Konverter til prosent
                    'description': 'Inntektsvekst (%)',
                    'signal': 'buy' if info['revenueGrowth'] > 0.1 else ('sell' if info['revenueGrowth'] < 0 else 'neutral')
                }
            
            # Profittmargin
            if info.get('profitMargins') is not None:
                metrics['profit_margin'] = {
                    'value': info['profitMargins'] * 100,  # Konverter til prosent
                    'description': 'Profittmargin (%)',
                    'signal': 'buy' if info['profitMargins'] > 0.15 else ('sell' if info['profitMargins'] < 0.05 else 'neutral')
                }
            
            # Gjeld/Egenkapital-forhold
            if info.get('debtToEquity') is not None:
                metrics['debt_to_equity'] = {
                    'value': info['debtToEquity'] / 100,  # Konverter til desimal
                    'description': 'Gjeld/Egenkapital-forhold',
                    'signal': 'buy' if info['debtToEquity'] < 100 else ('sell' if info['debtToEquity'] > 200 else 'neutral')
                }
            
            # Beregn samlet fundamental score (0-100)
            buy_signals = sum(1 for m in metrics.values() if m['signal'] == 'buy')
            sell_signals = sum(1 for m in metrics.values() if m['signal'] == 'sell')
            total_metrics = len(metrics)
            
            if total_metrics > 0:
                score = 50 + ((buy_signals - sell_signals) / total_metrics) * 50
            else:
                score = 50
            
            return {
                'symbol': symbol,
                'metrics': metrics,
                'score': round(score, 1),
                'recommendation': 'buy' if score > 60 else ('sell' if score < 40 else 'hold')
            }
            
        except Exception as e:
            self.logger.error(f"Feil ved henting av fundamentale data for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'error': str(e),
                'metrics': {},
                'score': 50,
                'recommendation': 'hold'
            }
    
    def _get_info(self, symbol: str) -> Dict:
        """
        Henter info fra Yahoo Finance.
        
        Args:
            symbol (str): Aksjesymbol
            
        Returns:
            dict: Info fra Yahoo Finance
        """
        ticker = yf.Ticker(symbol)
        return ticker.info

def get_fundamentals_provider(provider_name: str = 'yahoo') -> FundamentalsProvider:
    """
    Factory-funksjon for å opprette fundamentals providers.
    
    Args:
        provider_name (str): Navn på provideren
        
    Returns:
        FundamentalsProvider: Provider-instans
    """
    if provider_name.lower() == 'yahoo':
        return YahooFinanceFundamentalsProvider()
    else:
        raise ValueError(f"Ukjent fundamentals provider: {provider_name}")

