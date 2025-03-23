# -*- coding: utf-8 -*-

"""
Loggoppsett for AutoTrader One.
"""

import os
import logging
from datetime import datetime

def setup_logger(level, log_file):
    """
    Setter opp logging for applikasjonen.
    
    Args:
        level (int): Loggnivå (logging.DEBUG, logging.INFO, etc.)
        log_file (str): Sti til loggfil
        
    Returns:
        logging.Logger: Konfigurert logger
    """
    # Opprett loggkatalog hvis den ikke eksisterer
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Konfigurer root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Fjern eksisterende handlers for å unngå dupliserte logger
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Opprett filhåndterer
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Opprett konsolhåndterer
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    return logger

