from __future__ import annotations

import os
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import INFO, SUCCESS
from ttkbootstrap.widgets import DateEntry

from desktop_exporter.actions import export_via_gui


class Dashboard(tb.Frame):
    def __init__(self, master, base_var, token_var, target_var, on_pick_dir):
        super().__init__(master)
        self.base_var = base_var
        self.token_var = token_var
        self.target_var = target_var
        self.on_pick_dir = on_pick_dir

        self.columnconfigure(0, weight=1)

        inner = tb.Frame(self)
        inner.grid(row=0, column=0, sticky="n")

        rowi = 0
        date_row = tb.Frame(inner)
        date_row.grid(row=rowi, column=0, sticky=tk.W)

        tb.Label(date_row, text="Desde").grid(row=0, column=0, sticky=tk.W, padx=(24,12), pady=(8,4))
        self.desde_picker = DateEntry(date_row, width=20, bootstyle=INFO, dateformat="%m-%d-%Y")
        self.desde_picker.grid(row=1, column=0, sticky=tk.W, padx=(24,12), pady=(0,8))
        self.desde_picker.set_date(__import__('datetime').date.today())
        self.desde_picker.entry.bind('<Key>', lambda e: 'break')
        self.desde_picker.entry.bind('<Control-Key>', lambda e: 'break')

        tb.Label(date_row, text="Hasta").grid(row=0, column=1, sticky=tk.W, padx=(12,24), pady=(8,4))
        self.hasta_picker = DateEntry(date_row, width=20, bootstyle=INFO, dateformat="%m-%d-%Y")
        self.hasta_picker.grid(row=1, column=1, sticky=tk.W, padx=(12,24), pady=(0,8))
        self.hasta_picker.set_date(__import__('datetime').date.today())
        self.hasta_picker.entry.bind('<Key>', lambda e: 'break')
        self.hasta_picker.entry.bind('<Control-Key>', lambda e: 'break')

        rowi += 2

        if os.name != "nt":
            rowi += 1
            tb.Label(inner, text="Destino").grid(row=rowi, column=0, sticky=tk.W, padx=24, pady=(8,4))
            rowi += 1
            dest_row = tb.Frame(inner)
            dest_row.grid(row=rowi, column=0, sticky=tk.EW, padx=24, pady=(0,8))
            dest_row.columnconfigure(0, weight=1)
            tb.Entry(dest_row, textvariable=self.target_var, width=48).grid(row=0, column=0, sticky=tk.EW)
            tb.Button(dest_row, text="Elegir...", bootstyle=INFO, command=self.on_pick_dir).grid(row=0, column=1, sticky=tk.W, padx=(8,0))

        rowi += 1
        btn_row = tb.Frame(inner)
        btn_row.grid(row=rowi, column=0, sticky="n", pady=(16, 0))
        tb.Button(btn_row, text="Exportar", bootstyle=SUCCESS, command=self._do_export).pack()

    def _do_export(self):
        base = self.base_var.get().strip()
        token = self.token_var.get().strip()
        desde = self.desde_picker.entry.get().strip()
        hasta = self.hasta_picker.entry.get().strip()
        target = self.target_var.get().strip()
        msg = export_via_gui(base, token, desde, hasta, target)
        from tkinter import messagebox
        messagebox.showinfo("OK", msg)



