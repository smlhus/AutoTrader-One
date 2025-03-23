#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sentimentanalyse for AutoTrader One.
"""

import logging
from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta
from textblob import TextBlob

class SentimentAnalyzer:
    """Klasse for sentimentanalyse i AutoTrader One."""
    
    def __init__(self, config: Dict):
        """
        Initialiserer SentimentAnalyzer.
        
        Args:
            config (Dict): Konfigurasjon for sentimentanalyse
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Hent konfigurasjon
        self.min_articles = config.get('min_articles', 3)
        self.recent_weight = config.get('recent_weight', 0.7)
        self.older_weight = config.get('older_weight', 0.3)
        self.recent_days = config.get('recent_days', 3)
    
    def analyze(self, news_data: List[Dict]) -> Dict:
        """
        Utfører sentimentanalyse på nyhetsdata.
        
        Args:
            news_data (List[Dict]): Liste med nyhetsartikler
            
        Returns:
            Dict: Analyseresultater
        """
        try:
            if not news_data or len(news_data) < self.min_articles:
                self.logger.warning(f"For få artikler for sentimentanalyse (minimum {self.min_articles})")
                return self._get_default_result()
            
            # Konverter til DataFrame for enklere håndtering
            df = pd.DataFrame(news_data)
            df['published_at'] = pd.to_datetime(df['published_at'])
            df['sentiment'] = df.apply(lambda x: self._analyze_text(x['title'] + ' ' + x['description']), axis=1)
            
            # Del opp i nylige og eldre artikler
            cutoff_date = datetime.now() - timedelta(days=self.recent_days)
            recent_articles = df[df['published_at'] >= cutoff_date]
            older_articles = df[df['published_at'] < cutoff_date]
            
            # Beregn sentiment-scores
            recent_sentiment = recent_articles['sentiment'].mean() if not recent_articles.empty else 0
            older_sentiment = older_articles['sentiment'].mean() if not older_articles.empty else 0
            
            # Beregn vektet gjennomsnitt
            weighted_sentiment = (
                recent_sentiment * self.recent_weight +
                older_sentiment * self.older_weight
            )
            
            # Konverter til 0-100 skala
            sentiment_score = self._normalize_sentiment(weighted_sentiment)
            
            # Bestem anbefaling
            recommendation = self._get_recommendation(sentiment_score)
            
            return {
                'score': sentiment_score,
                'recommendation': recommendation,
                'metrics': {
                    'recent_sentiment': round(recent_sentiment, 3),
                    'older_sentiment': round(older_sentiment, 3),
                    'total_articles': len(df),
                    'recent_articles': len(recent_articles),
                    'older_articles': len(older_articles)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Feil ved sentimentanalyse: {str(e)}")
            return self._get_default_result()
    
    def _analyze_text(self, text: str) -> float:
        """
        Analyserer sentiment i tekst.
        
        Args:
            text (str): Tekst som skal analyseres
            
        Returns:
            float: Sentiment-score (-1 til 1)
        """
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
            
        except Exception as e:
            self.logger.error(f"Feil ved tekstanalyse: {str(e)}")
            return 0.0
    
    def _normalize_sentiment(self, sentiment: float) -> float:
        """
        Konverterer sentiment fra -1,1 skala til 0-100 skala.
        
        Args:
            sentiment (float): Sentiment-score (-1 til 1)
            
        Returns:
            float: Normalisert score (0 til 100)
        """
        try:
            # Konverter fra -1,1 til 0,100 skala
            normalized = (sentiment + 1) * 50
            
            # Avrund til én desimal
            return round(normalized, 1)
            
        except Exception as e:
            self.logger.error(f"Feil ved normalisering av sentiment: {str(e)}")
            return 50.0
    
    def _get_recommendation(self, score: float) -> str:
        """
        Bestemmer anbefaling basert på sentiment-score.
        
        Args:
            score (float): Sentiment-score
            
        Returns:
            str: Anbefaling (buy, sell, hold)
        """
        if score >= 70:
            return 'buy'
        elif score <= 30:
            return 'sell'
        else:
            return 'hold'
    
    def _get_default_result(self) -> Dict:
        """
        Returnerer standardresultat ved feil eller manglende data.
        
        Returns:
            Dict: Standardresultat
        """
        return {
            'score': 50.0,
            'recommendation': 'hold',
            'metrics': {
                'recent_sentiment': 0.0,
                'older_sentiment': 0.0,
                'total_articles': 0,
                'recent_articles': 0,
                'older_articles': 0
            }
        }

