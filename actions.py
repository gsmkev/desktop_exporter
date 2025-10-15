from __future__ import annotations

from pathlib import Path
from datetime import datetime
from io import BytesIO
import zipfile

from desktop_exporter.api import AjaxAPI


def run_export(base_url: str, token: str, desde_iso: str, hasta_iso: str, target_dir: str) -> str:
    api = AjaxAPI(base_url=base_url, token=token)
    blob = api.download_dbf_zip(fecha_desde=desde_iso, fecha_hasta=hasta_iso)
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)

    # Extract ZIP contents directly into target directory
    with zipfile.ZipFile(BytesIO(blob)) as zf:
        zf.extractall(path=target)

    return "Archivos DBF descargados y extraídos correctamente."


def export_via_gui(base_url: str, token: str, desde_ui: str, hasta_ui: str, target_dir: str) -> str:
    # UI uses MM-DD-YYYY; convert to ISO
    desde_dt = datetime.strptime(desde_ui, "%m-%d-%Y")
    hasta_dt = datetime.strptime(hasta_ui, "%m-%d-%Y")
    desde_iso = desde_dt.strftime("%Y-%m-%d")
    hasta_iso = hasta_dt.strftime("%Y-%m-%d")
    return run_export(base_url, token, desde_iso, hasta_iso, target_dir)


