# -*- coding: utf-8 -*-

"""
Nyhetsanalysemodul for AutoTrader One.
"""

import logging
from datetime import datetime

class NewsAnalyzer:
    """Klasse for analyse av nyheter."""
    
    def __init__(self, config):
        """
        Initialiserer NewsAnalyzer.
        
        Args:
            config (dict): Applikasjonskonfigurasjon
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Hent konfigurasjon
        self.relevance_threshold = config.get('analysis', {}).get('news', {}).get('relevance_threshold', 0.6)
    
    def analyze(self, news_data):
        """
        Analyserer nyhetsdata.
        
        Args:
            news_data (list): Nyhetsartikler
            
        Returns:
            dict: Nyhetsanalyseresultat
        """
        if not news_data:
            self.logger.warning("Ingen nyhetsdata å analysere")
            return {'score': 50, 'articles': []}
        
        self.logger.info("Analyserer %d nyhetsartikler", len(news_data))
        
        # Sorter nyheter etter dato (nyeste først)
        sorted_news = sorted(news_data, 
                            key=lambda x: datetime.fromisoformat(x['published_at'].replace('Z', '+00:00')), 
                            reverse=True)
        
        # Analyser hver artikkel
        analyzed_articles = []
        for article in sorted_news:
            relevance = self._calculate_relevance(article)
            impact = self._calculate_impact(article)
            
            if relevance >= self.relevance_threshold:
                analyzed_articles.append({
                    'title': article['title'],
                    'source': article.get('source', 'Ukjent'),
                    'published_at': article['published_at'],
                    'relevance': relevance,
                    'impact': impact,
                    'sentiment': article.get('sentiment', self._estimate_sentiment(article))
                })
        
        # Beregn samlet score (0-100)
        if analyzed_articles:
            # Vekt nyere artikler høyere
            weights = [max(0.5, 1.0 - i*0.1) for i in range(len(analyzed_articles))]
            total_weight = sum(weights)
            
            # Beregn vektet gjennomsnitt av impact
            weighted_impact = sum(a['impact'] * w for a, w in zip(analyzed_articles, weights)) / total_weight
            
            # Konverter til score (0-100)
            score = 50 + weighted_impact * 25
        else:
            score = 50  # Nøytral hvis ingen relevante artikler
        
        return {
            'score': round(score, 1),
            'articles': analyzed_articles[:5],  # Returner bare de 5 mest relevante
            'recommendation': 'buy' if score > 60 else ('sell' if score < 40 else 'hold')
        }
    
    def _calculate_relevance(self, article):
        """
        Beregner relevansen til en nyhetsartikkel.
        
        Args:
            article (dict): Nyhetsartikkel
            
        Returns:
            float: Relevans (0-1)
        """
        # I en faktisk implementasjon ville vi bruke NLP for å beregne relevans
        # For demonstrasjonsformål returnerer vi en høy verdi
        return 0.8
    
    def _calculate_impact(self, article):
        """
        Beregner den potensielle innvirkningen av en nyhetsartikkel.
        
        Args:
            article (dict): Nyhetsartikkel
            
        Returns:
            float: Innvirkning (-1 til 1, hvor positiv er positiv innvirkning)
        """
        # I en faktisk implementasjon ville vi bruke NLP for å beregne innvirkning
        # For demonstrasjonsformål bruker vi sentiment hvis tilgjengelig
        sentiment = article.get('sentiment', self._estimate_sentiment(article))
        
        if sentiment == 'positive':
            return 0.7
        elif sentiment == 'negative':
            return -0.7
        else:
            return 0.0
    
    def _estimate_sentiment(self, article):
        """
        Estimerer sentimentet til en nyhetsartikkel.
        
        Args:
            article (dict): Nyhetsartikkel
            
        Returns:
            str: Sentiment ('positive', 'negative', eller 'neutral')
        """
        # I en faktisk implementasjon ville vi bruke NLP for å beregne sentiment
        # For demonstrasjonsformål bruker vi en enkel ordbasert tilnærming
        
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        
        positive_words = ['øker', 'vekst', 'positiv', 'oppgang', 'sterk', 'bedre', 'overgår', 'suksess']
        negative_words = ['faller', 'nedgang', 'negativ', 'tap', 'svak', 'dårlig', 'skuffende', 'problemer']
        
        positive_count = sum(1 for word in positive_words if word in title or word in description)
        negative_count = sum(1 for word in negative_words if word in title or word in description)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

