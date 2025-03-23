#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Overvåkningsmodul for AutoTrader One.
"""

import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

class Alert:
    """Klasse for å definere varsler."""
    
    def __init__(self, name: str, condition: str, threshold: float, 
                 severity: str = 'info', description: str = ''):
        """
        Initialiserer et varsel.
        
        Args:
            name (str): Navn på varslet
            condition (str): Betingelse ('gt', 'lt', 'eq')
            threshold (float): Terskelverdi
            severity (str): Alvorlighetsgrad ('info', 'warning', 'error')
            description (str): Beskrivelse av varslet
        """
        self.name = name
        self.condition = condition
        self.threshold = threshold
        self.severity = severity
        self.description = description
        self.last_triggered = None
    
    def should_trigger(self, current_value: float) -> bool:
        """
        Sjekker om varslet skal utløses.
        
        Args:
            current_value (float): Nåværende verdi
            
        Returns:
            bool: True hvis varslet skal utløses
        """
        if self.condition == 'gt':
            return current_value > self.threshold
        elif self.condition == 'lt':
            return current_value < self.threshold
        elif self.condition == 'eq':
            return abs(current_value - self.threshold) < 0.0001
        return False

class MonitoringSystem:
    """Klasse for å overvåke systemets ytelse og tilstand."""
    
    def __init__(self, config: Dict):
        """
        Initialiserer MonitoringSystem.
        
        Args:
            config (dict): Applikasjonskonfigurasjon
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialiser metrikker og varsler
        self.metrics: Dict[str, List[tuple]] = {}
        self.alerts: List[Alert] = []
        
        # Last konfigurerte varsler
        self._load_alerts()
        
        # Opprett metrikk-katalog
        self.metrics_dir = 'metrics'
        if not os.path.exists(self.metrics_dir):
            os.makedirs(self.metrics_dir)
    
    def track_metric(self, name: str, value: float, timestamp: Optional[float] = None) -> None:
        """
        Sporer en metrikk.
        
        Args:
            name (str): Navn på metrikken
            value (float): Verdi
            timestamp (float, optional): Tidspunkt
        """
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append((timestamp or time.time(), value))
        
        # Behold bare de siste 1000 verdiene
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
        
        # Sjekk varsler
        self.check_alerts(name, value)
    
    def check_alerts(self, metric_name: str, current_value: float) -> None:
        """
        Sjekker om noen varsler skal utløses.
        
        Args:
            metric_name (str): Navn på metrikken
            current_value (float): Nåværende verdi
        """
        for alert in self.alerts:
            if alert.name == metric_name and alert.should_trigger(current_value):
                self._trigger_alert(alert, current_value)
    
    def _trigger_alert(self, alert: Alert, current_value: float) -> None:
        """
        Utløser et varsel.
        
        Args:
            alert (Alert): Varselobjektet
            current_value (float): Nåværende verdi
        """
        # Sjekk om varslet allerede er utløst nylig
        if alert.last_triggered and time.time() - alert.last_triggered < 3600:  # 1 time cooldown
            return
        
        message = f"Varsel: {alert.name} = {current_value:.2f} {alert.description}"
        
        if alert.severity == 'error':
            self.logger.error(message)
        elif alert.severity == 'warning':
            self.logger.warning(message)
        else:
            self.logger.info(message)
        
        alert.last_triggered = time.time()
    
    def save_metrics(self) -> None:
        """Lagrer metrikker til disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.metrics_dir, f"metrics_{timestamp}.json")
        
        # Konverter metrikker til serialiserbar format
        serializable_metrics = {}
        for name, values in self.metrics.items():
            serializable_metrics[name] = [
                {"timestamp": ts, "value": val}
                for ts, val in values
            ]
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(serializable_metrics, f, indent=2)
            self.logger.info(f"Metrikker lagret til {filename}")
        except Exception as e:
            self.logger.error(f"Feil ved lagring av metrikker: {str(e)}")
    
    def _load_alerts(self) -> None:
        """Laster konfigurerte varsler fra konfigurasjonen."""
        alerts_config = self.config.get('monitoring', {}).get('alerts', [])
        
        for alert_config in alerts_config:
            alert = Alert(
                name=alert_config['name'],
                condition=alert_config['condition'],
                threshold=alert_config['threshold'],
                severity=alert_config.get('severity', 'info'),
                description=alert_config.get('description', '')
            )
            self.alerts.append(alert) 