#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MonitoringSystem for AutoTrader One.
"""

import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time

class MonitoringSystem:
    """Klasse for overvåking av handel og portefølje i AutoTrader One."""
    
    def __init__(self, config: Dict):
        """
        Initialiserer MonitoringSystem.
        
        Args:
            config (Dict): Konfigurasjon for overvåkingssystemet
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Hent konfigurasjon
        self.max_daily_loss = config.get('max_daily_loss', 0.02)
        self.max_drawdown = config.get('max_drawdown', 0.10)
        self.alert_threshold = config.get('alert_threshold', 0.05)
        self.monitoring_interval = config.get('monitoring_interval', 60)  # sekunder
        
        # Initialiser overvåkingsdata
        self.portfolio_history = []
        self.trade_history = []
        self.alerts = []
        self.last_check = datetime.now()
        
        # Initialiser overvåkingstråd
        self.monitoring_thread = None
        self.is_monitoring = False
    
    def start_monitoring(self) -> None:
        """Starter overvåking av handel og portefølje."""
        try:
            if not self.is_monitoring:
                self.is_monitoring = True
                self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()
                self.logger.info("Overvåking startet")
            else:
                self.logger.warning("Overvåking er allerede aktiv")
            
        except Exception as e:
            self.logger.error(f"Feil ved start av overvåking: {str(e)}")
    
    def stop_monitoring(self) -> None:
        """Stopper overvåking av handel og portefølje."""
        try:
            if self.is_monitoring:
                self.is_monitoring = False
                if self.monitoring_thread:
                    self.monitoring_thread.join(timeout=5)
                self.logger.info("Overvåking stoppet")
            else:
                self.logger.warning("Overvåking er ikke aktiv")
            
        except Exception as e:
            self.logger.error(f"Feil ved stopp av overvåking: {str(e)}")
    
    def _monitoring_loop(self) -> None:
        """Hovedløkke for overvåking."""
        try:
            while self.is_monitoring:
                # Sjekk portefølje og varsler
                self._check_portfolio_alerts()
                
                # Vent til neste intervall
                time.sleep(self.monitoring_interval)
                
        except Exception as e:
            self.logger.error(f"Feil i overvåkingsløkke: {str(e)}")
            self.is_monitoring = False
    
    def update_portfolio(self, portfolio_data: Dict) -> None:
        """
        Oppdaterer porteføljedata og sjekker for varsler.
        
        Args:
            portfolio_data (Dict): Oppdatert porteføljedata
        """
        try:
            # Legg til ny porteføljedata
            self.portfolio_history.append({
                'timestamp': datetime.now(),
                'value': portfolio_data['total_value'],
                'positions': portfolio_data['positions'],
                'cash': portfolio_data['cash']
            })
            
            # Sjekk for varsler
            self._check_portfolio_alerts()
            
            # Oppdater siste sjekk
            self.last_check = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Feil ved oppdatering av porteføljedata: {str(e)}")
    
    def add_trade(self, trade_data: Dict) -> None:
        """
        Legger til en ny handel i historikken.
        
        Args:
            trade_data (Dict): Data for ny handel
        """
        try:
            # Legg til ny handel
            self.trade_history.append({
                'timestamp': datetime.now(),
                'symbol': trade_data['symbol'],
                'action': trade_data['action'],
                'quantity': trade_data['quantity'],
                'price': trade_data['price'],
                'total_value': trade_data['total_value']
            })
            
            # Sjekk for handelsvarsler
            self._check_trade_alerts(trade_data)
            
        except Exception as e:
            self.logger.error(f"Feil ved registrering av handel: {str(e)}")
    
    def get_portfolio_metrics(self) -> Dict:
        """
        Beregner porteføljemetrikker.
        
        Returns:
            Dict: Porteføljemetrikker
        """
        try:
            if not self.portfolio_history:
                return self._get_default_metrics()
            
            # Beregn avkastning
            returns = self._calculate_returns()
            
            # Beregn risikometrikker
            risk_metrics = self._calculate_risk_metrics(returns)
            
            # Beregn prestasjonsmål
            performance_metrics = self._calculate_performance_metrics(returns)
            
            return {
                'returns': {
                    'daily': round(returns['daily'] * 100, 2),
                    'weekly': round(returns['weekly'] * 100, 2),
                    'monthly': round(returns['monthly'] * 100, 2),
                    'yearly': round(returns['yearly'] * 100, 2)
                },
                'risk': risk_metrics,
                'performance': performance_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av porteføljemetrikker: {str(e)}")
            return self._get_default_metrics()
    
    def get_alerts(self) -> List[Dict]:
        """
        Henter aktive varsler.
        
        Returns:
            List[Dict]: Liste over aktive varsler
        """
        return self.alerts
    
    def _check_portfolio_alerts(self) -> None:
        """Sjekker for porteføljevarsler."""
        try:
            if len(self.portfolio_history) < 2:
                return
            
            current_value = self.portfolio_history[-1]['value']
            previous_value = self.portfolio_history[-2]['value']
            
            # Sjekk for daglig tap
            daily_return = (current_value - previous_value) / previous_value
            if abs(daily_return) > self.max_daily_loss:
                self._add_alert(
                    'high_daily_loss',
                    f'Daglig tap overskrider grense: {round(daily_return * 100, 2)}%'
                )
            
            # Sjekk for drawdown
            peak_value = max(h['value'] for h in self.portfolio_history)
            drawdown = (current_value - peak_value) / peak_value
            if abs(drawdown) > self.max_drawdown:
                self._add_alert(
                    'high_drawdown',
                    f'Drawdown overskrider grense: {round(drawdown * 100, 2)}%'
                )
            
        except Exception as e:
            self.logger.error(f"Feil ved sjekk av porteføljevarsler: {str(e)}")
    
    def _check_trade_alerts(self, trade_data: Dict) -> None:
        """
        Sjekker for handelsvarsler.
        
        Args:
            trade_data (Dict): Data for ny handel
        """
        try:
            # Sjekk for store handler
            portfolio_value = self.portfolio_history[-1]['value']
            trade_value = trade_data['total_value']
            trade_size = trade_value / portfolio_value
            
            if trade_size > self.alert_threshold:
                self._add_alert(
                    'large_trade',
                    f'Stor handel i {trade_data["symbol"]}: {round(trade_size * 100, 2)}% av portefølje'
                )
            
            # Sjekk for hyppige handler
            recent_trades = [
                t for t in self.trade_history
                if t['symbol'] == trade_data['symbol']
                and datetime.now() - t['timestamp'] < timedelta(hours=24)
            ]
            
            if len(recent_trades) > 3:
                self._add_alert(
                    'frequent_trades',
                    f'Hyppige handler i {trade_data["symbol"]}: {len(recent_trades)} handler siste 24t'
                )
            
        except Exception as e:
            self.logger.error(f"Feil ved sjekk av handelsvarsler: {str(e)}")
    
    def _add_alert(self, alert_type: str, message: str) -> None:
        """
        Legger til et nytt varsel.
        
        Args:
            alert_type (str): Type varsel
            message (str): Varselmelding
        """
        alert = {
            'timestamp': datetime.now(),
            'type': alert_type,
            'message': message
        }
        
        self.alerts.append(alert)
        self.logger.warning(f"Nytt varsel: {message}")
    
    def _calculate_returns(self) -> Dict:
        """
        Beregner avkastning over ulike perioder.
        
        Returns:
            Dict: Avkastning for ulike perioder
        """
        try:
            values = pd.DataFrame(
                [(h['timestamp'], h['value']) for h in self.portfolio_history],
                columns=['timestamp', 'value']
            ).set_index('timestamp')
            
            current_value = values['value'].iloc[-1]
            daily_value = values['value'].iloc[-2] if len(values) > 1 else current_value
            weekly_value = values['value'].iloc[-6] if len(values) > 5 else current_value
            monthly_value = values['value'].iloc[-21] if len(values) > 20 else current_value
            yearly_value = values['value'].iloc[-252] if len(values) > 251 else current_value
            
            return {
                'daily': (current_value - daily_value) / daily_value,
                'weekly': (current_value - weekly_value) / weekly_value,
                'monthly': (current_value - monthly_value) / monthly_value,
                'yearly': (current_value - yearly_value) / yearly_value
            }
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av avkastning: {str(e)}")
            return {'daily': 0.0, 'weekly': 0.0, 'monthly': 0.0, 'yearly': 0.0}
    
    def _calculate_risk_metrics(self, returns: Dict) -> Dict:
        """
        Beregner risikometrikker.
        
        Args:
            returns (Dict): Avkastning for ulike perioder
            
        Returns:
            Dict: Risikometrikker
        """
        try:
            values = pd.DataFrame(
                [(h['timestamp'], h['value']) for h in self.portfolio_history],
                columns=['timestamp', 'value']
            ).set_index('timestamp')
            
            daily_returns = values['value'].pct_change().dropna()
            
            volatility = daily_returns.std() * np.sqrt(252)
            var_95 = np.percentile(daily_returns, 5)
            max_drawdown = self._calculate_max_drawdown(values['value'])
            
            return {
                'volatility': round(volatility * 100, 2),
                'var_95': round(abs(var_95) * 100, 2),
                'max_drawdown': round(max_drawdown * 100, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av risikometrikker: {str(e)}")
            return {'volatility': 0.0, 'var_95': 0.0, 'max_drawdown': 0.0}
    
    def _calculate_performance_metrics(self, returns: Dict) -> Dict:
        """
        Beregner prestasjonsmål.
        
        Args:
            returns (Dict): Avkastning for ulike perioder
            
        Returns:
            Dict: Prestasjonsmål
        """
        try:
            values = pd.DataFrame(
                [(h['timestamp'], h['value']) for h in self.portfolio_history],
                columns=['timestamp', 'value']
            ).set_index('timestamp')
            
            daily_returns = values['value'].pct_change().dropna()
            
            # Beregn Sharpe ratio (antar 2% risikofri rente)
            excess_returns = daily_returns - 0.02/252
            sharpe = np.sqrt(252) * excess_returns.mean() / daily_returns.std()
            
            # Beregn Sortino ratio
            downside_returns = daily_returns[daily_returns < 0]
            sortino = np.sqrt(252) * excess_returns.mean() / downside_returns.std()
            
            # Beregn Information ratio
            # I en produksjonsversjon bør vi sammenligne med en referanseindeks
            ir = np.sqrt(252) * daily_returns.mean() / daily_returns.std()
            
            return {
                'sharpe_ratio': round(sharpe, 2),
                'sortino_ratio': round(sortino, 2),
                'information_ratio': round(ir, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av prestasjonsmål: {str(e)}")
            return {'sharpe_ratio': 0.0, 'sortino_ratio': 0.0, 'information_ratio': 0.0}
    
    def _calculate_max_drawdown(self, values: pd.Series) -> float:
        """
        Beregner maksimal drawdown.
        
        Args:
            values (pd.Series): Porteføljeverdier
            
        Returns:
            float: Maksimal drawdown
        """
        try:
            rolling_max = values.expanding().max()
            drawdown = (values - rolling_max) / rolling_max
            return abs(drawdown.min())
            
        except Exception as e:
            self.logger.error(f"Feil ved beregning av maksimal drawdown: {str(e)}")
            return 0.0
    
    def _get_default_metrics(self) -> Dict:
        """
        Returnerer standardmetrikker.
        
        Returns:
            Dict: Standardmetrikker
        """
        return {
            'returns': {
                'daily': 0.0,
                'weekly': 0.0,
                'monthly': 0.0,
                'yearly': 0.0
            },
            'risk': {
                'volatility': 0.0,
                'var_95': 0.0,
                'max_drawdown': 0.0
            },
            'performance': {
                'sharpe_ratio': 0.0,
                'sortino_ratio': 0.0,
                'information_ratio': 0.0
            }
        } 