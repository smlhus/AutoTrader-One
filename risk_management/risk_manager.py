#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RiskManager for AutoTrader One.
"""

import logging
from typing import Dict, Optional
import pandas as pd
import numpy as np

class RiskManager:
    """Klasse for risikostyring i AutoTrader One."""
    
    def __init__(self, config: Dict):
        """
        Initialiserer RiskManager.
        
        Args:
            config (Dict): Konfigurasjon for risikostyring
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Hent konfigurasjon
        self.max_position_size = config.get('max_position_size', 0.10)
        self.max_daily_loss = config.get('max_daily_loss', 0.02)
        self.max_drawdown = config.get('max_drawdown', 0.10)
        self.leverage = config.get('leverage', 1.0)
    
    def assess_risk(self, symbol: str, market_data: pd.DataFrame, fundamental_data: Dict) -> Dict:
        """
        Vurderer risiko for et symbol.
        
        Args:
            symbol (str): Symbol som skal vurderes
            market_data (pd.DataFrame): Markedsdata
            fundamental_data (Dict): Fundamental data
            
        Returns:
            Dict: Risikovurdering
        """
        try:
            # Beregn volatilitet
            volatility = self._calculate_volatility(market_data)
            
            # Beregn beta
            beta = self._calculate_beta(market_data)
            
            # Beregn Sharpe ratio
            sharpe = self._calculate_sharpe_ratio(market_data)
            
            # Beregn maksimal drawdown
            max_drawdown = self._calculate_max_drawdown(market_data)
            
            # Beregn Value at Risk (VaR)
            var = self._calculate_var(market_data)
            
            # Beregn risikoscore
            risk_score = self._calculate_risk_score(
                volatility,
                beta,
                sharpe,
                max_drawdown,
                var,
                fundamental_data
            )
            
            # Beregn suksessannsynlighet
            success_probability = self._calculate_success_probability(
                risk_score,
                market_data,
                fundamental_data
            )
            
            # Beregn potensiell avkastning
            potential_return = self._calculate_potential_return(
                market_data,
                fundamental_data,
                risk_score
            )
            
            # Bestem maksimal posisjonsstørrelse
            position_size = self._calculate_position_size(risk_score)
            
            return {
                'symbol': symbol,
                'risk_score': round(risk_score, 1),
                'success_probability': round(success_probability * 100, 1),
                'potential_return': round(potential_return * 100, 1),
                'metrics': {
                    'volatility': round(volatility * 100, 2),
                    'beta': round(beta, 2),
                    'sharpe_ratio': round(sharpe, 2),
                    'max_drawdown': round(max_drawdown * 100, 2),
                    'var_95': round(var * 100, 2)
                },
                'position_sizing': {
                    'max_position_size': round(position_size * 100, 2),
                    'leverage': self.leverage
                }
            }
            
        except Exception as e:
            self.logger.error(f"Feil ved risikovurdering av {symbol}: {str(e)}")
            return self._get_default_assessment(symbol)
    
    def _calculate_volatility(self, market_data: pd.DataFrame) -> float:
        """
        Beregner volatilitet.
        
        Args:
            market_data (pd.DataFrame): Markedsdata
            
        Returns:
            float: Volatilitet
        """
        try:
            # Beregn daglig avkastning
            returns = market_data['Close'].pct_change().dropna()
            
            # Beregn årlig volatilitet
            annual_volatility = returns.std() * np.sqrt(252)
            
            return annual_volatility
            
        except Exception as e:
            self.logger.error(f"Feil ved volatilitetsberegning: {str(e)}")
            return 0.30  # Standard volatilitet
    
    def _calculate_beta(self, market_data: pd.DataFrame) -> float:
        """
        Beregner beta.
        
        Args:
            market_data (pd.DataFrame): Markedsdata
            
        Returns:
            float: Beta
        """
        try:
            # Beregn daglig avkastning
            returns = market_data['Close'].pct_change().dropna()
            
            # For nå, bruk en forenklet beta-beregning
            # I en produksjonsversjon bør vi sammenligne med markedsindeks
            beta = returns.mean() / returns.std()
            
            return max(min(beta, 2.0), 0.5)  # Begrens beta til 0.5-2.0
            
        except Exception as e:
            self.logger.error(f"Feil ved beta-beregning: {str(e)}")
            return 1.0  # Nøytral beta
    
    def _calculate_sharpe_ratio(self, market_data: pd.DataFrame) -> float:
        """
        Beregner Sharpe ratio.
        
        Args:
            market_data (pd.DataFrame): Markedsdata
            
        Returns:
            float: Sharpe ratio
        """
        try:
            # Beregn daglig avkastning
            returns = market_data['Close'].pct_change().dropna()
            
            # Beregn årlig avkastning og volatilitet
            annual_return = returns.mean() * 252
            annual_volatility = returns.std() * np.sqrt(252)
            
            # Bruk 2% som risikofri rente
            risk_free_rate = 0.02
            
            # Beregn Sharpe ratio
            sharpe = (annual_return - risk_free_rate) / annual_volatility
            
            return sharpe
            
        except Exception as e:
            self.logger.error(f"Feil ved Sharpe ratio-beregning: {str(e)}")
            return 0.0
    
    def _calculate_max_drawdown(self, market_data: pd.DataFrame) -> float:
        """
        Beregner maksimal drawdown.
        
        Args:
            market_data (pd.DataFrame): Markedsdata
            
        Returns:
            float: Maksimal drawdown
        """
        try:
            # Beregn kumulativ maksimum
            rolling_max = market_data['Close'].expanding().max()
            
            # Beregn drawdown
            drawdown = (market_data['Close'] - rolling_max) / rolling_max
            
            # Finn maksimal drawdown
            max_drawdown = abs(drawdown.min())
            
            return max_drawdown
            
        except Exception as e:
            self.logger.error(f"Feil ved drawdown-beregning: {str(e)}")
            return 0.20  # Standard drawdown
    
    def _calculate_var(self, market_data: pd.DataFrame) -> float:
        """
        Beregner Value at Risk (VaR).
        
        Args:
            market_data (pd.DataFrame): Markedsdata
            
        Returns:
            float: VaR (95% konfidensnivå)
        """
        try:
            # Beregn daglig avkastning
            returns = market_data['Close'].pct_change().dropna()
            
            # Beregn 95% VaR
            var_95 = np.percentile(returns, 5)
            
            return abs(var_95)
            
        except Exception as e:
            self.logger.error(f"Feil ved VaR-beregning: {str(e)}")
            return 0.02  # Standard VaR
    
    def _calculate_risk_score(self, volatility: float, beta: float, sharpe: float,
                            max_drawdown: float, var: float, fundamental_data: Dict) -> float:
        """
        Beregner samlet risikoscore.
        
        Args:
            volatility (float): Volatilitet
            beta (float): Beta
            sharpe (float): Sharpe ratio
            max_drawdown (float): Maksimal drawdown
            var (float): Value at Risk
            fundamental_data (Dict): Fundamental data
            
        Returns:
            float: Risikoscore fra 0 til 100
        """
        try:
            # Normaliser metrikkene
            vol_score = self._normalize_volatility(volatility)
            beta_score = self._normalize_beta(beta)
            sharpe_score = self._normalize_sharpe(sharpe)
            drawdown_score = self._normalize_drawdown(max_drawdown)
            var_score = self._normalize_var(var)
            
            # Legg til fundamental risiko
            fundamental_score = self._calculate_fundamental_risk(fundamental_data)
            
            # Vektlegging av ulike risikofaktorer
            weights = {
                'volatility': 0.25,
                'beta': 0.15,
                'sharpe': 0.20,
                'drawdown': 0.15,
                'var': 0.10,
                'fundamental': 0.15
            }
            
            # Beregn vektet gjennomsnitt
            risk_score = (
                vol_score * weights['volatility'] +
                beta_score * weights['beta'] +
                sharpe_score * weights['sharpe'] +
                drawdown_score * weights['drawdown'] +
                var_score * weights['var'] +
                fundamental_score * weights['fundamental']
            )
            
            return round(risk_score, 1)
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av risikoscore: {str(e)}")
            return 50.0
    
    def _normalize_volatility(self, volatility: float) -> float:
        """
        Normaliserer volatilitet til 0-100 skala.
        
        Args:
            volatility (float): Volatilitet
            
        Returns:
            float: Normalisert score
        """
        # Høyere volatilitet gir høyere risiko
        if volatility <= 0.15:
            return 20.0
        elif volatility <= 0.25:
            return 40.0
        elif volatility <= 0.35:
            return 60.0
        elif volatility <= 0.45:
            return 80.0
        else:
            return 100.0
    
    def _normalize_beta(self, beta: float) -> float:
        """
        Normaliserer beta til 0-100 skala.
        
        Args:
            beta (float): Beta
            
        Returns:
            float: Normalisert score
        """
        # Beta rundt 1.0 gir lavere risiko
        if beta < 0.5:
            return 70.0
        elif beta <= 0.8:
            return 40.0
        elif beta <= 1.2:
            return 30.0
        elif beta <= 1.5:
            return 60.0
        else:
            return 80.0
    
    def _normalize_sharpe(self, sharpe: float) -> float:
        """
        Normaliserer Sharpe ratio til 0-100 skala.
        
        Args:
            sharpe (float): Sharpe ratio
            
        Returns:
            float: Normalisert score
        """
        # Høyere Sharpe ratio gir lavere risiko
        if sharpe <= 0:
            return 80.0
        elif sharpe <= 0.5:
            return 60.0
        elif sharpe <= 1.0:
            return 40.0
        elif sharpe <= 1.5:
            return 30.0
        else:
            return 20.0
    
    def _normalize_drawdown(self, drawdown: float) -> float:
        """
        Normaliserer drawdown til 0-100 skala.
        
        Args:
            drawdown (float): Drawdown
            
        Returns:
            float: Normalisert score
        """
        # Høyere drawdown gir høyere risiko
        if drawdown <= 0.10:
            return 20.0
        elif drawdown <= 0.20:
            return 40.0
        elif drawdown <= 0.30:
            return 60.0
        elif drawdown <= 0.40:
            return 80.0
        else:
            return 100.0
    
    def _normalize_var(self, var: float) -> float:
        """
        Normaliserer VaR til 0-100 skala.
        
        Args:
            var (float): Value at Risk
            
        Returns:
            float: Normalisert score
        """
        # Høyere VaR gir høyere risiko
        if var <= 0.01:
            return 20.0
        elif var <= 0.02:
            return 40.0
        elif var <= 0.03:
            return 60.0
        elif var <= 0.04:
            return 80.0
        else:
            return 100.0
    
    def _calculate_fundamental_risk(self, fundamental_data: Dict) -> float:
        """
        Beregner fundamental risiko.
        
        Args:
            fundamental_data (Dict): Fundamental data
            
        Returns:
            float: Risikoscore fra 0 til 100
        """
        try:
            # Hent nøkkeltall med standardverdier
            debt_equity = fundamental_data.get('debt_to_equity') or 1.0
            current_ratio = fundamental_data.get('current_ratio') or 1.5
            profit_margin = fundamental_data.get('profit_margin') or 0.1
            
            # Beregn delscorer
            debt_score = 100 if debt_equity > 2.0 else (debt_equity / 2.0) * 100
            liquidity_score = 100 if current_ratio < 1.0 else (1.0 / current_ratio) * 100
            profit_score = 100 if profit_margin < 0 else (1.0 - profit_margin) * 100
            
            # Beregn gjennomsnitt
            return (debt_score + liquidity_score + profit_score) / 3
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av fundamental risiko: {str(e)}")
            return 50.0
    
    def _calculate_success_probability(self, risk_score: float, market_data: pd.DataFrame,
                                    fundamental_data: Dict) -> float:
        """
        Beregner sannsynlighet for suksess.
        
        Args:
            risk_score (float): Risikoscore
            market_data (pd.DataFrame): Markedsdata
            fundamental_data (Dict): Fundamental data
            
        Returns:
            float: Sannsynlighet (0-1)
        """
        try:
            # Beregn trend-styrke
            trend = self._calculate_trend_strength(market_data)
            
            # Beregn fundamental styrke
            fundamental_strength = self._calculate_fundamental_strength(fundamental_data)
            
            # Kombiner faktorer
            base_probability = (100 - risk_score) / 100
            trend_adjustment = trend * 0.3
            fundamental_adjustment = fundamental_strength * 0.2
            
            # Beregn total sannsynlighet
            probability = base_probability + trend_adjustment + fundamental_adjustment
            
            # Begrens til 0-1
            return max(min(probability, 1.0), 0.0)
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av suksessannsynlighet: {str(e)}")
            return 0.5
    
    def _calculate_trend_strength(self, market_data: pd.DataFrame) -> float:
        """
        Beregner trend-styrke.
        
        Args:
            market_data (pd.DataFrame): Markedsdata
            
        Returns:
            float: Trend-styrke (-1 til 1)
        """
        try:
            # Beregn korte og lange glidende gjennomsnitt
            sma_20 = market_data['Close'].rolling(window=20).mean()
            sma_50 = market_data['Close'].rolling(window=50).mean()
            
            # Beregn trend-styrke
            current_price = market_data['Close'].iloc[-1]
            trend_strength = (
                (current_price - sma_50.iloc[-1]) / sma_50.iloc[-1] +
                (sma_20.iloc[-1] - sma_50.iloc[-1]) / sma_50.iloc[-1]
            ) / 2
            
            # Begrens til -1 til 1
            return max(min(trend_strength, 1.0), -1.0)
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av trend-styrke: {str(e)}")
            return 0.0
    
    def _calculate_fundamental_strength(self, fundamental_data: Dict) -> float:
        """
        Beregner fundamental styrke.
        
        Args:
            fundamental_data (Dict): Fundamental data
            
        Returns:
            float: Fundamental styrke (0-1)
        """
        try:
            # Hent nøkkeltall
            pe_ratio = fundamental_data.get('trailing_pe', 15)
            pb_ratio = fundamental_data.get('price_to_book', 2)
            profit_margin = fundamental_data.get('profit_margin', 0.1)
            roe = fundamental_data.get('return_on_equity', 0.15)
            
            # Beregn delscorer
            pe_score = 1.0 if pe_ratio < 15 else (20 / pe_ratio)
            pb_score = 1.0 if pb_ratio < 2 else (3 / pb_ratio)
            margin_score = min(profit_margin * 5, 1.0)
            roe_score = min(roe * 3, 1.0)
            
            # Beregn gjennomsnitt
            return (pe_score + pb_score + margin_score + roe_score) / 4
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av fundamental styrke: {str(e)}")
            return 0.5
    
    def _calculate_potential_return(self, market_data: pd.DataFrame, fundamental_data: Dict,
                                  risk_score: float) -> float:
        """
        Beregner potensiell avkastning.
        
        Args:
            market_data (pd.DataFrame): Markedsdata
            fundamental_data (Dict): Fundamental data
            risk_score (float): Risikoscore
            
        Returns:
            float: Potensiell avkastning (0-1)
        """
        try:
            # Beregn teknisk potensial
            technical_potential = self._calculate_technical_potential(market_data)
            
            # Beregn fundamental potensial
            fundamental_potential = self._calculate_fundamental_potential(fundamental_data)
            
            # Juster for risiko
            risk_adjustment = 1 - (risk_score / 200)  # Mindre justering for høy risiko
            
            # Kombiner potensial
            total_potential = (
                technical_potential * 0.5 +
                fundamental_potential * 0.5
            ) * risk_adjustment
            
            # Begrens til 0-1
            return max(min(total_potential, 1.0), 0.0)
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av potensiell avkastning: {str(e)}")
            return 0.1
    
    def _calculate_technical_potential(self, market_data: pd.DataFrame) -> float:
        """
        Beregner teknisk potensial.
        
        Args:
            market_data (pd.DataFrame): Markedsdata
            
        Returns:
            float: Teknisk potensial (0-1)
        """
        try:
            # Beregn momentum
            returns = market_data['Close'].pct_change()
            momentum = returns.mean() * 252
            
            # Beregn trendstyrke
            trend = self._calculate_trend_strength(market_data)
            
            # Beregn volatilitetsjustert potensial
            volatility = returns.std() * np.sqrt(252)
            vol_adjusted_potential = momentum / volatility
            
            # Kombiner faktorer
            technical_potential = (
                abs(momentum) * 0.4 +
                abs(trend) * 0.4 +
                abs(vol_adjusted_potential) * 0.2
            )
            
            # Begrens til 0-1
            return max(min(technical_potential, 1.0), 0.0)
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av teknisk potensial: {str(e)}")
            return 0.1
    
    def _calculate_fundamental_potential(self, fundamental_data: Dict) -> float:
        """
        Beregner fundamental potensial.
        
        Args:
            fundamental_data (Dict): Fundamental data
            
        Returns:
            float: Fundamental potensial (0-1)
        """
        try:
            # Hent nøkkeltall
            pe_ratio = fundamental_data.get('trailing_pe', 15)
            pb_ratio = fundamental_data.get('price_to_book', 2)
            profit_margin = fundamental_data.get('profit_margin', 0.1)
            roe = fundamental_data.get('return_on_equity', 0.15)
            
            # Beregn delpotensialer
            pe_potential = 1.0 if pe_ratio < 12 else (15 / pe_ratio)
            pb_potential = 1.0 if pb_ratio < 1.5 else (2 / pb_ratio)
            margin_potential = min(profit_margin * 4, 1.0)
            roe_potential = min(roe * 2.5, 1.0)
            
            # Beregn gjennomsnitt
            return (pe_potential + pb_potential + margin_potential + roe_potential) / 4
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av fundamental potensial: {str(e)}")
            return 0.1
    
    def _calculate_position_size(self, risk_score: float) -> float:
        """
        Beregner anbefalt posisjonsstørrelse.
        
        Args:
            risk_score (float): Risikoscore
            
        Returns:
            float: Posisjonsstørrelse (0-1)
        """
        try:
            # Juster maksimal posisjonsstørrelse basert på risiko
            risk_factor = 1 - (risk_score / 100)
            position_size = self.max_position_size * risk_factor
            
            # Begrens til konfigurert maksimum
            return min(position_size, self.max_position_size)
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av posisjonsstørrelse: {str(e)}")
            return self.max_position_size / 2
    
    def _get_default_assessment(self, symbol: str) -> Dict:
        """
        Returnerer standard risikovurdering.
        
        Args:
            symbol (str): Symbol
            
        Returns:
            Dict: Standard risikovurdering
        """
        return {
            'symbol': symbol,
            'risk_score': 50.0,
            'success_probability': 50.0,
            'potential_return': 10.0,
            'metrics': {
                'volatility': 30.0,
                'beta': 1.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 20.0,
                'var_95': 2.0
            },
            'position_sizing': {
                'max_position_size': 5.0,
                'leverage': self.leverage
            }
        } 