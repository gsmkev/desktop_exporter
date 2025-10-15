from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import PRIMARY, DANGER

from desktop_exporter.api import AjaxAPI


class LoginDialog(tb.Toplevel):
    def __init__(self, parent: tk.Tk, base_url_var: tk.StringVar, token_out: tk.StringVar, user_email_out: tk.StringVar) -> None:
        super().__init__(parent)
        self.title("Iniciar sesión")
        self.resizable(False, False)
        self.grab_set()
        self.var_email = tk.StringVar()
        self.var_password = tk.StringVar()
        self.base_url_var = base_url_var
        self.token_out = token_out
        self.user_email_out = user_email_out

        frm = tb.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)
        tb.Label(frm, text="Email").grid(row=0, column=0, sticky=tk.W)
        tb.Entry(frm, textvariable=self.var_email, width=40).grid(row=0, column=1, padx=6)
        tb.Label(frm, text="Password").grid(row=1, column=0, sticky=tk.W)
        tb.Entry(frm, textvariable=self.var_password, width=40, show='*').grid(row=1, column=1, padx=6)
        btns = tb.Frame(frm)
        btns.grid(row=2, column=1, sticky=tk.E, pady=8)
        tb.Button(btns, text="Cancelar", bootstyle=DANGER, command=self.destroy).pack(side=tk.RIGHT, padx=4)
        tb.Button(btns, text="Entrar", bootstyle=PRIMARY, command=self.on_login).pack(side=tk.RIGHT)

    def on_login(self) -> None:
        try:
            api = AjaxAPI(base_url=self.base_url_var.get())
            access = api.login(self.var_email.get().strip(), self.var_password.get().strip())
            self.token_out.set(access)
            self.user_email_out.set(self.var_email.get().strip())
            self.destroy()
        except Exception as exc:
            try:
                self.clipboard_clear()
                self.clipboard_append(str(exc))
                self.update()
            except Exception:
                pass
            from tkinter import messagebox
            messagebox.showerror("Login", str(exc))



