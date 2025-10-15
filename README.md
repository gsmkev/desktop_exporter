## Desktop Exporter

Aplicación de escritorio mínima para obtener facturas desde la API de Ajax y exportar archivos DBF compatibles con Visual FoxPro (`movimcab.dbf` y `movimite.dbf`).

### Requisitos

- Python 3.10+
- Windows para ejecución (interfaz Tkinter)

### Instalación

```bash
pip install -r requirements.txt
```

### Uso

```bash
python -m main
```

Configura la URL base y el token en la interfaz. Selecciona el rango de fechas y exporta.

### Empaquetado (opcional)

```bash
pyinstaller --noconfirm --onefile --windowed --name DesktopExporter main.py
```
