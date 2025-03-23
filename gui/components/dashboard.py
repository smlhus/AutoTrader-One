#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AutoTrader One GUI - Dashboard
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class DashboardFrame(ctk.CTkFrame):
    """Dashboard-ramme for AutoTrader One GUI."""
    
    def __init__(self, parent):
        """
        Initialiserer dashboard-rammen.
        
        Args:
            parent: Foreldrevinduet
        """
        super().__init__(parent)
        
        # Sett opp farger og design
        self.colors = {
            'background': '#1E293B',
            'text': '#FFFFFF',
            'text_secondary': '#A0AEC0',
            'accent_positive': '#4CAF50',
            'accent_negative': '#F44336',
            'accent_neutral': '#FFC107',
            'border': '#2A3A5C',
            'card_bg': '#1E293B',
            'hover': '#2D3748'
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
        """Setter opp layouten for dashboardet."""
        # Opprett oversiktskort
        self._create_overview_cards()
        
        # Opprett anbefalinger
        self._create_recommendations()
        
        # Opprett porteføljeutvikling
        self._create_portfolio_chart()
    
    def _create_overview_cards(self):
        """Oppretter oversiktskort."""
        # Oversiktsramme
        overview_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors['card_bg'],
            corner_radius=8
        )
        overview_frame.pack(fill="x", padx=20, pady=10)
        
        # Overskrift
        title = ctk.CTkLabel(
            overview_frame,
            text="Oversikt",
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        )
        title.pack(pady=10)
        
        # Kortramme
        cards_frame = ctk.CTkFrame(
            overview_frame,
            fg_color=self.colors['card_bg']
        )
        cards_frame.pack(fill="x", padx=10, pady=10)
        
        # Opprett kort
        self._create_stat_card(
            cards_frame,
            "Anbefalinger",
            "3",
            "Kjøp: 2 | Selg: 1",
            self.colors['accent_positive'],
            0
        )
        
        self._create_stat_card(
            cards_frame,
            "Porteføljeavkastning",
            "+12.5%",
            "Siste 30 dager",
            self.colors['accent_positive'],
            1
        )
        
        self._create_stat_card(
            cards_frame,
            "Risikoscore",
            "Medium",
            "Gjennomsnittlig risiko",
            self.colors['accent_neutral'],
            2
        )
        
        # Konfigurer kolonner
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)
    
    def _create_stat_card(self, parent, title, value, subtitle, color, column):
        """
        Oppretter et statistikkort.
        
        Args:
            parent: Foreldrerammen
            title (str): Korttittel
            value (str): Hovedverdi
            subtitle (str): Undertekst
            color (str): Farge for indikator
            column (int): Kolonneposisjon
        """
        # Kortramme
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors['card_bg'],
            corner_radius=8
        )
        card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        
        # Indikator
        indicator = ctk.CTkFrame(
            card,
            fg_color=color,
            corner_radius=4,
            width=4,
            height=40
        )
        indicator.pack(side="left", padx=10, pady=10)
        
        # Innhold
        content = ctk.CTkFrame(
            card,
            fg_color=self.colors['card_bg']
        )
        content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tittel
        title_label = ctk.CTkLabel(
            content,
            text=title,
            font=self.fonts['body'],
            text_color=self.colors['text_secondary']
        )
        title_label.pack(anchor="w")
        
        # Verdi
        value_label = ctk.CTkLabel(
            content,
            text=value,
            font=self.fonts['metrics'],
            text_color=self.colors['text']
        )
        value_label.pack(anchor="w")
        
        # Undertekst
        subtitle_label = ctk.CTkLabel(
            content,
            text=subtitle,
            font=self.fonts['body'],
            text_color=self.colors['text_secondary']
        )
        subtitle_label.pack(anchor="w")
    
    def _create_recommendations(self):
        """Oppretter anbefalingsseksjonen."""
        # Anbefalingsramme
        recommendations_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors['card_bg'],
            corner_radius=8
        )
        recommendations_frame.pack(fill="x", padx=20, pady=10)
        
        # Overskrift
        title = ctk.CTkLabel(
            recommendations_frame,
            text="Topp anbefalinger",
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        )
        title.pack(pady=10)
        
        # Ramme for anbefalingskort
        cards_frame = ctk.CTkFrame(recommendations_frame)
        cards_frame.pack(fill="x", padx=10, pady=10)
        
        # Anbefalingskort
        self._create_recommendation_card(
            cards_frame,
            "EQNR.OL",
            "Kjøp",
            "+5.2%",
            "Medium",
            self.colors['accent_positive'],
            0
        )
        
        self._create_recommendation_card(
            cards_frame,
            "DNB.OL",
            "Selg",
            "-2.1%",
            "Høy",
            self.colors['accent_negative'],
            1
        )
        
        self._create_recommendation_card(
            cards_frame,
            "TEL.OL",
            "Hold",
            "+0.8%",
            "Lav",
            self.colors['accent_neutral'],
            2
        )
        
        # Konfigurer kolonner
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)
    
    def _create_recommendation_card(self, parent, symbol, action, change, risk, color, column):
        """
        Oppretter et anbefalingskort.
        
        Args:
            parent: Foreldrerammen
            symbol (str): Aksjesymbol
            action (str): Anbefaling
            change (str): Endring
            risk (str): Risikonivå
            color (str): Farge for indikator
            column (int): Kolonneposisjon
        """
        # Kortramme
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors['card_bg'],
            corner_radius=8
        )
        card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        
        # Symbol og anbefaling
        header = ctk.CTkFrame(
            card,
            fg_color=self.colors['card_bg']
        )
        header.pack(fill="x", padx=10, pady=5)
        
        symbol_label = ctk.CTkLabel(
            header,
            text=symbol,
            font=self.fonts['metrics'],
            text_color=self.colors['text']
        )
        symbol_label.pack(side="left")
        
        action_label = ctk.CTkLabel(
            header,
            text=action,
            font=self.fonts['body'],
            text_color=color
        )
        action_label.pack(side="right")
        
        # Mini-graf
        self._create_mini_chart(card, color)
        
        # Metadata
        metadata = ctk.CTkFrame(
            card,
            fg_color=self.colors['card_bg']
        )
        metadata.pack(fill="x", padx=10, pady=5)
        
        change_label = ctk.CTkLabel(
            metadata,
            text=f"Endring: {change}",
            font=self.fonts['body'],
            text_color=color
        )
        change_label.pack(side="left")
        
        risk_label = ctk.CTkLabel(
            metadata,
            text=f"Risiko: {risk}",
            font=self.fonts['body'],
            text_color=self.colors['text_secondary']
        )
        risk_label.pack(side="right")
    
    def _create_mini_chart(self, parent, color):
        """
        Oppretter en mini-graf for anbefalingskortet.
        
        Args:
            parent: Foreldrerammen
            color (str): Linjefarge
        """
        # Opprett figur
        fig = Figure(figsize=(3, 1), facecolor=self.colors['card_bg'])
        ax = fig.add_subplot(111)
        
        # Generer eksempeldata
        x = np.linspace(0, 10, 100)
        y = np.sin(x) + np.random.normal(0, 0.1, 100)
        
        # Tegn graf
        ax.plot(x, y, color=color, linewidth=2)
        ax.fill_between(x, y, alpha=0.2, color=color)
        
        # Fjern akser og rutenett
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        # Legg til i vinduet
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=5)
    
    def _create_portfolio_chart(self):
        """Oppretter porteføljeutviklingsgrafen."""
        # Porteføljeramme
        portfolio_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors['card_bg'],
            corner_radius=8
        )
        portfolio_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Overskrift
        title = ctk.CTkLabel(
            portfolio_frame,
            text="Porteføljeutvikling",
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        )
        title.pack(pady=10)
        
        # Opprett hovedgraf
        self._create_main_chart(portfolio_frame)
    
    def _create_main_chart(self, parent):
        """
        Oppretter hovedgrafen for porteføljeutvikling.
        
        Args:
            parent: Foreldrerammen
        """
        # Opprett figur
        fig = Figure(figsize=(8, 4), facecolor=self.colors['card_bg'])
        ax = fig.add_subplot(111)
        
        # Generer eksempeldata
        x = np.linspace(0, 30, 100)
        y = np.exp(x/30) + np.random.normal(0, 0.1, 100)
        
        # Tegn graf
        ax.plot(x, y, color=self.colors['accent_positive'], linewidth=2)
        ax.fill_between(x, y, alpha=0.2, color=self.colors['accent_positive'])
        
        # Sett opp akser
        ax.set_facecolor(self.colors['card_bg'])
        ax.grid(True, color=self.colors['border'], alpha=0.2)
        ax.tick_params(colors=self.colors['text_secondary'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color(self.colors['border'])
        ax.spines['left'].set_color(self.colors['border'])
        
        # Legg til i vinduet
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10) 