#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AutoTrader One - Automatisk handelssystem
"""

import logging
import asyncio
import argparse
from typing import Dict, List, Optional
import yaml
from datetime import datetime

from data_sources.alpha_vantage import AlphaVantageProvider
from data_sources.fmp import FMPProvider
from data_sources.news_api import NewsAPIProvider
from analysis.technical import TechnicalAnalyzer
from analysis.fundamental import FundamentalAnalyzer
from analysis.sentiment import SentimentAnalyzer
from risk_management.risk_manager import RiskManager
from reporting.report_generator import ReportGenerator

class AutoTraderOne:
    """Hovedklasse for AutoTrader One."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialiserer AutoTrader One.
        
        Args:
            config_path (str): Sti til konfigurasjonsfil
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        
        # Sett opp dataprovidere
        self.market_data = AlphaVantageProvider(self.config['market_data'])
        self.fundamental_data = FMPProvider(self.config['fundamental_data'])
        self.news_data = NewsAPIProvider(self.config['news_data'])
        
        # Sett opp analysatorer
        self.technical_analyzer = TechnicalAnalyzer(self.config['analysis'])
        self.fundamental_analyzer = FundamentalAnalyzer(self.config['analysis'])
        self.sentiment_analyzer = SentimentAnalyzer(self.config['analysis'])
        
        # Sett opp risikostyring
        self.risk_manager = RiskManager(self.config['risk_management'])
        
        # Sett opp rapportgenerering
        self.report_generator = ReportGenerator(self.config['reporting'])
        
        self.logger.info("AutoTrader One starter")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Laster konfigurasjon fra fil.
        
        Args:
            config_path (str): Sti til konfigurasjonsfil
            
        Returns:
            Dict: Konfigurasjon
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Feil ved lasting av konfigurasjon: {str(e)}")
            raise
    
    async def analyze_symbol(self, symbol: str) -> Optional[Dict]:
        """
        Analyserer et symbol.
        
        Args:
            symbol (str): Symbol å analysere
            
        Returns:
            Optional[Dict]: Analyse eller None ved feil
        """
        try:
            self.logger.info(f"Analyserer {symbol}")
            
            # Hent data
            market_data = await self.market_data.get_historical_data(symbol)
            technical_indicators = await self.market_data.get_technical_indicators(symbol)
            fundamental_data = await self.fundamental_data.get_fundamental_data(symbol)
            news = await self.news_data.get_news(symbol)
            
            if not all([market_data, technical_indicators, fundamental_data, news]):
                self.logger.error(f"Kunne ikke hente all data for {symbol}")
                return None
            
            # Utfør analyser
            technical_analysis = self.technical_analyzer.analyze(market_data, technical_indicators)
            fundamental_analysis = self.fundamental_analyzer.analyze(fundamental_data)
            sentiment_analysis = self.sentiment_analyzer.analyze(news)
            
            # Beregn total score
            total_score = self._calculate_total_score(
                technical_analysis,
                fundamental_analysis,
                sentiment_analysis
            )
            
            # Vurder risiko
            risk_assessment = self.risk_manager.assess_risk(
                symbol,
                market_data,
                technical_analysis,
                fundamental_analysis,
                sentiment_analysis
            )
            
            # Bestem anbefaling
            recommendation = self._get_recommendation(total_score, risk_assessment)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'technical_analysis': technical_analysis,
                'fundamental_analysis': fundamental_analysis,
                'sentiment_analysis': sentiment_analysis,
                'total_score': total_score,
                'risk_assessment': risk_assessment,
                'recommendation': recommendation
            }
            
        except Exception as e:
            self.logger.error(f"Feil ved analyse av {symbol}: {str(e)}")
            return None
    
    def _calculate_total_score(self, technical: Dict, fundamental: Dict, sentiment: Dict) -> float:
        """
        Beregner total score basert på alle analyser.
        
        Args:
            technical (Dict): Teknisk analyse
            fundamental (Dict): Fundamental analyse
            sentiment (Dict): Sentiment-analyse
            
        Returns:
            float: Total score
        """
        weights = self.config['analysis']['weights']
        
        technical_score = technical.get('score', 0.0) * weights['technical']
        fundamental_score = fundamental.get('score', 0.0) * weights['fundamental']
        sentiment_score = sentiment.get('score', 0.0) * weights['sentiment']
        
        return technical_score + fundamental_score + sentiment_score
    
    def _get_recommendation(self, total_score: float, risk_assessment: Dict) -> str:
        """
        Bestemmer anbefaling basert på score og risiko.
        
        Args:
            total_score (float): Total score
            risk_assessment (Dict): Risikovurdering
            
        Returns:
            str: Anbefaling (buy/hold/sell)
        """
        thresholds = self.config['recommendations']['thresholds']
        risk_score = risk_assessment.get('risk_score', 0.0)
        
        if total_score >= thresholds['buy'] and risk_score <= thresholds['max_risk']:
            return 'buy'
        elif total_score <= thresholds['sell'] or risk_score >= thresholds['max_risk']:
            return 'sell'
        else:
            return 'hold'
    
    async def run(self, symbols: List[str]) -> None:
        """
        Kjører AutoTrader One.
        
        Args:
            symbols (List[str]): Liste med symboler å analysere
        """
        try:
            # Analyser hvert symbol
            analyses = []
            for symbol in symbols:
                analysis = await self.analyze_symbol(symbol)
                if analysis:
                    analyses.append(analysis)
            
            if not analyses:
                self.logger.error("Ingen analyser ble generert")
                return
            
            # Generer rapport
            metrics = self.risk_manager.get_portfolio_metrics(analyses)
            self.report_generator.generate_report(analyses, metrics)
            
            self.logger.info("AutoTrader One fullført")
            
        except Exception as e:
            self.logger.error(f"Feil under kjøring: {str(e)}")

def main():
    """Hovedfunksjon."""
    # Sett opp argumentparsing
    parser = argparse.ArgumentParser(description="AutoTrader One - Automatisk handelssystem")
    parser.add_argument("--config", default="config.yaml", help="Sti til konfigurasjonsfil")
    parser.add_argument("--debug", action="store_true", help="Aktiver debug-logging")
    parser.add_argument("--symbols", nargs="+", help="Liste med symboler å analysere")
    args = parser.parse_args()
    
    # Sett opp logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Opprett og kjør AutoTrader One
    trader = AutoTraderOne(args.config)
    
    # Bestem symboler
    if args.symbols:
        symbols = args.symbols
    else:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            symbols = config['symbols']
    
    # Kjør systemet
    asyncio.run(trader.run(symbols))

if __name__ == "__main__":
    main()

