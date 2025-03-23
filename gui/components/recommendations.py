#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AutoTrader One GUI - Anbefalingsramme
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from typing import Dict, List, Optional

class RecommendationsFrame(ctk.CTkFrame):
    """Anbefalingsramme for AutoTrader One GUI."""
    
    def __init__(self, parent: ctk.CTk):
        """
        Initialiserer anbefalingsrammen.
        
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
        """Setter opp anbefalingslayouten."""
        # Sett bakgrunnsfarge
        self.configure(fg_color=self.colors['background'])
        
        # Opprett filterpanel
        self._create_filter_panel()
        
        # Opprett anbefalingsliste
        self._create_recommendations_list()
        
        # Opprett detaljvisning
        self._create_details_panel()
    
    def _create_filter_panel(self):
        """Oppretter filterpanel for anbefalinger."""
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        # Anbefalingstype
        type_frame = ctk.CTkFrame(filter_frame)
        type_frame.pack(side="left", padx=10)
        
        type_label = ctk.CTkLabel(
            type_frame,
            text="Type:",
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        type_label.pack(side="left", padx=5)
        
        self.type_var = ctk.StringVar(value="Alle")
        for type_ in ["Alle", "Kjøp", "Selg", "Hold"]:
            ctk.CTkRadioButton(
                type_frame,
                text=type_,
                variable=self.type_var,
                value=type_,
                command=self._filter_recommendations
            ).pack(side="left", padx=5)
        
        # Risikoscore
        risk_frame = ctk.CTkFrame(filter_frame)
        risk_frame.pack(side="left", padx=10)
        
        risk_label = ctk.CTkLabel(
            risk_frame,
            text="Risiko:",
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        risk_label.pack(side="left", padx=5)
        
        self.risk_var = ctk.StringVar(value="Alle")
        for risk in ["Alle", "Lav", "Medium", "Høy"]:
            ctk.CTkRadioButton(
                risk_frame,
                text=risk,
                variable=self.risk_var,
                value=risk,
                command=self._filter_recommendations
            ).pack(side="left", padx=5)
        
        # Søk
        search_frame = ctk.CTkFrame(filter_frame)
        search_frame.pack(side="right", padx=10)
        
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Søk etter symbol...",
            textvariable=self.search_var,
            width=200
        )
        search_entry.pack(side="left", padx=5)
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Søk",
            command=self._filter_recommendations
        )
        search_button.pack(side="left", padx=5)
    
    def _create_recommendations_list(self):
        """Oppretter liste over anbefalinger."""
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Overskrift
        header_frame = ctk.CTkFrame(list_frame)
        header_frame.pack(fill="x", pady=5)
        
        headers = ["Symbol", "Anbefaling", "Risiko", "Avkastning", "Score"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=self.fonts['body'],
                text_color=self.colors['text']
            ).pack(side="left", expand=True, padx=5)
        
        # Anbefalingsliste
        self.recommendations_list = ctk.CTkScrollableFrame(list_frame)
        self.recommendations_list.pack(fill="both", expand=True, pady=5)
        
        # Eksempeldata
        self._add_recommendation("EQNR.OL", "Kjøp", "Lav", "+2.5%", "85")
        self._add_recommendation("DNB.OL", "Hold", "Medium", "-0.5%", "65")
        self._add_recommendation("TEL.OL", "Selg", "Høy", "-1.2%", "45")
    
    def _create_details_panel(self):
        """Oppretter detaljvisning for valgt anbefaling."""
        details_frame = ctk.CTkFrame(self)
        details_frame.pack(fill="x", padx=20, pady=10)
        
        # Overskrift
        title_label = ctk.CTkLabel(
            details_frame,
            text="Detaljer",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=10)
        
        # Detaljer
        details_grid = ctk.CTkFrame(details_frame)
        details_grid.pack(fill="x", padx=20, pady=10)
        
        # Tekniske indikatorer
        self._create_technical_indicators(details_grid)
        
        # Fundamentale data
        self._create_fundamental_data(details_grid)
        
        # Sentiment
        self._create_sentiment_data(details_grid)
    
    def _add_recommendation(self, symbol: str, recommendation: str, 
                          risk: str, return_: str, score: str):
        """
        Legger til en anbefaling i listen.
        
        Args:
            symbol (str): Aksjesymbol
            recommendation (str): Anbefaling
            risk (str): Risikoscore
            return_ (str): Forventet avkastning
            score (str): Totalscore
        """
        row = ctk.CTkFrame(self.recommendations_list)
        row.pack(fill="x", pady=2)
        
        # Symbol
        symbol_label = ctk.CTkLabel(
            row,
            text=symbol,
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        symbol_label.pack(side="left", expand=True, padx=5)
        
        # Anbefaling
        rec_color = {
            "Kjøp": self.colors['accent_positive'],
            "Selg": self.colors['accent_negative'],
            "Hold": self.colors['accent_neutral']
        }[recommendation]
        
        rec_label = ctk.CTkLabel(
            row,
            text=recommendation,
            font=self.fonts['body'],
            text_color=rec_color
        )
        rec_label.pack(side="left", expand=True, padx=5)
        
        # Risiko
        risk_label = ctk.CTkLabel(
            row,
            text=risk,
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        risk_label.pack(side="left", expand=True, padx=5)
        
        # Avkastning
        return_label = ctk.CTkLabel(
            row,
            text=return_,
            font=self.fonts['body'],
            text_color=self.colors['accent_positive'] if return_.startswith("+") 
                      else self.colors['accent_negative']
        )
        return_label.pack(side="left", expand=True, padx=5)
        
        # Score
        score_label = ctk.CTkLabel(
            row,
            text=score,
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        score_label.pack(side="left", expand=True, padx=5)
        
        # Klikkbar
        row.bind("<Button-1>", lambda e: self._show_details(symbol))
    
    def _create_technical_indicators(self, parent: ctk.CTkFrame):
        """Oppretter visning av tekniske indikatorer."""
        indicators_frame = ctk.CTkFrame(parent)
        indicators_frame.pack(fill="x", pady=5)
        
        # Overskrift
        title_label = ctk.CTkLabel(
            indicators_frame,
            text="Tekniske Indikatorer",
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=5)
        
        # Indikatorer
        indicators = [
            ("RSI", "65.2"),
            ("MACD", "0.8"),
            ("SMA 20", "150.3"),
            ("SMA 50", "148.9")
        ]
        
        for name, value in indicators:
            self._create_indicator_row(indicators_frame, name, value)
    
    def _create_fundamental_data(self, parent: ctk.CTkFrame):
        """Oppretter visning av fundamentale data."""
        fundamental_frame = ctk.CTkFrame(parent)
        fundamental_frame.pack(fill="x", pady=5)
        
        # Overskrift
        title_label = ctk.CTkLabel(
            fundamental_frame,
            text="Fundamentale Data",
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=5)
        
        # Data
        data = [
            ("P/E", "12.5"),
            ("P/B", "1.8"),
            ("Dividende", "4.2%"),
            ("ROE", "15.3%")
        ]
        
        for name, value in data:
            self._create_indicator_row(fundamental_frame, name, value)
    
    def _create_sentiment_data(self, parent: ctk.CTkFrame):
        """Oppretter visning av sentimentdata."""
        sentiment_frame = ctk.CTkFrame(parent)
        sentiment_frame.pack(fill="x", pady=5)
        
        # Overskrift
        title_label = ctk.CTkLabel(
            sentiment_frame,
            text="Sentiment",
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=5)
        
        # Sentimentindikator
        sentiment_value = 0.7
        sentiment_color = self.colors['accent_positive'] if sentiment_value > 0.5 \
                         else self.colors['accent_negative']
        
        sentiment_label = ctk.CTkLabel(
            sentiment_frame,
            text=f"Sentiment: {sentiment_value:.2f}",
            font=self.fonts['body'],
            text_color=sentiment_color
        )
        sentiment_label.pack(pady=5)
        
        # Sentimentgraf
        self._create_sentiment_chart(sentiment_frame)
    
    def _create_indicator_row(self, parent: ctk.CTkFrame, name: str, value: str):
        """
        Oppretter en indikatorrad.
        
        Args:
            parent (ctk.CTkFrame): Foreldreramme
            name (str): Indikatortittel
            value (str): Indikatorverdi
        """
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", pady=2)
        
        name_label = ctk.CTkLabel(
            row,
            text=name,
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        name_label.pack(side="left", padx=5)
        
        value_label = ctk.CTkLabel(
            row,
            text=value,
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        value_label.pack(side="right", padx=5)
    
    def _create_sentiment_chart(self, parent: ctk.CTkFrame):
        """Oppretter sentimentgraf."""
        fig = Figure(figsize=(6, 2), dpi=100)
        ax = fig.add_subplot(111)
        
        # Eksempeldata
        days = ["Man", "Tir", "Ons", "Tors", "Fre"]
        sentiment = [0.6, 0.7, 0.5, 0.8, 0.7]
        
        ax.plot(days, sentiment, color=self.colors['accent_positive'])
        ax.fill_between(days, sentiment, alpha=0.2, color=self.colors['accent_positive'])
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=5)
    
    def _filter_recommendations(self):
        """Filtrerer anbefalinger basert på valgte kriterier."""
        # TODO: Implementer filtrering
        pass
    
    def _show_details(self, symbol: str):
        """
        Viser detaljer for valgt symbol.
        
        Args:
            symbol (str): Aksjesymbol
        """
        # TODO: Implementer detaljvisning
        pass 