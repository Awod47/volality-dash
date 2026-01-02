import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from ibapi.contract import Contract

import threading
import time
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")


class VolatalityDashBoard:
    def __init__(self, root):
        self.root = root
        self.root.title('Implied Volatality Dashboard')
        self.root.geometry('1400X1200')
        
        self.option_data = None
        self.volatality_data = None
        self.current_implied_vol = None

        # self.ib_app = IBApp()
        self.connected = False

        self.vol_annualization = 252
        self.setup_ui()

    def create_contract(self, ticker):
        contract = Contract()
        contract.ticker = ticker.upper()
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'

        return contract
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding = '10')
        main_frame.grid(row = 0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfig(0, weight=1)
        self.root.rowconfig(0, weight = 1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # connection frame
        conn_frame = ttk.LabelFrame(main_frame, text='Interactive Brokers Connection', padding='5')
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,10))
        
        ttk.Label(conn_frame, text='Host:').grid(row=0, column=0, padx=(0,5))
        self.host_var = tk.StringVar(value='127.0.0.1')
        ttk.Entry(conn_frame, textvariable = self.host_var, width = 15).grid(row=0,column=1,padx=(0,10))

        ttk.Label(conn_frame, text='Port:').grid(row=0, column=2, padx=(0,5))
        self.host_var = tk.StringVar(value='7497')
        ttk.Entry(conn_frame, textvariable = self.port_var, width = 15).grid(row=0,column=3,padx=(0,10))

        self.connect_btn = ttk.Button(conn_frame, text='Connect', command=self.connect_ib)
        self.connect_btn.grid(row=0, column=4, padx = (0,10))
    
        self.disconnect_btn = ttk.Button(conn_frame, text='Disconnect', command=self.disconnect_ib, state='disabled')
        self.disconnect_btn.grid(row=0, column=5, padx = (0,10))

        # data query frame
        data_frame = ttk.LabelFrame(main_frame, text='Data Query', padding='5')
        data_frame.grid(row = 1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady = (0,10))

        ttk.Label(data_frame, text='Symbol:').grid(row=0, column=0, padx=(0,5))
        self.symbol_var = tk.StringVar(value='SPY')
        ttk.Entry(data_frame, textvariable = self.port_var, width = 15).grid(row=0,column=1,padx=(0,10))

        ttk.Label(data_frame, text='Duration:').grid(row=0, column=2, padx=(0,5))
        self.duration_var = tk.StringVar(value='2 Y')
        ttk.Entry(data_frame, textvariable = self.duration_var, width = 15).grid(row=0,column=3,padx=(0,10))

        self.query_btn = ttk.Button(data_frame, text='Query IV data', command=self.query_data, state='disabled')
        self.query_btn.grid(row=0, column=4, padx = (0,10))
    
        self.analyze_btn = ttk.Button(data_frame, text='Analyze Implied Vol', command=self.analyze_volatility, state='disabled')
        self.analyze_btn.grid(row=0, column=5, padx = (0,10))

        # volatality frame
        vol_frame = ttk.LabelFrame(main_frame, text='Current Implied Volatility', padding='5')
        vol_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,10))

        ttk.Label(vol_frame, text='Current IV:').grid(row=0, column=0, padx=(0,5))
        self.current_vol_label = ttk.Label(vol_frame, text='N/A', font=('Arial', 12, 'bold'))
        self.current_vol_label.grid(row=0,column=1, padx=(0,20))

        ttk.Label(vol_frame, text='Computation:').grid(row=0, column=2, padx=(0,5))
        self.vol_computation_label = ttk.Label(vol_frame, text='No data', font=('Arial', 10))
        self.vol_computation_label.grid(row=0,column=3, padx=(0,10))

        ttk.Label(vol_frame, text='Volatility Range:').grid(row=0, column=4, padx=(0,5))
        self.vol_range_label = ttk.Label(vol_frame, text='N/A', font=('Arial', 10))
        self.vol_range_label.grid(row=0,column=5)

        # regime frame
        regime_frame = ttk.LabelFrame(main_frame, text='Volatility Regime Analysis', padding='5')
        regime_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,10))

        ttk.Label(regime_frame, text='Current Regime:').grid(row=0, column=0, padx=(0,5))
        self.regime_label = ttk.Label(vol_frame, text='N/A', font=('Arial', 12, 'bold'))
        self.regime_label.grid(row=0,column=5, padx=(0, 20))
    
        ttk.Label(regime_frame, text='Percentile:').grid(row=0, column=2, padx=(0,5))
        self.percentile_label = ttk.Label(vol_frame, text='N/A', font=('Arial', 10))
        self.percentile_label.grid(row=0,column=3, padx=(0, 20))

        ttk.Label(regime_frame, text='Mean Reversion Signal:').grid(row=0, column=4, padx=(0,5))
        self.reversion_label = ttk.Label(vol_frame, text='N/A', font=('Arial', 10))
        self.reversion_label.grid(row=0,column=5, padx=(0, 20))

        status_frame = ttk.LabelFrame(main_frame, text='Status', padding='5')
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0,10))

        self.status_text = scrolledtext.ScrolledText(status_frame, height = 6, width = 80)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)

        plot_frame = ttk.LabelFrame(main_frame, text='Implied Volatality Results', padding='5')
        plot_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        plot_frame.columnconfigure(9, weight=1)
        plot_frame.rowconfigure(0, weight=1)

        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(1,3,figsize = (18,6))
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().grid(row=0,column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        def log_message(self, message):
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.status_text.insert(tk.END, f'[[{timestamp}] {message}\n')
            self.status_text.see(tk.END)
            self.root.update_idletasks()

        def connect_ib(self):
            try:
                host = self.host_var.get()
                port = self.port_var.get()

                self.log_message(f'Connecting to IB at {host}:{port}')

                def connect_thread():
                    try:
                        self.ib_app.connect(host, port, 0)
                        self.ib_app.run()
