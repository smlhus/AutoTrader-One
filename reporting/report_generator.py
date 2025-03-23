#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ReportGenerator for AutoTrader One.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml

class ReportGenerator:
    """Klasse for generering av handelsrapporter i AutoTrader One."""
    
    def __init__(self, config: Dict):
        """
        Initialiserer ReportGenerator.
        
        Args:
            config (Dict): Konfigurasjon for rapportgeneratoren
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Opprett rapportmappe hvis den ikke eksisterer
        self.report_dir = config.get('report_dir', 'rapporter')
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Hent konfigurasjon
        self.include_charts = config.get('include_charts', True)
        self.save_raw_data = config.get('save_raw_data', True)
        self.output_format = config.get('output_format', 'markdown')
    
    def generate_report(self, recommendations: List[Dict], metrics: Dict) -> str:
        """
        Genererer en handelsrapport.
        
        Args:
            recommendations (List[Dict]): Liste over handelsanbefalinger
            metrics (Dict): Porteføljemetrikker
            
        Returns:
            str: Filbane til generert rapport
        """
        try:
            # Opprett filnavn med tidsstempel
            timestamp = datetime.now().strftime('%Y-%m-%d')
            filename = f'handelsanbefalinger_{timestamp}.md'
            filepath = os.path.join(self.report_dir, filename)
            
            # Grupper anbefalinger etter type
            buy_recommendations = [r for r in recommendations if r['recommendation'] == 'buy']
            sell_recommendations = [r for r in recommendations if r['recommendation'] == 'sell']
            hold_recommendations = [r for r in recommendations if r['recommendation'] == 'hold']
            
            # Generer rapport
            with open(filepath, 'w', encoding='utf-8') as f:
                # Skriv header
                f.write('# Handelsanbefalinger\n\n')
                f.write(f'Generert: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
                
                # Skriv sammendrag
                f.write('## Sammendrag\n\n')
                f.write(f'- Antall kjøpsanbefalinger: {len(buy_recommendations)}\n')
                f.write(f'- Antall salgsanbefalinger: {len(sell_recommendations)}\n')
                f.write(f'- Antall holdeanbefalinger: {len(hold_recommendations)}\n\n')
                
                # Skriv porteføljemetrikker
                self._write_portfolio_metrics(f, metrics)
                
                # Skriv anbefalinger
                if buy_recommendations:
                    f.write('\n## Kjøpsanbefalinger\n\n')
                    for rec in buy_recommendations:
                        self._write_recommendation(f, rec)
                
                if sell_recommendations:
                    f.write('\n## Salgsanbefalinger\n\n')
                    for rec in sell_recommendations:
                        self._write_recommendation(f, rec)
                
                if hold_recommendations:
                    f.write('\n## Holdeanbefalinger\n\n')
                    for rec in hold_recommendations:
                        self._write_recommendation(f, rec)
                
                # Skriv disclaimer
                f.write('\n## Disclaimer\n\n')
                f.write('Dette er en automatisk generert rapport fra AutoTrader One. ')
                f.write('Anbefalingene er basert på teknisk analyse, fundamental analyse, ')
                f.write('nyhetsanalyse og markedssentiment. Dette er ikke finansiell ')
                f.write('rådgivning, og alle investeringsbeslutninger tas på eget ansvar. ')
                f.write('Det anbefales å gjøre egen analyse før handel.\n')
            
            # Lagre rådata hvis konfigurert
            if self.save_raw_data:
                self._save_raw_data(recommendations, metrics, timestamp)
            
            self.logger.info(f"Rapport generert: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Feil ved generering av rapport: {str(e)}")
            return ""
    
    def _write_portfolio_metrics(self, f, metrics: Dict) -> None:
        """
        Skriver porteføljemetrikker til rapporten.
        
        Args:
            f: Filhåndterer
            metrics (Dict): Porteføljemetrikker
        """
        f.write('## Porteføljemetrikker\n\n')
        
        # Skriv avkastning
        f.write('### Avkastning\n\n')
        f.write(f'- Daglig: {metrics["returns"]["daily"]}%\n')
        f.write(f'- Ukentlig: {metrics["returns"]["weekly"]}%\n')
        f.write(f'- Månedlig: {metrics["returns"]["monthly"]}%\n')
        f.write(f'- Årlig: {metrics["returns"]["yearly"]}%\n\n')
        
        # Skriv risikometrikker
        f.write('### Risiko\n\n')
        f.write(f'- Volatilitet: {metrics["risk"]["volatility"]}%\n')
        f.write(f'- Value at Risk (95%): {metrics["risk"]["var_95"]}%\n')
        f.write(f'- Maksimal Drawdown: {metrics["risk"]["max_drawdown"]}%\n\n')
        
        # Skriv prestasjonsmål
        f.write('### Prestasjonsmål\n\n')
        f.write(f'- Sharpe Ratio: {metrics["performance"]["sharpe_ratio"]}\n')
        f.write(f'- Sortino Ratio: {metrics["performance"]["sortino_ratio"]}\n')
        f.write(f'- Information Ratio: {metrics["performance"]["information_ratio"]}\n\n')
    
    def _write_recommendation(self, f, recommendation: Dict) -> None:
        """
        Skriver en enkelt anbefaling til rapporten.
        
        Args:
            f: Filhåndterer
            recommendation (Dict): Handelsanbefaling
        """
        symbol = recommendation['symbol']
        total_score = recommendation['total_score']
        risk_score = recommendation['risk_assessment']['risk_score']
        success_probability = recommendation['risk_assessment']['success_probability']
        potential_return = recommendation['risk_assessment']['potential_return']
        
        f.write(f'### {symbol}\n\n')
        f.write(f'**Total score: {total_score}/100**\n\n')
        f.write(f'**Risikoscore: {risk_score}/100**\n\n')
        f.write(f'**Suksessannsynlighet: {success_probability}%**\n\n')
        f.write(f'**Potensiell avkastning: {potential_return}%**\n\n')
        
        # Skriv teknisk analyse
        f.write('#### Teknisk Analyse\n\n')
        tech = recommendation['technical_analysis']
        f.write(f'- RSI: {tech.get("rsi", "N/A")} ({tech.get("rsi_signal", "N/A")})\n')
        f.write(f'- SMA: Kort {tech.get("sma_short", "N/A")} vs Lang {tech.get("sma_long", "N/A")} ({tech.get("sma_signal", "N/A")})\n')
        f.write(f'- MACD: {tech.get("macd_signal", "N/A")}\n')
        f.write(f'- Volum: {tech.get("volume_signal", "N/A")}\n\n')
        
        # Skriv fundamental analyse
        f.write('#### Fundamental Analyse\n\n')
        fund = recommendation['fundamental_analysis']
        for metric, data in fund.get('metrics', {}).items():
            f.write(f'- {data["description"]}: {data["value"]:.2f} ({data["signal"]})\n')
        f.write('\n')
        
        # Skriv nyhetsanalyse
        f.write('#### Nyhetsanalyse\n\n')
        for news in recommendation['sentiment_analysis'].get('news', []):
            f.write(f'- {news["date"]}: {news["title"]} ({news["sentiment"]})\n')
        f.write('\n')
        
        # Skriv sentimentanalyse
        f.write('#### Sentimentanalyse\n\n')
        sentiment = recommendation['sentiment_analysis']
        f.write(f'- Markedssentiment: {sentiment.get("market_sentiment", "N/A")}\n')
        f.write(f'- Nyhetssentiment: {sentiment.get("news_sentiment", "N/A")}\n')
        f.write(f'- Sosiale medier: {sentiment.get("social_sentiment", "N/A")}\n\n')
        
        # Skriv konklusjon
        f.write('#### Konklusjon\n\n')
        f.write(f'Basert på kombinasjonen av teknisk analyse (score: {tech.get("score", "N/A")}), ')
        f.write(f'fundamental analyse (score: {fund.get("score", "N/A")}), og ')
        f.write(f'sentimentanalyse (score: {sentiment.get("score", "N/A")}), ')
        f.write(f'anbefales det å {recommendation["recommendation"]} {symbol}. ')
        
        if recommendation['recommendation'] == 'hold':
            f.write('Det er ikke tilstrekkelig signal for hverken kjøp eller salg på nåværende tidspunkt.')
        elif recommendation['recommendation'] == 'buy':
            f.write(f'Potensiell oppside på {potential_return}% med {success_probability}% sannsynlighet.')
        else:
            f.write(f'Risiko for nedside på {potential_return}% med {success_probability}% sannsynlighet.')
        f.write('\n\n')
        
        # Legg til grafer hvis konfigurert
        if self.include_charts and 'charts' in recommendation:
            self._add_charts(recommendation['charts'], symbol)
    
    def _add_charts(self, charts: Dict, symbol: str) -> None:
        """
        Legger til grafer i rapporten.
        
        Args:
            charts (Dict): Grafdata
            symbol (str): Handelssymbol
        """
        try:
            # Opprett grafmappe hvis den ikke eksisterer
            chart_dir = os.path.join(self.report_dir, 'grafer')
            os.makedirs(chart_dir, exist_ok=True)
            
            # Generer prisutvikling
            if 'price_history' in charts:
                plt.figure(figsize=(12, 6))
                sns.lineplot(data=charts['price_history'])
                plt.title(f'Prisutvikling - {symbol}')
                plt.xlabel('Dato')
                plt.ylabel('Pris')
                plt.savefig(os.path.join(chart_dir, f'{symbol}_price.png'))
                plt.close()
            
            # Generer tekniske indikatorer
            if 'technical_indicators' in charts:
                plt.figure(figsize=(12, 6))
                for indicator, values in charts['technical_indicators'].items():
                    sns.lineplot(data=values, label=indicator)
                plt.title(f'Tekniske Indikatorer - {symbol}')
                plt.xlabel('Dato')
                plt.ylabel('Verdi')
                plt.legend()
                plt.savefig(os.path.join(chart_dir, f'{symbol}_indicators.png'))
                plt.close()
            
            # Generer volumanalyse
            if 'volume_analysis' in charts:
                plt.figure(figsize=(12, 4))
                sns.barplot(data=charts['volume_analysis'])
                plt.title(f'Volumanalyse - {symbol}')
                plt.xlabel('Dato')
                plt.ylabel('Volum')
                plt.savefig(os.path.join(chart_dir, f'{symbol}_volume.png'))
                plt.close()
            
        except Exception as e:
            self.logger.error(f"Feil ved generering av grafer for {symbol}: {str(e)}")
    
    def _save_raw_data(self, recommendations: List[Dict], metrics: Dict,
                      timestamp: str) -> None:
        """
        Lagrer rådata fra analysen.
        
        Args:
            recommendations (List[Dict]): Liste over handelsanbefalinger
            metrics (Dict): Porteføljemetrikker
            timestamp (str): Tidsstempel
        """
        try:
            # Opprett datamappe hvis den ikke eksisterer
            data_dir = os.path.join(self.report_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Lagre data som JSON
            data = {
                'recommendations': recommendations,
                'metrics': metrics,
                'timestamp': timestamp
            }
            
            filepath = os.path.join(data_dir, f'raw_data_{timestamp}.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True)
            
            self.logger.info(f"Rådata lagret: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Feil ved lagring av rådata: {str(e)}")
    
    def _format_number(self, number: float, decimals: int = 2) -> str:
        """
        Formaterer et tall med riktig antall desimaler.
        
        Args:
            number (float): Tall som skal formateres
            decimals (int): Antall desimaler
            
        Returns:
            str: Formatert tall
        """
        try:
            return f"{number:,.{decimals}f}"
        except Exception:
            return str(number) 