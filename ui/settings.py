from __future__ import annotations

import ttkbootstrap as tb
from desktop_exporter.config import load_config, save_config


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
    def on_close():
        cfg = load_config()
        cfg["AJAX_API_BASE"] = base_var.get().strip()
        save_config(cfg)
        dlg.destroy()

    tb.Button(btns, text="Guardar", bootstyle="primary", command=on_close).pack(side="right")
    dlg.protocol("WM_DELETE_WINDOW", on_close)
    frm.columnconfigure(1, weight=1)



