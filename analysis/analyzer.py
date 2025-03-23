# -*- coding: utf-8 -*-

"""
Analysemodul for AutoTrader One.
"""

import logging
from analysis.technical import TechnicalAnalyzer
from analysis.news import NewsAnalyzer
from analysis.sentiment import SentimentAnalyzer
from analysis.fundamental import FundamentalAnalyzer

class AnalysisEngine:
    """Hovedklasse for analyse av markedsdata."""
    
    def __init__(self, config):
        """
        Initialiserer AnalysisEngine.
        
        Args:
            config (dict): Applikasjonskonfigurasjon
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialiser analysemoduler
        self.technical_analyzer = TechnicalAnalyzer(config)
        self.news_analyzer = NewsAnalyzer(config)
        self.sentiment_analyzer = SentimentAnalyzer(config)
        self.fundamental_analyzer = FundamentalAnalyzer(config)
    
    def analyze_all(self, market_data):
        """
        Analyserer all markedsdata.
        
        Args:
            market_data (dict): Markedsdata for alle symboler
            
        Returns:
            dict: Analyseresultater
        """
        self.logger.info("Starter analyse av markedsdata")
        
        results = {}
        
        for symbol in market_data['market_data'].keys():
            try:
                self.logger.debug("Analyserer %s", symbol)
                
                # Hent data for dette symbolet
                symbol_market_data = market_data['market_data'].get(symbol, {})
                symbol_news = market_data['news'].get(symbol, [])
                symbol_fundamentals = market_data['fundamentals'].get(symbol, {})
                
                # Utfør analyser
                technical_analysis = self.technical_analyzer.analyze(symbol_market_data)
                news_analysis = self.news_analyzer.analyze(symbol_news)
                sentiment_analysis = self.sentiment_analyzer.analyze(symbol_news)
                fundamental_analysis = self.fundamental_analyzer.analyze(symbol_fundamentals)
                
                # Samle resultatene
                results[symbol] = {
                    'technical': technical_analysis,
                    'news': news_analysis,
                    'sentiment': sentiment_analysis,
                    'fundamental': fundamental_analysis
                }
                
            except Exception as e:
                self.logger.error("Feil ved analyse av %s: %s", symbol, str(e))
        
        self.logger.info("Analyse fullført for %d symboler", len(results))
        return results

