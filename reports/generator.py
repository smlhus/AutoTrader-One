# -*- coding: utf-8 -*-

"""
Rapportgeneratormodul for AutoTrader One.
"""

import logging
import os
from datetime import datetime

class ReportGenerator:
    """Klasse for å generere rapporter."""
    
    def __init__(self, config):
        """
        Initialiserer ReportGenerator.
        
        Args:
            config (dict): Applikasjonskonfigurasjon
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Hent konfigurasjon
        self.format = config.get('reporting', {}).get('format', 'markdown')
        self.output_dir = config.get('reporting', {}).get('output_dir', 'rapporter')
        
        # Opprett rapportkatalog hvis den ikke eksisterer
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_report(self, recommendations, date_str):
        """
        Genererer en rapport basert på anbefalinger.
        
        Args:
            recommendations (list): Handelsanbefalinger
            date_str (str): Datostrengen for rapporten
            
        Returns:
            str: Sti til den genererte rapporten
        """
        self.logger.info("Genererer rapport for %s med %d anbefalinger", date_str, len(recommendations))
        
        if self.format.lower() == 'markdown':
            return self._generate_markdown_report(recommendations, date_str)
        else:
            self.logger.warning("Ukjent rapportformat: %s. Bruker markdown.", self.format)
            return self._generate_markdown_report(recommendations, date_str)
    
    def _generate_markdown_report(self, recommendations, date_str):
        """
        Genererer en Markdown-rapport.
        
        Args:
            recommendations (list): Handelsanbefalinger
            date_str (str): Datostrengen for rapporten
            
        Returns:
            str: Sti til den genererte rapporten
        """
        # Opprett filnavn
        filename = os.path.join(self.output_dir, f"handelsanbefalinger_{date_str}.md")
        
        # Grupper anbefalinger
        buy_recommendations = [r for r in recommendations if r['recommendation'] == 'buy']
        sell_recommendations = [r for r in recommendations if r['recommendation'] == 'sell']
        hold_recommendations = [r for r in recommendations if r['recommendation'] == 'hold']
        
        # Generer rapportinnhold
        content = f"# AutoTrader One: Handelsanbefalinger for {date_str}\n\n"
        content += f"*Generert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        content += "## Sammendrag\n\n"
        content += f"- **Kjøpsanbefalinger:** {len(buy_recommendations)}\n"
        content += f"- **Salgsanbefalinger:** {len(sell_recommendations)}\n"
        content += f"- **Hold-anbefalinger:** {len(hold_recommendations)}\n\n"
        
        # Legg til kjøpsanbefalinger
        if buy_recommendations:
            content += "## Kjøpsanbefalinger\n\n"
            
            for rec in buy_recommendations:
                content += f"### {rec['symbol']}\n\n"
                content += f"- **Score:** {rec['overall_score']:.1f}/100\n"
                content += f"- **Risiko:** {rec['risk_score']:.1f}/100\n"
                content += f"- **Sannsynlighet for suksess:** {rec['success_probability']:.1f}%\n"
                content += f"- **Potensiell avkastning:** {rec['potential_return']:.1f}%\n\n"
                content += f"{rec['explanation']}\n\n"
                content += "---\n\n"
        
        # Legg til salgsanbefalinger
        if sell_recommendations:
            content += "## Salgsanbefalinger\n\n"
            
            for rec in sell_recommendations:
                content += f"### {rec['symbol']}\n\n"
                content += f"- **Score:** {rec['overall_score']:.1f}/100\n"
                content += f"- **Risiko:** {rec['risk_score']:.1f}/100\n"
                content += f"- **Sannsynlighet for suksess:** {rec['success_probability']:.1f}%\n"
                content += f"- **Potensiell avkastning:** {rec['potential_return']:.1f}%\n\n"
                content += f"{rec['explanation']}\n\n"
                content += "---\n\n"
        
        # Legg til hold-anbefalinger (forenklet)
        if hold_recommendations:
            content += "## Hold-anbefalinger\n\n"
            
            for rec in hold_recommendations:
                content += f"### {rec['symbol']}\n\n"
                content += f"- **Score:** {rec['overall_score']:.1f}/100\n"
                content += f"- **Risiko:** {rec['risk_score']:.1f}/100\n\n"
                content += f"{rec['explanation']}\n\n"
                content += "---\n\n"
        
        # Legg til ansvarsfraskrivelse
        content += "## Ansvarsfraskrivelse\n\n"
        content += "Dette er en automatisk generert rapport fra AutoTrader One. "
        content += "Anbefalingene er basert på historiske data og nåværende markedsforhold, "
        content += "og er ment som et beslutningsgrunnlag, ikke som finansiell rådgivning. "
        content += "All handel innebærer risiko, og du bør alltid gjøre din egen analyse før du handler. "
        content += "AutoTrader One og dets utviklere tar ikke ansvar for eventuelle tap som måtte oppstå "
        content += "som følge av handel basert på disse anbefalingene.\n"
        
        # Skriv til fil
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info("Rapport lagret til %s", filename)
        except Exception as e:
            self.logger.error("Feil ved lagring av rapport: %s", str(e))
            return None
        
        return filename

