#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AutoTrader One GUI - Innstillingsramme
"""

import customtkinter as ctk
import json
import os
from typing import Dict, List, Optional

class SettingsFrame(ctk.CTkFrame):
    """Innstillingsramme for AutoTrader One GUI."""
    
    def __init__(self, parent: ctk.CTk):
        """
        Initialiserer innstillingsrammen.
        
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
        
        # Last inn innstillinger
        self._load_settings()
    
    def _setup_layout(self):
        """Setter opp innstillingslayouten."""
        # Sett bakgrunnsfarge
        self.configure(fg_color=self.colors['background'])
        
        # Opprett innstillingspaneler
        self._create_api_settings()
        self._create_analysis_settings()
        self._create_risk_settings()
        self._create_notification_settings()
        
        # Opprett lagreknapp
        self._create_save_button()
    
    def _create_api_settings(self):
        """Oppretter API-innstillinger."""
        api_frame = ctk.CTkFrame(self)
        api_frame.pack(fill="x", padx=20, pady=10)
        
        # Overskrift
        title_label = ctk.CTkLabel(
            api_frame,
            text="API-innstillinger",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=10)
        
        # Alpha Vantage
        self._create_api_field(
            api_frame,
            "Alpha Vantage API-nøkkel:",
            "alpha_vantage_key",
            "Skriv inn API-nøkkel for Alpha Vantage"
        )
        
        # Financial Modeling Prep
        self._create_api_field(
            api_frame,
            "Financial Modeling Prep API-nøkkel:",
            "fmp_key",
            "Skriv inn API-nøkkel for Financial Modeling Prep"
        )
        
        # NewsAPI
        self._create_api_field(
            api_frame,
            "NewsAPI API-nøkkel:",
            "newsapi_key",
            "Skriv inn API-nøkkel for NewsAPI"
        )
    
    def _create_analysis_settings(self):
        """Oppretter analyseinnstillinger."""
        analysis_frame = ctk.CTkFrame(self)
        analysis_frame.pack(fill="x", padx=20, pady=10)
        
        # Overskrift
        title_label = ctk.CTkLabel(
            analysis_frame,
            text="Analyseinnstillinger",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=10)
        
        # Tekniske indikatorer
        self._create_checkbox_group(
            analysis_frame,
            "Tekniske indikatorer:",
            "technical_indicators",
            ["RSI", "MACD", "SMA", "EMA", "Bollinger Bands"]
        )
        
        # Fundamentale data
        self._create_checkbox_group(
            analysis_frame,
            "Fundamentale data:",
            "fundamental_data",
            ["P/E", "P/B", "Dividende", "ROE", "Debt/Equity"]
        )
        
        # Sentimentanalyse
        self._create_checkbox_group(
            analysis_frame,
            "Sentimentanalyse:",
            "sentiment_analysis",
            ["Nyhetsanalyse", "Sosiale medier", "Markedssentiment"]
        )
    
    def _create_risk_settings(self):
        """Oppretter risikoinntillinger."""
        risk_frame = ctk.CTkFrame(self)
        risk_frame.pack(fill="x", padx=20, pady=10)
        
        # Overskrift
        title_label = ctk.CTkLabel(
            risk_frame,
            text="Risikoinntillinger",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=10)
        
        # Maksimal posisjonsstørrelse
        self._create_slider_field(
            risk_frame,
            "Maksimal posisjonsstørrelse (%):",
            "max_position_size",
            0,
            100,
            20
        )
        
        # Stop-loss
        self._create_slider_field(
            risk_frame,
            "Stop-loss (%):",
            "stop_loss",
            0,
            20,
            5
        )
        
        # Take-profit
        self._create_slider_field(
            risk_frame,
            "Take-profit (%):",
            "take_profit",
            0,
            50,
            15
        )
        
        # Maksimal drawdown
        self._create_slider_field(
            risk_frame,
            "Maksimal drawdown (%):",
            "max_drawdown",
            0,
            30,
            10
        )
    
    def _create_notification_settings(self):
        """Oppretter varslingsinnstillinger."""
        notification_frame = ctk.CTkFrame(self)
        notification_frame.pack(fill="x", padx=20, pady=10)
        
        # Overskrift
        title_label = ctk.CTkLabel(
            notification_frame,
            text="Varslingsinnstillinger",
            font=self.fonts['heading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=10)
        
        # Varslingstyper
        self._create_checkbox_group(
            notification_frame,
            "Varslingstyper:",
            "notification_types",
            ["E-post", "Push-varsling", "SMS"]
        )
        
        # Varslingsfrekvens
        self._create_radio_group(
            notification_frame,
            "Varslingsfrekvens:",
            "notification_frequency",
            ["Realtid", "Daglig", "Ukentlig"]
        )
    
    def _create_save_button(self):
        """Oppretter lagreknapp."""
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Lagre innstillinger",
            command=self._save_settings
        )
        save_button.pack(side="right", padx=10)
    
    def _create_api_field(self, parent: ctk.CTkFrame, label: str, 
                         key: str, placeholder: str):
        """
        Oppretter et API-felt.
        
        Args:
            parent (ctk.CTkFrame): Foreldreramme
            label (str): Etikett
            key (str): Nøkkel for lagring
            placeholder (str): Plassholdertekst
        """
        field_frame = ctk.CTkFrame(parent)
        field_frame.pack(fill="x", padx=20, pady=5)
        
        # Etikett
        label = ctk.CTkLabel(
            field_frame,
            text=label,
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        label.pack(side="left", padx=5)
        
        # Inndatafelt
        entry = ctk.CTkEntry(
            field_frame,
            placeholder_text=placeholder,
            width=300
        )
        entry.pack(side="right", padx=5)
        
        # Lagre referanse
        setattr(self, key, entry)
    
    def _create_checkbox_group(self, parent: ctk.CTkFrame, label: str, 
                             key: str, options: List[str]):
        """
        Oppretter en gruppe av avkrysningsbokser.
        
        Args:
            parent (ctk.CTkFrame): Foreldreramme
            label (str): Gruppetittel
            key (str): Nøkkel for lagring
            options (List[str]): Alternativer
        """
        group_frame = ctk.CTkFrame(parent)
        group_frame.pack(fill="x", padx=20, pady=5)
        
        # Tittel
        title_label = ctk.CTkLabel(
            group_frame,
            text=label,
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=5)
        
        # Alternativer
        checkboxes = {}
        for option in options:
            var = ctk.BooleanVar(value=True)
            checkbox = ctk.CTkCheckBox(
                group_frame,
                text=option,
                variable=var
            )
            checkbox.pack(pady=2)
            checkboxes[option] = var
        
        # Lagre referanse
        setattr(self, key, checkboxes)
    
    def _create_radio_group(self, parent: ctk.CTkFrame, label: str, 
                          key: str, options: List[str]):
        """
        Oppretter en gruppe av radioknapper.
        
        Args:
            parent (ctk.CTkFrame): Foreldreramme
            label (str): Gruppetittel
            key (str): Nøkkel for lagring
            options (List[str]): Alternativer
        """
        group_frame = ctk.CTkFrame(parent)
        group_frame.pack(fill="x", padx=20, pady=5)
        
        # Tittel
        title_label = ctk.CTkLabel(
            group_frame,
            text=label,
            font=self.fonts['subheading'],
            text_color=self.colors['text']
        )
        title_label.pack(pady=5)
        
        # Alternativer
        var = ctk.StringVar(value=options[0])
        for option in options:
            radio = ctk.CTkRadioButton(
                group_frame,
                text=option,
                variable=var,
                value=option
            )
            radio.pack(pady=2)
        
        # Lagre referanse
        setattr(self, key, var)
    
    def _create_slider_field(self, parent: ctk.CTkFrame, label: str, 
                           key: str, min_: float, max_: float, default: float):
        """
        Oppretter et glidebryterfelt.
        
        Args:
            parent (ctk.CTkFrame): Foreldreramme
            label (str): Etikett
            key (str): Nøkkel for lagring
            min_ (float): Minimumsverdi
            max_ (float): Maksimumsverdi
            default (float): Standardverdi
        """
        field_frame = ctk.CTkFrame(parent)
        field_frame.pack(fill="x", padx=20, pady=5)
        
        # Etikett
        label = ctk.CTkLabel(
            field_frame,
            text=label,
            font=self.fonts['body'],
            text_color=self.colors['text']
        )
        label.pack(side="left", padx=5)
        
        # Glidebryter
        slider = ctk.CTkSlider(
            field_frame,
            from_=min_,
            to=max_,
            number_of_steps=int(max_ - min_)
        )
        slider.set(default)
        slider.pack(side="right", padx=5, fill="x", expand=True)
        
        # Verdi
        value_label = ctk.CTkLabel(
            field_frame,
            text=f"{default}%",
            font=self.fonts['metrics'],
            text_color=self.colors['text']
        )
        value_label.pack(side="right", padx=5)
        
        # Oppdater verdi
        def update_value(value):
            value_label.configure(text=f"{value:.1f}%")
        
        slider.configure(command=update_value)
        
        # Lagre referanse
        setattr(self, key, slider)
    
    def _load_settings(self):
        """Laster inn innstillinger fra fil."""
        try:
            if os.path.exists("config.yaml"):
                with open("config.yaml", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                
                # Last inn API-nøkler
                if "api_keys" in settings:
                    for key, value in settings["api_keys"].items():
                        if hasattr(self, key):
                            getattr(self, key).insert(0, value)
                
                # Last inn analyseinnstillinger
                if "analysis" in settings:
                    for key, value in settings["analysis"].items():
                        if hasattr(self, key):
                            checkboxes = getattr(self, key)
                            for option, checked in value.items():
                                if option in checkboxes:
                                    checkboxes[option].set(checked)
                
                # Last inn risikoinntillinger
                if "risk" in settings:
                    for key, value in settings["risk"].items():
                        if hasattr(self, key):
                            getattr(self, key).set(value)
                
                # Last inn varslingsinnstillinger
                if "notifications" in settings:
                    for key, value in settings["notifications"].items():
                        if hasattr(self, key):
                            if isinstance(value, dict):
                                checkboxes = getattr(self, key)
                                for option, checked in value.items():
                                    if option in checkboxes:
                                        checkboxes[option].set(checked)
                            else:
                                getattr(self, key).set(value)
        
        except Exception as e:
            print(f"Kunne ikke laste inn innstillinger: {e}")
    
    def _save_settings(self):
        """Lagrer innstillinger til fil."""
        try:
            settings = {
                "api_keys": {
                    "alpha_vantage_key": self.alpha_vantage_key.get(),
                    "fmp_key": self.fmp_key.get(),
                    "newsapi_key": self.newsapi_key.get()
                },
                "analysis": {
                    "technical_indicators": {
                        option: var.get()
                        for option, var in self.technical_indicators.items()
                    },
                    "fundamental_data": {
                        option: var.get()
                        for option, var in self.fundamental_data.items()
                    },
                    "sentiment_analysis": {
                        option: var.get()
                        for option, var in self.sentiment_analysis.items()
                    }
                },
                "risk": {
                    "max_position_size": self.max_position_size.get(),
                    "stop_loss": self.stop_loss.get(),
                    "take_profit": self.take_profit.get(),
                    "max_drawdown": self.max_drawdown.get()
                },
                "notifications": {
                    "notification_types": {
                        option: var.get()
                        for option, var in self.notification_types.items()
                    },
                    "notification_frequency": self.notification_frequency.get()
                }
            }
            
            with open("config.yaml", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
            
            print("Innstillinger lagret")
        
        except Exception as e:
            print(f"Kunne ikke lagre innstillinger: {e}") 