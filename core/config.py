# -*- coding: utf-8 -*-

"""
Konfigurasjonshåndtering for AutoTrader One.
"""

import os
import yaml
import logging

def load_config(config_path):
    """
    Laster konfigurasjon fra en YAML-fil.
    
    Args:
        config_path (str): Sti til konfigurasjonsfilen
        
    Returns:
        dict: Konfigurasjonsobjekt
    """
    try:
        if not os.path.exists(config_path):
            logging.warning(f"Konfigurasjonsfil ikke funnet: {config_path}. Bruker standardkonfigurasjon.")
            return get_default_config()
            
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            
        # Valider konfigurasjon
        if not config:
            logging.warning("Tom konfigurasjonsfil. Bruker standardkonfigurasjon.")
            return get_default_config()
            
        return config
        
    except Exception as e:
        logging.error(f"Feil ved lasting av konfigurasjon: {str(e)}")
        return get_default_config()

def get_default_config():
    """
    Returnerer standardkonfigurasjon.
    
    Returns:
        dict: Standard konfigurasjonsobjekt
    """
    return {
        'symbols': ['EQNR.OL', 'DNB.OL', 'MOWI.OL', 'TEL.OL', 'AKRBP.OL'],  # Noen populære norske aksjer
        'data_sources': {
            'market_data': {
                'provider': 'yahoo',
                'days_history': 90
            },
            'news': {
                'provider': 'newsapi',
                'api_key': '',
                'days_history': 7
            },
            'fundamentals': {
                'provider': 'yahoo'
            }
        },
        'analysis': {
            'technical': {
                'indicators': ['rsi', 'sma', 'macd', 'volume']
            },
            'news': {
                'relevance_threshold': 0.6
            },
            'sentiment': {
                'sources': ['news']
            },
            'fundamental': {
                'metrics': ['pe_ratio', 'eps', 'revenue_growth']
            }
        },
        'recommendations': {
            'min_score': 60,
            'risk_weight': {
                'technical': 0.4,
                'fundamental': 0.3,
                'news': 0.2,
                'sentiment': 0.1
            }
        },
        'reporting': {
            'format': 'markdown',
            'output_dir': 'rapporter'
        },
        'logging': {
            'level': 'info',
            'file': 'logs/autotrader.log'
        }
    }

