#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AutoTrader One GUI - Hovedvindu
"""

import logging
from typing import Dict, List, Optional, Type
import customtkinter as ctk
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gui.components.dashboard import DashboardFrame
from gui.components.recommendations import RecommendationsFrame
from gui.components.analysis import AnalysisFrame
from gui.components.settings import SettingsFrame

class MainWindow(ctk.CTk):
    """Hovedvindu for AutoTrader One GUI."""
    
    def __init__(self):
        """Initialiserer hovedvinduet."""
        super().__init__()
        
        # Sett opp vindu
        self.title("AutoTrader One")
        self.geometry("1200x800")
        
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
        
        # Sett opp innhold
        self._setup_content()
        
        # Sett opp gradient bakgrunn
        self._setup_gradient_background()
    
    def _setup_layout(self):
        """Setter opp hovedlayouten."""
        # Sett bakgrunnsfarge
        self.configure(fg_color=self.colors['background'])
        
        # Opprett hovedramme
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors['background']
        )
        self.main_frame.pack(fill="both", expand=True)
        
        # Opprett innholdsramme
        self.content_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['background']
        )
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    
    def _setup_content(self):
        """Setter opp hovedinnholdet i vinduet."""
        # Initialiser rammer
        self.frames = {}
        self.frame_classes = {
            "dashboard": DashboardFrame,
            "anbefalinger": RecommendationsFrame,
            "analyse": AnalysisFrame,
            "innstillinger": SettingsFrame
        }
        
        # Vis dashboard som standard
        self._show_frame("dashboard")
    
    def _show_frame(self, frame_name: str):
        """
        Viser valgt ramme.
        
        Args:
            frame_name (str): Navn på rammen som skal vises
        """
        # Skjul nåværende ramme
        if hasattr(self, 'current_frame') and self.current_frame:
            self.current_frame.pack_forget()
        
        # Opprett ny ramme hvis den ikke eksisterer
        if frame_name not in self.frames:
            frame_class = self.frame_classes[frame_name]
            self.frames[frame_name] = frame_class(self.content_frame)
        
        # Vis ny ramme
        self.current_frame = self.frames[frame_name]
        self.current_frame.pack(fill="both", expand=True)
    
    def _setup_gradient_background(self):
        """Setter opp gradient bakgrunn."""
        # Opprett en ramme som dekker hele vinduet
        self.gradient_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors['background'],
            corner_radius=0
        )
        self.gradient_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Opprett en annen ramme for gradient-effekten
        self.gradient_overlay = ctk.CTkFrame(
            self.gradient_frame,
            fg_color=self.colors['background'],
            corner_radius=0
        )
        self.gradient_overlay.place(relx=0, rely=0, relwidth=1, relheight=0.5)
    
    def _update_data(self):
        """Oppdaterer dataene i applikasjonen."""
        # TODO: Implementer dataoppdatering
        pass
    
    def run(self):
        """Starter applikasjonen."""
        self.mainloop() 