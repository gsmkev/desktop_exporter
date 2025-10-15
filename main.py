from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import PRIMARY, SUCCESS, INFO, DANGER
from ttkbootstrap.widgets import DateEntry
from pathlib import Path
from datetime import date
from PIL import Image, ImageTk

from desktop_exporter.api import AjaxAPI
from desktop_exporter.ui.login import LoginDialog
from desktop_exporter.ui.settings import open_settings as open_settings_dialog
from desktop_exporter.ui.dashboard import Dashboard


# run_export and LoginDialog moved to actions.py and ui/login.py


class App(tb.Window):
    def __init__(self) -> None:
        super().__init__(themename="flatly")
        self.title("Desktop Exporter")
        self.geometry("700x340")

        main = tb.Frame(self, padding=0)
        main.pack(fill=tk.BOTH, expand=True)
        self.main = main

        # Header bar (email shown when authenticated)
        self.header = tb.Frame(main, padding=(0, 0, 0, 12))
        self.header.grid(row=0, column=0, columnspan=2, sticky=tk.EW)
        self.header.columnconfigure(0, weight=1)
        self.var_user_email = tk.StringVar(value="")
        self.user_label = tb.Label(self.header, textvariable=self.var_user_email)

        # API config
        self.var_base = tk.StringVar(value=os.getenv("AJAX_API_BASE", "https://ajax-erp-2c56bc9ad64c.herokuapp.com"))
        self.var_token = tk.StringVar(value=os.getenv("AJAX_API_TOKEN", ""))
        self.var_desde = tk.StringVar(value=str(date.today()))
        self.var_hasta = tk.StringVar(value=str(date.today()))
        # Default to Windows E:\ if present
        default_target = "E:\\" if os.name == "nt" else str(Path.cwd())
        self.var_target = tk.StringVar(value=os.getenv("EXPORT_TARGET", default_target))

        row = 1

        # Central login if not authenticated
        self.center_login = tb.Frame(main)
        self.center_login.grid(row=row, column=0, columnspan=2, sticky="nsew")
        main.rowconfigure(row, weight=1)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        # Centered inline login with logo at left and form at right
        self.login_email_var = tk.StringVar()
        self.login_password_var = tk.StringVar()
        login_inner = tb.Frame(self.center_login, padding=0)
        login_inner.grid(row=0, column=0, sticky="nsew")
        self.center_login.rowconfigure(0, weight=1)
        self.center_login.columnconfigure(0, weight=1)

        # Use a two-column grid inside login_inner
        # Left column: blue canvas background for the rocket/logo side
        logo_col = tk.Canvas(login_inner, highlightthickness=0, bg="#0d6efd")
        form_col = tb.Frame(login_inner)
        logo_col.grid(row=0, column=0, sticky="nsew")
        form_col.grid(row=0, column=1, sticky="nsew", padx=10)
        # Left very small; right dominant
        login_inner.columnconfigure(0, weight=0, minsize=48)
        login_inner.columnconfigure(1, weight=1, minsize=560)
        login_inner.rowconfigure(0, weight=1)

        # Left: logo (scaled to reasonable height)
        try:
            logo_path = str(Path(__file__).resolve().parent / "logo.png")
            img = Image.open(logo_path)
            # scale to height ~100 keeping aspect ratio (larger logo)
            base_h = 100
            w, h = img.size
            scale = base_h / float(h)
            new_w = max(100, int(w * scale))
            img = img.resize((new_w, base_h), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            # Draw blue background full size and center the image
            def _place_logo(event=None):
                logo_col.delete("all")
                w = logo_col.winfo_width()
                h = logo_col.winfo_height()
                # fill blue background
                logo_col.create_rectangle(0, 0, w, h, fill="#0d6efd", outline="")
                # center image
                logo_col.create_image(w//2, h//2, image=self.logo_img)
            logo_col.bind("<Configure>", _place_logo)
            _place_logo()
        except Exception:
            # Ensure blue background visible even without image
            def _fill_blue(event=None):
                w = logo_col.winfo_width()
                h = logo_col.winfo_height()
                logo_col.delete("all")
                logo_col.create_rectangle(0, 0, w, h, fill="#0d6efd", outline="")
            logo_col.bind("<Configure>", _fill_blue)
            _fill_blue()

        # Right: login form (centered; labels above fields)
        form_inner = tb.Frame(form_col)
        form_inner.pack(expand=True, anchor='w', padx=24)
        tb.Label(form_inner, text="Email").grid(row=0, column=0, sticky=tk.W, pady=(0,4))
        tb.Entry(form_inner, textvariable=self.login_email_var, width=30).grid(row=1, column=0, sticky=tk.W, pady=(0,8))
        tb.Label(form_inner, text="Password").grid(row=2, column=0, sticky=tk.W, pady=(8,4))
        tb.Entry(form_inner, textvariable=self.login_password_var, show='*', width=30).grid(row=3, column=0, sticky=tk.W, pady=(0,8))
        tb.Button(form_inner, text="Entrar", bootstyle=PRIMARY, command=self.do_center_login).grid(row=4, column=0, sticky=tk.W, pady=(8,0))
        form_inner.columnconfigure(0, weight=0)
        row += 1
        # Form panel (hidden when not authenticated)
        self.form_frame = Dashboard(main, self.var_base, self.var_token, self.var_target, self.pick_dir)
        self.form_frame.grid(row=row, column=0, columnspan=2, sticky=tk.NSEW)

        main.columnconfigure(1, weight=1)

        # Secret shortcut: F1 opens settings dialog
        self.bind('<F1>', self.open_settings)

        # Initialize UI based on auth state (hide everything except centered login when not authenticated)
        self.update_auth_ui()

    def pick_dir(self) -> None:
        path = filedialog.askdirectory(initialdir=self.var_target.get() or "E:\\")
        if path:
            self.var_target.set(path)

    def open_login(self) -> None:
        dlg = LoginDialog(self, self.var_base, self.var_token, self.var_user_email)
        self.wait_window(dlg)
        if self.var_token.get():
            self.update_auth_ui()

    def do_center_login(self) -> None:
        try:
            api = AjaxAPI(base_url=self.var_base.get().strip())
            access = api.login(self.login_email_var.get().strip(), self.login_password_var.get().strip())
            self.var_token.set(access)
            self.var_user_email.set(self.login_email_var.get().strip())
            self.update_auth_ui()
        except Exception as exc:
            try:
                self.clipboard_clear()
                self.clipboard_append(str(exc))
                self.update()
            except Exception:
                pass
            messagebox.showerror("Login", str(exc))

    def update_auth_ui(self) -> None:
        authed = bool(self.var_token.get())
        if authed:
            # hide central login, show form, show email top-right
            try:
                self.center_login.grid_remove()
            except Exception:
                pass
            # move the whole form block up (row=1) so it aligns with the top
            try:
                self.form_frame.grid_configure(row=1, pady=(12, 0))
            except Exception:
                pass
            # ensure the spacer row is not consuming vertical space
            try:
                self.main.rowconfigure(1, weight=0)
            except Exception:
                pass
            # Show header and email
            try:
                self.header.grid()
            except Exception:
                pass
            self.user_label.grid(row=0, column=1, sticky=tk.E, padx=8, pady=(0, 0))
        else:
            # show central login, hide form and header email
            self.center_login.grid()
            try:
                self.form_frame.grid_remove()
            except Exception:
                pass
            try:
                self.user_label.grid_forget()
            except Exception:
                pass
            # Hide header entirely to show only the centered login button
            try:
                self.header.grid_remove()
            except Exception:
                pass

    def open_settings(self, event=None) -> None:
        open_settings_dialog(self, self.var_base)

    def on_export(self) -> None:
        try:
            base = self.var_base.get().strip()
            token = self.var_token.get().strip()
            from datetime import datetime
            desde_str = self.desde_picker.entry.get().strip()
            hasta_str = self.hasta_picker.entry.get().strip()
            # Convert UI format MM-DD-YYYY to API format YYYY-MM-DD
            desde_dt = datetime.strptime(desde_str, "%m-%d-%Y")
            hasta_dt = datetime.strptime(hasta_str, "%m-%d-%Y")
            desde = desde_dt.strftime("%Y-%m-%d")
            hasta = hasta_dt.strftime("%Y-%m-%d")
            target = self.var_target.get().strip()
            msg = run_export(base, token, desde, hasta, target)
            messagebox.showinfo("OK", msg)
        except Exception as exc:
            # Copy error to clipboard and show dialog
            try:
                self.clipboard_clear()
                self.clipboard_append(str(exc))
                self.update()
            except Exception:
                pass
            messagebox.showerror("Error", str(exc))


if __name__ == "__main__":
    app = App()
    app.mainloop()


