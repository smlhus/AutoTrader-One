#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AutoTrader One GUI - Analyseramme
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from typing import Dict, List, Optional

class AnalysisFrame(ctk.CTkFrame):
    """Analyseramme for AutoTrader One GUI."""
    
    def __init__(self, parent: ctk.CTk):
        """
        Initialiserer analyserammen.
        
        Args:
            parent (ctk.CTk): Foreldrevindu
        """
        super().__init__(parent)
        
        # Sett opp farger
        self.colors = {
            'background': '#1E2A3B',
            'text': '#FFFFFF',
            'accent_positive': '#4CAF50',
            'accent_negative': '#F44336',
            'accent_neutral': '#FFC107'
        }
        
        # Sett opp fonter
        self.fonts = {
            'heading': ('Inter', 24, 'bold'),
            'subheading': ('Inter', 18, 'normal'),
            'body': ('Inter', 14, 'normal'),
            'metrics': ('Roboto Mono', 16, 'normal')
        }
        
        # Sett opp layout
        self._setup_layout()
    
    def _setup_layout(self):
        """Setter opp analyselayouten."""
        # Sett bakgrunnsfarge
        self.configure(fg_color=self.colors['background'])
        
        # Opprett symbolvelger
        self._create_symbol_selector()
        
        # Opprett analysepaneler
        self._create_analysis_panels()
    
    def _create_symbol_selector(self):
        """Oppretter symbolvelger."""
        selector_frame = ctk.CTkFrame(self)
        selector_frame.pack(fill="x", padx=20, pady=10)
        
        # Symbolvelger
        symbol_frame = ctk.CTkFrame(selector_frame)
        symbol_frame.pack(side="left", padx=10)
        
        symbol_label = ctk.CTkLabel(
            symbol_frame,
            text="Symbol:",
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        symbol_label.pack(side="left", padx=5)
        
        self.symbol_var = ctk.StringVar(value="EQNR.OL")
        symbol_menu = ctk.CTkOptionMenu(
            symbol_frame,
            values=["EQNR.OL", "DNB.OL", "TEL.OL", "AKRBP.OL"],
            variable=self.symbol_var,
            command=self._update_analysis
        )
        symbol_menu.pack(side="left", padx=5)
        
        # Tidsperiode
        period_frame = ctk.CTkFrame(selector_frame)
        period_frame.pack(side="left", padx=10)
        
        period_label = ctk.CTkLabel(
            period_frame,
            text="Periode:",
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        period_label.pack(side="left", padx=5)
        
        self.period_var = ctk.StringVar(value="1M")
        period_menu = ctk.CTkOptionMenu(
            period_frame,
            values=["1D", "1U", "1M", "3M", "6M", "1Å", "5Å"],
            variable=self.period_var,
            command=self._update_analysis
        )
        period_menu.pack(side="left", padx=5)
        
        # Oppdateringsknapp
        update_button = ctk.CTkButton(
            selector_frame,
            text="Oppdater",
            command=self._update_analysis
        )
        update_button.pack(side="right", padx=10)
    
    def _create_analysis_panels(self):
        """Oppretter analysepaneler."""
        # Hovedpanel for analyser
        main_panel = ctk.CTkFrame(self)
        main_panel.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Teknisk analyse
        self._create_technical_analysis(main_panel)
        
        # Fundamental analyse
        self._create_fundamental_analysis(main_panel)
        
        # Sentimentanalyse
        self._create_sentiment_analysis(main_panel)
    
    def _create_technical_analysis(self, parent: ctk.CTkFrame):
        """Oppretter teknisk analysepanel."""
        technical_frame = ctk.CTkFrame(parent)
        technical_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Overskrift
        title_label = ctk.CTkLabel(
            technical_frame,
            text="Teknisk Analyse",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=10)
        
        # Prisgraf
        self._create_price_chart(technical_frame)
        
        # Indikatorer
        self._create_technical_indicators(technical_frame)
    
    def _create_fundamental_analysis(self, parent: ctk.CTkFrame):
        """Oppretter fundamental analysepanel."""
        fundamental_frame = ctk.CTkFrame(parent)
        fundamental_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Overskrift
        title_label = ctk.CTkLabel(
            fundamental_frame,
            text="Fundamental Analyse",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=10)
        
        # Nøkkeltall
        self._create_key_metrics(fundamental_frame)
        
        # Finansiell analyse
        self._create_financial_analysis(fundamental_frame)
    
    def _create_sentiment_analysis(self, parent: ctk.CTkFrame):
        """Oppretter sentimentanalysepanel."""
        sentiment_frame = ctk.CTkFrame(parent)
        sentiment_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Overskrift
        title_label = ctk.CTkLabel(
            sentiment_frame,
            text="Sentimentanalyse",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=10)
        
        # Sentimentindikatorer
        self._create_sentiment_indicators(sentiment_frame)
        
        # Nyhetsanalyse
        self._create_news_analysis(sentiment_frame)
    
    def _create_price_chart(self, parent: ctk.CTkFrame):
        """Oppretter prisgraf."""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Graf
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Eksempeldata
        days = ["Man", "Tir", "Ons", "Tors", "Fre"]
        prices = [150.0, 152.5, 151.8, 153.2, 152.9]
        
        ax.plot(days, prices, color=self.colors['accent_positive'])
        ax.fill_between(days, prices, alpha=0.2, color=self.colors['accent_positive'])
        ax.set_title("Prisutvikling")
        ax.set_xlabel("Dager")
        ax.set_ylabel("Pris")
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _create_technical_indicators(self, parent: ctk.CTkFrame):
        """Oppretter tekniske indikatorer."""
        indicators_frame = ctk.CTkFrame(parent)
        indicators_frame.pack(fill="x", padx=20, pady=10)
        
        # RSI
        self._create_indicator_chart(
            indicators_frame,
            "RSI",
            [65.2, 68.5, 62.3, 70.1, 67.8],
            self.colors['accent_neutral']
        )
        
        # MACD
        self._create_indicator_chart(
            indicators_frame,
            "MACD",
            [0.8, 1.2, 0.5, 1.5, 1.1],
            self.colors['accent_positive']
        )
    
    def _create_key_metrics(self, parent: ctk.CTkFrame):
        """Oppretter nøkkeltall."""
        metrics_frame = ctk.CTkFrame(parent)
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        # Nøkkeltall
        metrics = [
            ("P/E", "12.5", "15.2"),
            ("P/B", "1.8", "2.1"),
            ("Dividende", "4.2%", "3.8%"),
            ("ROE", "15.3%", "14.2%")
        ]
        
        for name, value, benchmark in metrics:
            self._create_metric_row(metrics_frame, name, value, benchmark)
    
    def _create_financial_analysis(self, parent: ctk.CTkFrame):
        """Oppretter finansiell analyse."""
        analysis_frame = ctk.CTkFrame(parent)
        analysis_frame.pack(fill="x", padx=20, pady=10)
        
        # Finansiell analyse
        self._create_financial_chart(analysis_frame)
    
    def _create_sentiment_indicators(self, parent: ctk.CTkFrame):
        """Oppretter sentimentindikatorer."""
        indicators_frame = ctk.CTkFrame(parent)
        indicators_frame.pack(fill="x", padx=20, pady=10)
        
        # Sentimentindikator
        self._create_sentiment_chart(indicators_frame)
        
        # Sentimenttrend
        self._create_sentiment_trend(indicators_frame)
    
    def _create_news_analysis(self, parent: ctk.CTkFrame):
        """Oppretter nyhetsanalyse."""
        news_frame = ctk.CTkFrame(parent)
        news_frame.pack(fill="x", padx=20, pady=10)
        
        # Nyhetsliste
        self._create_news_list(news_frame)
    
    def _create_indicator_chart(self, parent: ctk.CTkFrame, name: str, 
                              values: List[float], color: str):
        """
        Oppretter en indikatorgraf.
        
        Args:
            parent (ctk.CTkFrame): Foreldreramme
            name (str): Indikatortittel
            values (List[float]): Indikatorverdier
            color (str): Fargekode
        """
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.pack(side="left", expand=True, padx=5)
        
        # Tittel
        title_label = ctk.CTkLabel(
            chart_frame,
            text=name,
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=5)
        
        # Graf
        fig = Figure(figsize=(4, 2), dpi=100)
        ax = fig.add_subplot(111)
        
        days = ["Man", "Tir", "Ons", "Tors", "Fre"]
        ax.plot(days, values, color=color)
        ax.fill_between(days, values, alpha=0.2, color=color)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _create_metric_row(self, parent: ctk.CTkFrame, name: str, 
                          value: str, benchmark: str):
        """
        Oppretter en metrikkrad.
        
        Args:
            parent (ctk.CTkFrame): Foreldreramme
            name (str): Metrikktittel
            value (str): Metrikkverdi
            benchmark (str): Sammenligningsverdi
        """
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", pady=2)
        
        # Tittel
        name_label = ctk.CTkLabel(
            row,
            text=name,
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        name_label.pack(side="left", padx=5)
        
        # Verdi
        value_label = ctk.CTkLabel(
            row,
            text=value,
            font=self.fonts['metrics'],
            text_color=self.colors['text']
        )
        value_label.pack(side="left", padx=5)
        
        # Sammenligning
        benchmark_label = ctk.CTkLabel(
            row,
            text=f"Sektor: {benchmark}",
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        benchmark_label.pack(side="right", padx=5)
    
    def _create_financial_chart(self, parent: ctk.CTkFrame):
        """Oppretter finansiell analysegraf."""
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Eksempeldata
        years = ["2019", "2020", "2021", "2022", "2023"]
        revenue = [100, 95, 105, 110, 115]
        profit = [20, 15, 25, 30, 35]
        
        ax.plot(years, revenue, label="Inntekter", color=self.colors['accent_positive'])
        ax.plot(years, profit, label="Resultat", color=self.colors['accent_neutral'])
        ax.set_title("Finansiell Utvikling")
        ax.set_xlabel("År")
        ax.set_ylabel("Millioner")
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _create_sentiment_chart(self, parent: ctk.CTkFrame):
        """Oppretter sentimentgraf."""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.pack(side="left", expand=True, padx=5)
        
        # Tittel
        title_label = ctk.CTkLabel(
            chart_frame,
            text="Sentiment",
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=5)
        
        # Graf
        fig = Figure(figsize=(4, 2), dpi=100)
        ax = fig.add_subplot(111)
        
        days = ["Man", "Tir", "Ons", "Tors", "Fre"]
        sentiment = [0.6, 0.7, 0.5, 0.8, 0.7]
        
        ax.plot(days, sentiment, color=self.colors['accent_positive'])
        ax.fill_between(days, sentiment, alpha=0.2, color=self.colors['accent_positive'])
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _create_sentiment_trend(self, parent: ctk.CTkFrame):
        """Oppretter sentimenttrend."""
        trend_frame = ctk.CTkFrame(parent)
        trend_frame.pack(side="left", expand=True, padx=5)
        
        # Tittel
        title_label = ctk.CTkLabel(
            trend_frame,
            text="Sentimenttrend",
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=5)
        
        # Trendindikator
        trend_value = 0.7
        trend_color = self.colors['accent_positive'] if trend_value > 0.5 \
                      else self.colors['accent_negative']
        
        trend_label = ctk.CTkLabel(
            trend_frame,
            text=f"Trend: {trend_value:.2f}",
            font=self.fonts['body'],
            text_color=trend_color
        )
        trend_label.pack(pady=5)
    
    def _create_news_list(self, parent: ctk.CTkFrame):
        """Oppretter nyhetsliste."""
        # Nyhetsliste
        news_list = ctk.CTkScrollableFrame(parent)
        news_list.pack(fill="both", expand=True, pady=5)
        
        # Eksempelnyheter
        news_items = [
            ("Positive nyheter", self.colors['accent_positive']),
            ("Negative nyheter", self.colors['accent_negative']),
            ("Nøytrale nyheter", self.colors['accent_neutral'])
        ]
        
        for title, color in news_items:
            self._create_news_item(news_list, title, color)
    
    def _create_news_item(self, parent: ctk.CTkFrame, title: str, color: str):
        """
        Oppretter et nyhetselement.
        
        Args:
            parent (ctk.CTkFrame): Foreldreramme
            title (str): Nyhetstittel
            color (str): Fargekode
        """
        item = ctk.CTkFrame(parent)
        item.pack(fill="x", pady=2)
        
        # Tittel
        title_label = ctk.CTkLabel(
            item,
            text=title,
            font=self.fonts['body'],
            text_color=color
        )
        title_label.pack(side="left", padx=5)
        
        # Dato
        date_label = ctk.CTkLabel(
            item,
            text="2024-03-23",
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        date_label.pack(side="right", padx=5)
    
    def _update_analysis(self, *args):
        """Oppdaterer analysene."""
        # TODO: Implementer oppdatering av analyser
        pass 