#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AutoTrader One GUI - Hovedfil
"""

import customtkinter as ctk
import sys
import os

# Legg til prosjektets rotmappe i Python-stien
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow

def main():
    """Starter AutoTrader One GUI-applikasjonen."""
    # Sett opp tema
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Opprett og start hovedvindu
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main() 