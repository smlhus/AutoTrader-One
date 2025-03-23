#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teknisk analyse for AutoTrader One.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict

class TechnicalAnalyzer:
    """Klasse for teknisk analyse i AutoTrader One."""
    
    def __init__(self, config: Dict):
        """
        Initialiserer TechnicalAnalyzer.
        
        Args:
            config (Dict): Konfigurasjon for teknisk analyse
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Hent konfigurasjon
        self.rsi_period = config.get('rsi_period', 14)
        self.sma_short = config.get('sma_short', 20)
        self.sma_long = config.get('sma_long', 50)
        self.macd_fast = config.get('macd_fast', 12)
        self.macd_slow = config.get('macd_slow', 26)
        self.macd_signal = config.get('macd_signal', 9)
    
    def analyze(self, market_data: Dict) -> Dict:
        """
        Utfører teknisk analyse på markedsdata.
        
        Args:
            market_data (Dict): Markedsdata
            
        Returns:
            Dict: Analyseresultater
        """
        try:
            # Konverter til DataFrame
            df = pd.DataFrame(market_data)
            
            # Beregn tekniske indikatorer
            rsi = self._calculate_rsi(df)
            sma_signals = self._calculate_sma_signals(df)
            macd_signals = self._calculate_macd_signals(df)
            volume_signals = self._calculate_volume_signals(df)
            
            # Beregn samlet teknisk score
            technical_score = self._calculate_technical_score(rsi, sma_signals, macd_signals, volume_signals)
            
            # Bestem anbefaling basert på score
            if technical_score >= 70:
                recommendation = 'buy'
            elif technical_score <= 30:
                recommendation = 'sell'
            else:
                recommendation = 'hold'
            
            return {
                'score': technical_score,
                'recommendation': recommendation,
                'rsi': round(rsi, 1),
                'rsi_signal': self._get_rsi_signal(rsi),
                'sma_short': round(sma_signals['short'], 2),
                'sma_long': round(sma_signals['long'], 2),
                'sma_signal': sma_signals['signal'],
                'macd_signal': macd_signals['signal'],
                'volume_signal': volume_signals['signal'],
                'risk_score': self._calculate_risk_score(df)
            }
            
        except Exception as e:
            self.logger.error(f"Feil ved teknisk analyse: {str(e)}")
            return {
                'score': 50,
                'recommendation': 'hold',
                'error': str(e)
            }
    
    def _calculate_rsi(self, df: pd.DataFrame) -> float:
        """
        Beregner Relative Strength Index (RSI).
        
        Args:
            df (pd.DataFrame): Prisdata
            
        Returns:
            float: RSI-verdi
        """
        try:
            # Beregn prisendringer
            delta = df['Close'].diff()
            
            # Separer positive og negative endringer
            gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
            
            # Beregn RS og RSI
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi.iloc[-1])
            
        except Exception as e:
            self.logger.error(f"Feil ved RSI-beregning: {str(e)}")
            return 50.0
    
    def _calculate_sma_signals(self, df: pd.DataFrame) -> Dict:
        """
        Beregner Simple Moving Average (SMA) signaler.
        
        Args:
            df (pd.DataFrame): Prisdata
            
        Returns:
            Dict: SMA-signaler
        """
        try:
            # Beregn korte og lange glidende gjennomsnitt
            sma_short = df['Close'].rolling(window=self.sma_short).mean()
            sma_long = df['Close'].rolling(window=self.sma_long).mean()
            
            # Bestem signal basert på kryssinger
            if sma_short.iloc[-1] > sma_long.iloc[-1] and sma_short.iloc[-2] <= sma_long.iloc[-2]:
                signal = 'buy'
            elif sma_short.iloc[-1] < sma_long.iloc[-1] and sma_short.iloc[-2] >= sma_long.iloc[-2]:
                signal = 'sell'
            else:
                signal = 'neutral'
            
            return {
                'short': float(sma_short.iloc[-1]),
                'long': float(sma_long.iloc[-1]),
                'signal': signal
            }
            
        except Exception as e:
            self.logger.error(f"Feil ved SMA-beregning: {str(e)}")
            return {
                'short': df['Close'].iloc[-1],
                'long': df['Close'].iloc[-1],
                'signal': 'neutral'
            }
    
    def _calculate_macd_signals(self, df: pd.DataFrame) -> Dict:
        """
        Beregner Moving Average Convergence Divergence (MACD) signaler.
        
        Args:
            df (pd.DataFrame): Prisdata
            
        Returns:
            Dict: MACD-signaler
        """
        try:
            # Beregn EMA-er
            ema_fast = df['Close'].ewm(span=self.macd_fast).mean()
            ema_slow = df['Close'].ewm(span=self.macd_slow).mean()
            
            # Beregn MACD og signal-linje
            macd = ema_fast - ema_slow
            signal_line = macd.ewm(span=self.macd_signal).mean()
            
            # Bestem signal basert på kryssinger
            if macd.iloc[-1] > signal_line.iloc[-1] and macd.iloc[-2] <= signal_line.iloc[-2]:
                signal = 'buy'
            elif macd.iloc[-1] < signal_line.iloc[-1] and macd.iloc[-2] >= signal_line.iloc[-2]:
                signal = 'sell'
            else:
                signal = 'neutral'
            
            return {
                'macd': float(macd.iloc[-1]),
                'signal_line': float(signal_line.iloc[-1]),
                'signal': signal
            }
            
        except Exception as e:
            self.logger.error(f"Feil ved MACD-beregning: {str(e)}")
            return {
                'macd': 0.0,
                'signal_line': 0.0,
                'signal': 'neutral'
            }
    
    def _calculate_volume_signals(self, df: pd.DataFrame) -> Dict:
        """
        Beregner volumsignaler.
        
        Args:
            df (pd.DataFrame): Prisdata
            
        Returns:
            Dict: Volumsignaler
        """
        try:
            # Beregn gjennomsnittlig volum
            avg_volume = df['Volume'].rolling(window=20).mean()
            current_volume = df['Volume'].iloc[-1]
            
            # Beregn volum-ratio
            volume_ratio = current_volume / avg_volume.iloc[-1]
            
            # Bestem signal basert på volum
            if volume_ratio > 2.0:
                signal = 'buy'
            elif volume_ratio < 0.5:
                signal = 'sell'
            else:
                signal = 'neutral'
            
            return {
                'ratio': float(volume_ratio),
                'signal': signal
            }
            
        except Exception as e:
            self.logger.error(f"Feil ved volum-beregning: {str(e)}")
            return {
                'ratio': 1.0,
                'signal': 'neutral'
            }
    
    def _calculate_technical_score(self, rsi: float, sma: Dict, macd: Dict, volume: Dict) -> float:
        """
        Beregner samlet teknisk score.
        
        Args:
            rsi (float): RSI-verdi
            sma (Dict): SMA-signaler
            macd (Dict): MACD-signaler
            volume (Dict): Volumsignaler
            
        Returns:
            float: Teknisk score fra 0 til 100
        """
        try:
            # Vektlegg ulike signaler
            rsi_score = self._get_rsi_score(rsi)
            sma_score = self._get_signal_score(sma['signal'])
            macd_score = self._get_signal_score(macd['signal'])
            volume_score = self._get_signal_score(volume['signal'])
            
            # Beregn vektet gjennomsnitt
            total_score = (
                rsi_score * 0.3 +
                sma_score * 0.3 +
                macd_score * 0.3 +
                volume_score * 0.1
            )
            
            return round(total_score, 1)
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av teknisk score: {str(e)}")
            return 50.0
    
    def _get_rsi_score(self, rsi: float) -> float:
        """
        Konverterer RSI til score.
        
        Args:
            rsi (float): RSI-verdi
            
        Returns:
            float: Score fra 0 til 100
        """
        if rsi >= 70:
            return 20.0  # Overkjøpt
        elif rsi <= 30:
            return 80.0  # Oversolgt
        else:
            return 50.0  # Nøytral
    
    def _get_signal_score(self, signal: str) -> float:
        """
        Konverterer signal til score.
        
        Args:
            signal (str): Signal (buy, sell, neutral)
            
        Returns:
            float: Score fra 0 til 100
        """
        if signal == 'buy':
            return 80.0
        elif signal == 'sell':
            return 20.0
        else:
            return 50.0
    
    def _get_rsi_signal(self, rsi: float) -> str:
        """
        Konverterer RSI til signal.
        
        Args:
            rsi (float): RSI-verdi
            
        Returns:
            str: Signal (buy, sell, neutral)
        """
        if rsi >= 70:
            return 'sell'
        elif rsi <= 30:
            return 'buy'
        else:
            return 'neutral'
    
    def _calculate_risk_score(self, df: pd.DataFrame) -> float:
        """
        Beregner risikoscore basert på volatilitet og trender.
        
        Args:
            df (pd.DataFrame): Prisdata
            
        Returns:
            float: Risikoscore fra 0 til 100
        """
        try:
            # Beregn volatilitet
            returns = df['Close'].pct_change()
            volatility = returns.std() * np.sqrt(252)  # Årlig volatilitet
            
            # Beregn trend-styrke
            trend = abs(df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]
            
            # Kombiner volatilitet og trend
            risk_score = (volatility * 100) + (trend * 50)
            
            return min(max(round(risk_score, 1), 0), 100)
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av risikoscore: {str(e)}")
            return 50.0

