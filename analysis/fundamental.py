# -*- coding: utf-8 -*-

"""
Fundamentalanalysemodul for AutoTrader One.
"""

import logging
import numpy as np

class FundamentalAnalyzer:
    """Klasse for fundamentalanalyse."""
    
    def __init__(self, config):
        """
        Initialiserer FundamentalAnalyzer.
        
        Args:
            config (dict): Applikasjonskonfigurasjon
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Hent konfigurasjon
        self.metrics = config.get('analysis', {}).get('fundamental', {}).get('metrics', 
                                                                           ['pe_ratio', 'eps', 'revenue_growth'])
    
    def analyze(self, fundamental_data):
        """
        Utfører fundamentalanalyse.
        
        Args:
            fundamental_data (dict): Fundamentale data
            
        Returns:
            dict: Fundamentalanalyseresultat
        """
        if not fundamental_data:
            self.logger.warning("Ingen fundamentale data å analysere")
            return {'score': 50, 'metrics': {}}
        
        symbol = fundamental_data.get('symbol', 'Ukjent')
        self.logger.info("Utfører fundamentalanalyse for %s", symbol)
        
        metrics_analysis = {}
        
        # Analyser P/E-forhold
        if 'pe_ratio' in self.metrics and 'pe_ratio' in fundamental_data:
            pe_ratio = fundamental_data['pe_ratio']
            
            # Vurder P/E-forhold (lavere er generelt bedre, men for lavt kan være et faresignal)
            if 5 <= pe_ratio <= 15:
                pe_score = 80  # Veldig bra
            elif 15 < pe_ratio <= 25:
                pe_score = 60  # Bra
            elif 25 < pe_ratio <= 35:
                pe_score = 40  # Middels
            elif pe_ratio > 35:
                pe_score = 20  # Høyt
            else:  # pe_ratio < 5
                pe_score = 30  # Mistenkelig lavt
            
            metrics_analysis['pe_ratio'] = {
                'value': pe_ratio,
                'score': pe_score,
                'interpretation': self._interpret_pe_ratio(pe_ratio)
            }
        
        # Analyser EPS
        if 'eps' in self.metrics and 'eps' in fundamental_data:
            eps = fundamental_data['eps']
            
            # Vurder EPS (høyere er generelt bedre)
            if eps <= 0:
                eps_score = 20  # Negativt
            elif 0 < eps <= 2:
                eps_score = 40  # Lavt
            elif 2 < eps <= 5:
                eps_score = 60  # Bra
            else:  # eps > 5
                eps_score = 80  # Veldig bra
            
            metrics_analysis['eps'] = {
                'value': eps,
                'score': eps_score,
                'interpretation': self._interpret_eps(eps)
            }
        
        # Analyser inntektsvekst
        if 'revenue_growth' in self.metrics and 'revenue_growth' in fundamental_data:
            revenue_growth = fundamental_data['revenue_growth']
            
            # Vurder inntektsvekst
            if revenue_growth < 0:
                growth_score = max(20, 50 + revenue_growth * 100)  # Negativ vekst
            elif 0 <= revenue_growth < 0.05:
                growth_score = 50  # Flat
            elif 0.05 <= revenue_growth < 0.1:
                growth_score = 60  # Moderat
            elif 0.1 <= revenue_growth < 0.2:
                growth_score = 75  # Bra
            else:  # revenue_growth >= 0.2
                growth_score = 90  # Veldig bra
            
            metrics_analysis['revenue_growth'] = {
                'value': revenue_growth,
                'score': growth_score,
                'interpretation': self._interpret_revenue_growth(revenue_growth)
            }
        
        # Analyser profittmargin
        if 'profit_margin' in self.metrics and 'profit_margin' in fundamental_data:
            profit_margin = fundamental_data['profit_margin']
            
            # Vurder profittmargin
            if profit_margin < 0:
                margin_score = 20  # Negativt
            elif 0 <= profit_margin < 0.05:
                margin_score = 40  # Lavt
            elif 0.05 <= profit_margin < 0.1:
                margin_score = 60  # Moderat
            elif 0.1 <= profit_margin < 0.2:
                margin_score = 80  # Bra
            else:  # profit_margin >= 0.2
                margin_score = 90  # Veldig bra
            
            metrics_analysis['profit_margin'] = {
                'value': profit_margin,
                'score': margin_score,
                'interpretation': self._interpret_profit_margin(profit_margin)
            }
        
        # Beregn samlet score
        if metrics_analysis:
            scores = [m['score'] for m in metrics_analysis.values()]
            overall_score = np.mean(scores)
        else:
            overall_score = 50
        
        return {
            'score': round(overall_score, 1),
            'metrics': metrics_analysis,
            'recommendation': 'buy' if overall_score > 60 else ('sell' if overall_score < 40 else 'hold')
        }
    
    def _interpret_pe_ratio(self, pe_ratio):
        """
        Tolker P/E-forhold.
        
        Args:
            pe_ratio (float): P/E-forhold
            
        Returns:
            str: Tolkning
        """
        if pe_ratio < 5:
            return "Svært lavt P/E-forhold kan indikere undervurdering eller problemer"
        elif 5 <= pe_ratio <= 15:
            return "Attraktivt P/E-forhold, potensielt undervurdert"
        elif 15 < pe_ratio <= 25:
            return "Moderat P/E-forhold, rimelig verdsatt"
        elif 25 < pe_ratio <= 35:
            return "Høyt P/E-forhold, potensielt overvurdert"
        else:  # pe_ratio > 35
            return "Svært høyt P/E-forhold, betydelig overvurdert eller høye vekstforventninger"
    
    def _interpret_eps(self, eps):
        """
        Tolker EPS.
        
        Args:
            eps (float): Earnings Per Share
            
        Returns:
            str: Tolkning
        """
        if eps <= 0:
            return "Negativ inntjening per aksje, selskapet er ikke lønnsomt"
        elif 0 < eps <= 2:
            return "Lav inntjening per aksje"
        elif 2 < eps <= 5:
            return "God inntjening per aksje"
        else:  # eps > 5
            return "Sterk inntjening per aksje"
    
    def _interpret_revenue_growth(self, growth):
        """
        Tolker inntektsvekst.
        
        Args:
            growth (float): Inntektsvekst
            
        Returns:
            str: Tolkning
        """
        if growth < 0:
            return f"Negativ inntektsvekst ({growth*100:.1f}%), bekymringsfullt"
        elif 0 <= growth < 0.05:
            return f"Flat inntektsvekst ({growth*100:.1f}%)"
        elif 0.05 <= growth < 0.1:
            return f"Moderat inntektsvekst ({growth*100:.1f}%)"
        elif 0.1 <= growth < 0.2:
            return f"Sterk inntektsvekst ({growth*100:.1f}%)"
        else:  # growth >= 0.2
            return f"Eksepsjonell inntektsvekst ({growth*100:.1f}%)"
    
    def _interpret_profit_margin(self, margin):
        """
        Tolker profittmargin.
        
        Args:
            margin (float): Profittmargin
            
        Returns:
            str: Tolkning
        """
        if margin < 0:
            return "Negativ profittmargin, selskapet er ikke lønnsomt"
        elif 0 <= margin < 0.05:
            return f"Lav  selskapet er ikke lønnsomt"
        elif 0 <= margin < 0.05:
            return f"Lav profittmargin ({margin*100:.1f}%)"
        elif 0.05 <= margin < 0.1:
            return f"Moderat profittmargin ({margin*100:.1f}%)"
        elif 0.1 <= margin < 0.2:
            return f"God profittmargin ({margin*100:.1f}%)"
        else:  # margin >= 0.2
            return f"Utmerket profittmargin ({margin*100:.1f}%)"

