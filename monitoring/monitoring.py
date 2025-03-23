#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Overvåkingssystem for AutoTrader One.
"""

import logging
from typing import Dict, List
import json
from datetime import datetime
from pathlib import Path

class MonitoringSystem:
    """Klasse for overvåking av AutoTrader One."""
    
    def __init__(self):
        """Initialiserer MonitoringSystem."""
        self.logger = logging.getLogger(__name__)
        self.metrics = {}
        self.alerts = []
        self.metrics_dir = Path("metrics")
        self.metrics_dir.mkdir(exist_ok=True)
    
    def track_metric(self, name: str, value: float):
        """
        Sporer en metrikk.
        
        Args:
            name (str): Navn på metrikken
            value (float): Verdi
        """
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            'timestamp': datetime.now().isoformat(),
            'value': value
        })
    
    def add_alert(self, level: str, message: str):
        """
        Legger til en varsling.
        
        Args:
            level (str): Nivå (info, warning, error)
            message (str): Melding
        """
        self.alerts.append({
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        })
        
        if level == 'error':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def save_metrics(self):
        """Lagrer metrikker til fil."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metrics_file = self.metrics_dir / f"metrics_{timestamp}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics,
            'alerts': self.alerts
        }
        
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Metrikker lagret til {metrics_file}")
    
    def get_metric_history(self, name: str) -> List[Dict]:
        """
        Henter historikk for en metrikk.
        
        Args:
            name (str): Navn på metrikken
            
        Returns:
            List[Dict]: Liste over verdier over tid
        """
        return self.metrics.get(name, [])
    
    def get_recent_alerts(self, level: str = None, limit: int = 10) -> List[Dict]:
        """
        Henter nylige varslinger.
        
        Args:
            level (str, optional): Filtrer på nivå
            limit (int): Maksimalt antall varslinger
            
        Returns:
            List[Dict]: Liste over varslinger
        """
        alerts = self.alerts
        if level:
            alerts = [a for a in alerts if a['level'] == level]
        
        return sorted(alerts, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def get_system_status(self) -> Dict:
        """
        Henter systemstatus.
        
        Returns:
            Dict: Systemstatus
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                name: values[-1]['value'] if values else None
                for name, values in self.metrics.items()
            },
            'recent_alerts': self.get_recent_alerts(),
            'total_alerts': len(self.alerts)
        } 