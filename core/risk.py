#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Risikostyringsmodul for AutoTrader One.
"""

import logging
from typing import Dict, Tuple, Optional
from datetime import datetime

class RiskManager:
    """Klasse for å håndtere risikostyring i handelssystemet."""
    
    def __init__(self, config: Dict):
        """
        Initialiserer RiskManager.
        
        Args:
            config (dict): Applikasjonskonfigurasjon
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Hent risikoparametre fra konfigurasjon
        risk_config = config.get('risk', {})
        self.max_position_size = risk_config.get('max_position_size', 0.1)  # 10% av portefølje
        self.max_daily_loss = risk_config.get('max_daily_loss', 0.02)  # 2% per dag
        self.max_drawdown = risk_config.get('max_drawdown', 0.1)  # 10% maksimal drawdown
        self.max_leverage = risk_config.get('max_leverage', 1.0)  # Ingen gearing som standard
        
        # Spor dagens tap
        self.daily_loss = 0.0
        self.daily_start_value = 0.0
        self.peak_portfolio_value = 0.0
    
    def validate_trade(self, recommendation: Dict, portfolio: Dict) -> Tuple[bool, str]:
        """
        Validerer om en handel er innenfor risikoparametre.
        
        Args:
            recommendation (dict): Handelsanbefaling
            portfolio (dict): Nåværende portefølje
            
        Returns:
            tuple: (bool, str) - (er handelen gyldig, forklaring)
        """
        # Sjekk risikoscore
        if recommendation.get('risk_score', 100) > 80:
            return False, "For høy risiko (score > 80)"
        
        # Sjekk posisjonsstørrelse
        position_size = self._calculate_position_size(recommendation, portfolio)
        if position_size > self.max_position_size:
            return False, f"Posisjon for stor ({position_size:.1%} > {self.max_position_size:.1%})"
        
        # Sjekk daglig tap
        if self.daily_loss > self.max_daily_loss:
            return False, f"Dagens maksimale tap nådd ({self.daily_loss:.1%} > {self.max_daily_loss:.1%})"
        
        # Sjekk drawdown
        current_value = portfolio.get('total_value', 0)
        if current_value > 0 and self.peak_portfolio_value > 0:
            drawdown = (self.peak_portfolio_value - current_value) / self.peak_portfolio_value
            if drawdown > self.max_drawdown:
                return False, f"Maksimal drawdown nådd ({drawdown:.1%} > {self.max_drawdown:.1%})"
        
        return True, "Handel godkjent"
    
    def update_daily_metrics(self, portfolio_value: float) -> None:
        """
        Oppdaterer daglige risikometrikker.
        
        Args:
            portfolio_value (float): Nåværende porteføljeverdi
        """
        # Oppdater peak value
        self.peak_portfolio_value = max(self.peak_portfolio_value, portfolio_value)
        
        # Beregn dagens tap
        if self.daily_start_value == 0:
            self.daily_start_value = portfolio_value
        else:
            self.daily_loss = (self.daily_start_value - portfolio_value) / self.daily_start_value
    
    def reset_daily_metrics(self) -> None:
        """Nullstiller daglige metrikker."""
        self.daily_loss = 0.0
        self.daily_start_value = 0.0
    
    def _calculate_position_size(self, recommendation: Dict, portfolio: Dict) -> float:
        """
        Beregner optimal posisjonsstørrelse for en handel.
        
        Args:
            recommendation (dict): Handelsanbefaling
            portfolio (dict): Nåværende portefølje
            
        Returns:
            float: Posisjonsstørrelse som andel av porteføljen
        """
        # Basis posisjonsstørrelse basert på risikoscore
        base_size = min(1.0, recommendation['success_probability'] / 100)
        
        # Juster for risiko
        risk_adjustment = 1 - (recommendation['risk_score'] / 100)
        
        # Beregn final posisjonsstørrelse
        position_size = base_size * risk_adjustment
        
        # Begrens til maksimal størrelse
        return min(position_size, self.max_position_size) 