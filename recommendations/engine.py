# -*- coding: utf-8 -*-

"""
Anbefalingsmodul for AutoTrader One.
"""

import logging
import numpy as np
from datetime import datetime

class RecommendationEngine:
    """Klasse for å generere handelsanbefalinger."""
    
    def __init__(self, config):
        """
        Initialiserer RecommendationEngine.
        
        Args:
            config (dict): Applikasjonskonfigurasjon
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Hent konfigurasjon
        self.min_score = config.get('recommendations', {}).get('min_score', 60)
        self.risk_weights = config.get('recommendations', {}).get('risk_weight', {
            'technical': 0.4,
            'fundamental': 0.3,
            'news': 0.2,
            'sentiment': 0.1
        })
    
    def generate_recommendations(self, analysis_results):
        """
        Genererer handelsanbefalinger basert på analyseresultater.
        
        Args:
            analysis_results (dict): Analyseresultater for alle symboler
            
        Returns:
            list: Handelsanbefalinger
        """
        self.logger.info("Genererer handelsanbefalinger for %d symboler", len(analysis_results))
        
        recommendations = []
        
        for symbol, analysis in analysis_results.items():
            try:
                # Beregn samlet score
                overall_score = self._calculate_overall_score(analysis)
                
                # Beregn risikoscore (0-100, hvor høyere er mer risikabelt)
                risk_score = self._calculate_risk_score(analysis)
                
                # Beregn sannsynlighet for suksess (0-100%)
                success_probability = self._calculate_success_probability(overall_score, risk_score)
                
                # Beregn potensiell avkastning (%)
                potential_return = self._calculate_potential_return(overall_score, risk_score)
                
                # Bestem anbefaling (kjøp, selg, hold)
                if overall_score >= self.min_score:
                    recommendation = 'buy'
                elif overall_score <= 100 - self.min_score:
                    recommendation = 'sell'
                else:
                    recommendation = 'hold'
                
                # Generer forklaring
                explanation = self._generate_explanation(symbol, analysis, overall_score, 
                                                       recommendation, risk_score, 
                                                       success_probability, potential_return)
                
                # Legg til anbefaling
                recommendations.append({
                    'symbol': symbol,
                    'recommendation': recommendation,
                    'overall_score': round(overall_score, 1),
                    'risk_score': round(risk_score, 1),
                    'success_probability': round(success_probability, 1),
                    'potential_return': round(potential_return, 1),
                    'explanation': explanation,
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.error("Feil ved generering av anbefaling for %s: %s", symbol, str(e))
        
        # Sorter anbefalinger etter score (høyest først for kjøp, lavest først for salg)
        buy_recommendations = [r for r in recommendations if r['recommendation'] == 'buy']
        sell_recommendations = [r for r in recommendations if r['recommendation'] == 'sell']
        hold_recommendations = [r for r in recommendations if r['recommendation'] == 'hold']
        
        buy_recommendations.sort(key=lambda x: x['overall_score'], reverse=True)
        sell_recommendations.sort(key=lambda x: x['overall_score'])
        
        # Kombiner sorterte anbefalinger
        sorted_recommendations = buy_recommendations + sell_recommendations + hold_recommendations
        
        self.logger.info("Genererte %d anbefalinger (%d kjøp, %d selg, %d hold)", 
                        len(sorted_recommendations), 
                        len(buy_recommendations), 
                        len(sell_recommendations), 
                        len(hold_recommendations))
        
        return sorted_recommendations
    
    def _calculate_overall_score(self, analysis):
        """
        Beregner samlet score basert på alle analysetyper.
        
        Args:
            analysis (dict): Analyseresultater for et symbol
            
        Returns:
            float: Samlet score (0-100)
        """
        scores = {}
        
        # Hent scores fra hver analysetype
        if 'technical' in analysis:
            scores['technical'] = analysis['technical'].get('score', 50)
        
        if 'fundamental' in analysis:
            scores['fundamental'] = analysis['fundamental'].get('score', 50)
        
        if 'news' in analysis:
            scores['news'] = analysis['news'].get('score', 50)
        
        if 'sentiment' in analysis:
            scores['sentiment'] = analysis['sentiment'].get('score', 50)
        
        # Beregn vektet gjennomsnitt
        weighted_sum = 0
        total_weight = 0
        
        for analysis_type, score in scores.items():
            weight = self.risk_weights.get(analysis_type, 0)
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 50  # Nøytral hvis ingen vekter
        
        return weighted_sum / total_weight
    
    def _calculate_risk_score(self, analysis):
        """
        Beregner risikoscore.
        
        Args:
            analysis (dict): Analyseresultater for et symbol
            
        Returns:
            float: Risikoscore (0-100, hvor høyere er mer risikabelt)
        """
        # Beregn volatilitet fra teknisk analyse hvis tilgjengelig
        volatility = 50  # Standard middels risiko
        
        if 'technical' in analysis:
            # Bruk RSI som en indikator på volatilitet
            technical = analysis['technical']
            if 'signals' in technical and 'rsi' in technical['signals']:
                rsi = technical['signals']['rsi'].get('value', 50)
                
                # RSI nær ekstremene indikerer høyere risiko
                rsi_risk = abs(rsi - 50) / 50 * 100
                volatility = max(volatility, rsi_risk)
        
        # Juster risiko basert på sentiment
        sentiment_risk = 50
        if 'sentiment' in analysis:
            sentiment_score = analysis['sentiment'].get('score', 50)
            
            # Ekstreme sentiment-verdier indikerer høyere risiko
            sentiment_risk = abs(sentiment_score - 50) / 50 * 100
        
        # Juster risiko basert på fundamentale data
        fundamental_risk = 50
        if 'fundamental' in analysis:
            fundamental = analysis['fundamental']
            
            # Høy P/E-ratio indikerer høyere risiko
            if 'metrics' in fundamental and 'pe_ratio' in fundamental['metrics']:
                pe_ratio = fundamental['metrics']['pe_ratio'].get('value', 15)
                
                if pe_ratio > 30:
                    fundamental_risk = 70
                elif pe_ratio < 5:
                    fundamental_risk = 60  # Også risikabelt hvis for lavt
        
        # Kombiner risikoer
        combined_risk = (volatility * 0.4 + sentiment_risk * 0.3 + fundamental_risk * 0.3)
        
        return combined_risk
    
    def _calculate_success_probability(self, overall_score, risk_score):
        """
        Beregner sannsynlighet for suksess.
        
        Args:
            overall_score (float): Samlet score
            risk_score (float): Risikoscore
            
        Returns:
            float: Sannsynlighet for suksess (0-100%)
        """
        # Juster sannsynlighet basert på score og risiko
        if overall_score > 50:  # Kjøpsanbefaling
            base_probability = 50 + (overall_score - 50) * 0.8
        else:  # Salgsanbefaling
            base_probability = 50 + (50 - overall_score) * 0.8
        
        # Juster for risiko (høyere risiko reduserer sannsynlighet)
        risk_adjustment = (100 - risk_score) / 100
        
        adjusted_probability = base_probability * risk_adjustment
        
        # Begrens til 0-100%
        return max(0, min(100, adjusted_probability))
    
    def _calculate_potential_return(self, overall_score, risk_score):
        """
        Beregner potensiell avkastning.
        
        Args:
            overall_score (float): Samlet score
            risk_score (float): Risikoscore
            
        Returns:
            float: Potensiell avkastning (%)
        """
        # Beregn basisavkastning basert på score
        if overall_score > 50:  # Kjøpsanbefaling
            base_return = (overall_score - 50) * 0.4
        else:  # Salgsanbefaling
            base_return = (50 - overall_score) * 0.4
        
        # Juster for risiko (høyere risiko gir høyere potensiell avkastning)
        risk_multiplier = 1 + (risk_score / 100)
        
        potential_return = base_return * risk_multiplier
        
        return potential_return
    
    def _generate_explanation(self, symbol, analysis, overall_score, recommendation, 
                             risk_score, success_probability, potential_return):
        """
        Genererer en forklaring på norsk for anbefalingen.
        
        Args:
            symbol (str): Aksjesymbol
            analysis (dict): Analyseresultater
            overall_score (float): Samlet score
            recommendation (str): Anbefaling (kjøp, selg, hold)
            risk_score (float): Risikoscore
            success_probability (float): Sannsynlighet for suksess
            potential_return (float): Potensiell avkastning
            
        Returns:
            str: Forklaring på norsk
        """
        # Oversett anbefaling til norsk
        if recommendation == 'buy':
            norsk_anbefaling = 'KJØP'
        elif recommendation == 'sell':
            norsk_anbefaling = 'SELG'
        else:
            norsk_anbefaling = 'HOLD'
        
        # Start forklaring
        explanation = f"**{norsk_anbefaling}**: {symbol}\n\n"
        
        # Legg til sammendrag
        if recommendation == 'buy':
            explanation += f"Analysen indikerer en kjøpsmulighet for {symbol} med en samlet score på {overall_score:.1f}/100. "
            explanation += f"Den estimerte sannsynligheten for suksess er {success_probability:.1f}% "
            explanation += f"med en potensiell avkastning på {potential_return:.1f}%. "
            explanation += f"Risikoscoren er {risk_score:.1f}/100 (høyere tall indikerer høyere risiko).\n\n"
        elif recommendation == 'sell':
            explanation += f"Analysen indikerer at {symbol} bør selges med en samlet score på {overall_score:.1f}/100. "
            explanation += f"Den estimerte sannsynligheten for suksess er {success_probability:.1f}% "
            explanation += f"med en potensiell gevinst på {potential_return:.1f}% ved å unngå tap. "
            explanation += f"Risikoscoren er {risk_score:.1f}/100 (høyere tall indikerer høyere risiko).\n\n"
        else:
            explanation += f"Analysen indikerer at {symbol} bør holdes med en nøytral score på {overall_score:.1f}/100. "
            explanation += f"Det er ikke tilstrekkelig signal for hverken kjøp eller salg på nåværende tidspunkt.\n\n"
        
        # Legg til teknisk analyse
        if 'technical' in analysis:
            technical = analysis['technical']
            explanation += "**Teknisk analyse**:\n"
            
            if 'recommendation' in technical:
                tech_rec = technical['recommendation']
                explanation += f"- Teknisk anbefaling: {tech_rec.upper()}\n"
            
            if 'signals' in technical:
                signals = technical['signals']
                
                if 'rsi' in signals:
                    rsi = signals['rsi']
                    explanation += f"- RSI: {rsi['value']:.1f} ({rsi['signal']})\n"
                
                if 'sma' in signals:
                    sma = signals['sma']
                    explanation += f"- SMA: Kort {sma['short']:.2f} vs Lang {sma['long']:.2f} ({sma['signal']})\n"
                
                if 'macd' in signals:
                    macd = signals['macd']
                    explanation += f"- MACD: {macd['signal']}\n"
                
                if 'volume' in signals:
                    volume = signals['volume']
                    explanation += f"- Volum: {volume['change']:.2f}x gjennomsnitt ({volume['signal']})\n"
            
            explanation += "\n"
        
        # Legg til fundamentalanalyse
        if 'fundamental' in analysis:
            fundamental = analysis['fundamental']
            explanation += "**Fundamental analyse**:\n"
            
            if 'metrics' in fundamental:
                metrics = fundamental['metrics']
                
                if 'pe_ratio' in metrics:
                    pe = metrics['pe_ratio']
                    explanation += f"- P/E-forhold: {pe['value']:.2f} - {pe['interpretation']}\n"
                
                if 'eps' in metrics:
                    eps = metrics['eps']
                    explanation += f"- EPS: {eps['value']:.2f} - {eps['interpretation']}\n"
                
                if 'revenue_growth' in metrics:
                    growth = metrics['revenue_growth']
                    explanation += f"- Inntektsvekst: {growth['value']*100:.1f}% - {growth['interpretation']}\n"
                
                if 'profit_margin' in metrics:
                    margin = metrics['profit_margin']
                    explanation += f"- Profittmargin: {margin['value']*100:.1f}% - {margin['interpretation']}\n"
            
            explanation += "\n"
        
        # Legg til nyhetsanalyse
        if 'news' in analysis and 'articles' in analysis['news'] and analysis['news']['articles']:
            news = analysis['news']
            explanation += "**Nyhetsanalyse**:\n"
            
            for article in news['articles'][:3]:  # Vis bare de 3 viktigste
                date_str = article['published_at'].split('T')[0]  # Forenklet datoformat
                explanation += f"- {date_str}: {article['title']} ({article['sentiment']})\n"
            
            explanation += "\n"
        
        # Legg til sentimentanalyse
        if 'sentiment' in analysis:
            sentiment = analysis['sentiment']
            explanation += "**Sentimentanalyse**:\n"
            
            if 'sentiment' in sentiment:
                if sentiment['sentiment'] == 'positive':
                    explanation += f"- Markedssentiment: Positivt ({sentiment['score']:.1f}/100)\n"
                elif sentiment['sentiment'] == 'negative':
                    explanation += f"- Markedssentiment: Negativt ({sentiment['score']:.1f}/100)\n"
                else:
                    explanation += f"- Markedssentiment: Nøytralt ({sentiment['score']:.1f}/100)\n"
            
            explanation += "\n"
        
        # Legg til konklusjon
        explanation += "**Konklusjon**:\n"
        if recommendation == 'buy':
            explanation += f"Basert på kombinasjonen av teknisk analyse, fundamentale data, nyheter og sentiment, "
            explanation += f"anbefales det å kjøpe {symbol} ved markedsåpning. "
            explanation += f"Husk at all handel innebærer risiko, og denne anbefalingen er basert på historiske data og nåværende markedsforhold."
        elif recommendation == 'sell':
            explanation += f"Basert på kombinasjonen av teknisk analyse, fundamentale data, nyheter og sentiment, "
            explanation += f"anbefales det å selge {symbol} ved markedsåpning. "
            explanation += f"Husk at all handel innebærer risiko, og denne anbefalingen er basert på historiske data og nåværende markedsforhold."
        else:
            explanation += f"Basert på kombinasjonen av teknisk analyse, fundamentale data, nyheter og sentiment, "
            explanation += f"anbefales det å holde {symbol} og overvåke utviklingen. "
            explanation += f"Det er ikke tilstrekkelig signal for hverken kjøp eller salg på nåværende tidspunkt."
        
        return explanation

