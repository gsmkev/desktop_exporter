from __future__ import annotations

import ttkbootstrap as tb


def open_settings(parent, base_var):
    dlg = tb.Toplevel(parent)
    dlg.title("Ajustes")
    dlg.resizable(False, False)
    frm = tb.Frame(dlg, padding=16)
    frm.pack(fill="both", expand=True)
    tb.Label(frm, text="API Base URL").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=6)
    tb.Entry(frm, textvariable=base_var, width=50).grid(row=0, column=1, sticky="ew", padx=6, pady=6)
    btns = tb.Frame(frm, padding=(0, 8, 0, 0))
    btns.grid(row=1, column=1, sticky="e")
    tb.Button(btns, text="Cerrar", bootstyle="primary", command=dlg.destroy).pack(side="right")
    frm.columnconfigure(1, weight=1)



