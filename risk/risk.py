#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Risikostyring for AutoTrader One.
"""

import logging
from typing import Dict, Tuple
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
        
        # Standardverdier hvis ikke spesifisert i konfigurasjonen
        self.max_position_size = config.get('max_position_size', 0.1)  # 10% av porteføljen
        self.max_daily_loss = config.get('max_daily_loss', 0.02)  # 2% per dag
        self.max_drawdown = config.get('max_drawdown', 0.1)  # 10% maksimal drawdown
        self.max_leverage = config.get('max_leverage', 1.0)  # Ingen gearing som standard
    
    def calculate_position_size(self, portfolio_value: float, price: float) -> int:
        """
        Beregner maksimal posisjonsstørrelse basert på risikoparametre.
        
        Args:
            portfolio_value (float): Total porteføljeverdi
            price (float): Aksjekurs
            
        Returns:
            int: Antall aksjer som kan kjøpes
        """
        max_position_value = portfolio_value * self.max_position_size
        return int(max_position_value / price)
    
    def calculate_daily_loss(self, portfolio_value: float, positions: Dict) -> float:
        """
        Beregner dagens tap basert på åpne posisjoner.
        
        Args:
            portfolio_value (float): Total porteføljeverdi
            positions (Dict): Åpne posisjoner
            
        Returns:
            float: Dagens tap i prosent
        """
        total_loss = 0.0
        for symbol, position in positions.items():
            if position['type'] == 'long':
                loss = (position['entry_price'] - position['current_price']) / position['entry_price']
            else:
                loss = (position['current_price'] - position['entry_price']) / position['entry_price']
            total_loss += loss * position['size']
        
        return total_loss / portfolio_value
    
    def calculate_drawdown(self, portfolio_history: list) -> float:
        """
        Beregner maksimal drawdown fra porteføljehistorikk.
        
        Args:
            portfolio_history (list): Liste over porteføljeverdier over tid
            
        Returns:
            float: Maksimal drawdown i prosent
        """
        if not portfolio_history:
            return 0.0
        
        portfolio_values = np.array(portfolio_history)
        peak = np.maximum.accumulate(portfolio_values)
        drawdown = (peak - portfolio_values) / peak
        return float(np.max(drawdown))
    
    def validate_trade(self, recommendation: Dict, portfolio: Dict) -> Tuple[bool, str]:
        """
        Validerer en handelsanbefaling mot risikoparametre.
        
        Args:
            recommendation (Dict): Handelsanbefaling
            portfolio (Dict): Porteføljeinformasjon
            
        Returns:
            Tuple[bool, str]: (Er handelen gyldig, Melding)
        """
        try:
            # Sjekk posisjonsstørrelse
            position_size = self.calculate_position_size(
                portfolio['total_value'],
                recommendation['current_price']
            )
            if position_size < recommendation['size']:
                return False, f"Posisjonsstørrelse {recommendation['size']} overskrider maksgrensen på {position_size}"
            
            # Sjekk daglig tap
            daily_loss = self.calculate_daily_loss(
                portfolio['total_value'],
                portfolio['positions']
            )
            if daily_loss > self.max_daily_loss:
                return False, f"Dagens tap {daily_loss:.2%} overskrider maksgrensen på {self.max_daily_loss:.2%}"
            
            # Sjekk drawdown
            drawdown = self.calculate_drawdown(portfolio['history'])
            if drawdown > self.max_drawdown:
                return False, f"Drawdown {drawdown:.2%} overskrider maksgrensen på {self.max_drawdown:.2%}"
            
            # Sjekk gearing
            if recommendation.get('leverage', 1.0) > self.max_leverage:
                return False, f"Gearing {recommendation['leverage']} overskrider maksgrensen på {self.max_leverage}"
            
            return True, "Handelen er gyldig"
            
        except Exception as e:
            self.logger.error(f"Feil ved validering av handel: {str(e)}")
            return False, f"Feil ved validering: {str(e)}"
    
    def calculate_risk_score(self, recommendation: Dict, portfolio: Dict) -> float:
        """
        Beregner en risikoscore for en handelsanbefaling.
        
        Args:
            recommendation (Dict): Handelsanbefaling
            portfolio (Dict): Porteføljeinformasjon
            
        Returns:
            float: Risikoscore fra 0 til 100
        """
        try:
            # Beregn ulike risikofaktorer
            position_risk = (recommendation['size'] * recommendation['current_price']) / portfolio['total_value']
            volatility_risk = recommendation.get('volatility', 0.5) * 100
            market_risk = recommendation.get('market_risk', 0.5) * 100
            
            # Vektlegg faktorene
            risk_score = (
                position_risk * 40 +
                volatility_risk * 30 +
                market_risk * 30
            )
            
            return min(max(risk_score, 0), 100)
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av risikoscore: {str(e)}")
            return 100  # Maksimal risiko ved feil 